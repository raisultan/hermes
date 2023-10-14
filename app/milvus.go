package main

import (
	"context"
	"fmt"
	"log"
	"math/rand"
	"time"

	"github.com/milvus-io/milvus-sdk-go/v2/client"
	"github.com/milvus-io/milvus-sdk-go/v2/entity"
)

const (
	// milvusAddr     = `localhost:19530`
	dim            = 1536
	collectionName = "ads"

	idCol, projectNameCol, embeddingCol = "ID", "projectName", "embeddings"

	nlist  = 128
	nprobe = 32

	msgFmt                              = "==== %s ====\n"
	topK                                = 3  // number of the most similar result to return
	nEntities                           = 3000
)

func createAdsCollection(ctx context.Context, c client.Client, collectionName string) {
	log.Printf(msgFmt, fmt.Sprintf("create collection, `%s`", collectionName))
	schema := entity.NewSchema().
		WithName(collectionName).WithDescription("Ads Collection").
		WithField(entity.NewField().WithName(idCol).WithDataType(entity.FieldTypeInt64).WithIsPrimaryKey(true).WithIsAutoID(false)).
		WithField(entity.NewField().WithName(projectNameCol).WithDataType(entity.FieldTypeVarChar).WithMaxLength(256)).
		WithField(entity.NewField().WithName(embeddingCol).WithDataType(entity.FieldTypeFloatVector).WithDim(dim))

	if err := c.CreateCollection(ctx, schema, entity.DefaultShardNumber); err != nil { // use default shard number
		log.Fatalf("create collection failed, err: %v", err)
	}
}

func insertAds(ctx context.Context, c client.Client, collectionName string, ids []int64, projectNames []string, embeddings [][]float32) {
	idColData := entity.NewColumnInt64(idCol, ids)
	projectNameColData := entity.NewColumnVarChar(projectNameCol, projectNames)
	embeddingColData := entity.NewColumnFloatVector(embeddingCol, dim, embeddings)

	if _, err := c.Insert(ctx, collectionName, "", idColData, projectNameColData, embeddingColData); err != nil {
		log.Fatalf("failed to insert random data into `hello_milvus, err: %v", err)
	}

	if err := c.Flush(ctx, collectionName, false); err != nil {
		log.Fatalf("failed to flush data, err: %v", err)
	}
}

func buildAdsIndex(ctx context.Context, c client.Client, collectionName string) {
	log.Printf(msgFmt, "start creating index IVF_FLAT")
	idx, err := entity.NewIndexIvfFlat(entity.L2, nlist)

	if err != nil {
		log.Fatalf("failed to create ivf flat index, err: %v", err)
	}

	if err := c.CreateIndex(ctx, collectionName, embeddingCol, idx, false); err != nil {
		log.Fatalf("failed to create index, err: %v", err)
	}
}

func loadAdsCollection(ctx context.Context, c client.Client, collectionName string) {
	log.Printf(msgFmt, "start loading collection")
	err := c.LoadCollection(ctx, collectionName, false)

	if err != nil {
		log.Fatalf("failed to load collection, err: %v", err)
	}
}

func searchSimilarAds(
	ctx context.Context,
	c client.Client,
	collectionName string,
	projectName string,
	embedding []float32,
) client.SearchResult {
	vec2search := []entity.Vector{entity.FloatVector(embedding)}
	begin := time.Now()
	sp, _ := entity.NewIndexIvfFlatSearchParam(nprobe)
	sRet, err := c.Search(
		ctx,
		collectionName,
		nil,
		"projectName == " + "'" + projectName + "'",
		[]string{idCol, projectNameCol},
		vec2search,
		embeddingCol,
		entity.L2,
		topK,
		sp,
	)
	end := time.Now()
	if err != nil {
		log.Fatalf("failed to search collection, err: %v", err)
	}

	log.Printf("\tsearch latency: %dms\n", end.Sub(begin)/time.Millisecond)
	return sRet[0]
}

func deleteAds(ctx context.Context, c client.Client, collectionName string, ids []int64) {
	log.Printf(msgFmt, "start deleting with expr ``")
	pks := entity.NewColumnInt64(idCol, ids)
	sRet, err := c.QueryByPks(ctx, collectionName, nil, pks, []string{projectNameCol})
	if err != nil {
		log.Fatalf("failed to query result, err: %v", err)
	}

	log.Println("results:")
	idlist := make([]int64, 0)
	randList := make([]string, 0)

	for _, col := range sRet {
		if col.Name() == idCol {
			idColumn := col.(*entity.ColumnInt64)
			for i := 0; i < col.Len(); i++ {
				val, err := idColumn.ValueByIdx(i)
				if err != nil {
					log.Fatal(err)
				}
				idlist = append(idlist, val)
			}
		} else {
			randColumn := col.(*entity.ColumnVarChar)
			for i := 0; i < col.Len(); i++ {
				val, err := randColumn.ValueByIdx(i)
				if err != nil {
					log.Fatal(err)
				}
				randList = append(randList, val)
			}
		}
	}
	log.Printf("\tids: %#v, randoms: %#v\n", idlist, randList)

	if err := c.DeleteByPks(ctx, collectionName, "", pks); err != nil {
		log.Fatalf("failed to delete by pks, err: %v", err)
	}
	_, err = c.QueryByPks(
		ctx,
		collectionName,
		nil,
		pks,
		[]string{projectNameCol},
		client.WithSearchQueryConsistencyLevel(entity.ClStrong),
	)
	if err != nil {
		log.Printf("failed to query result, err: %v", err)
	}
}

func dropAdsCollection(ctx context.Context, c client.Client, collectionName string) {
	log.Printf(msgFmt, "drop collection `hello_milvus`")
	if err := c.DropCollection(ctx, collectionName); err != nil {
		log.Fatalf("failed to drop collection, err: %v", err)
	}
}

func milvus() {
	ctx := context.Background()

	log.Printf(msgFmt, "start connecting to Milvus")
	c, err := client.NewClient(ctx, client.Config{Address: milvusAddr})
	if err != nil {
		log.Fatal("failed to connect to milvus, err: ", err.Error())
	}
	defer c.Close()  // closes the client right after exit from the current function

	// delete collection if exists
	has, err := c.HasCollection(ctx, collectionName)
	if err != nil {
		log.Fatalf("failed to check collection exists, err: %v", err)
	}
	if has {
		c.DropCollection(ctx, collectionName)
	}

	// create collection
	createAdsCollection(ctx, c, collectionName)

	// insert data
	log.Printf(msgFmt, "start inserting random entities")
	idList, randomList := make([]int64, 0, nEntities), make([]string, 0, nEntities)
	embeddingList := make([][]float32, 0, nEntities)

	rand.Seed(time.Now().UnixNano())

	// generate data
	for i := 0; i < nEntities; i++ {
		idList = append(idList, int64(i))
	}
	for i := 0; i < nEntities; i++ {
		randomList = append(randomList, "hello")
	}
	for i := 0; i < nEntities; i++ {
		vec := make([]float32, 0, dim)
		for j := 0; j < dim; j++ {
			vec = append(vec, rand.Float32())
		}
		embeddingList = append(embeddingList, vec)
	}
	insertAds(ctx, c, collectionName, idList, randomList, embeddingList)

	// build index
	buildAdsIndex(ctx, c, collectionName)

	loadAdsCollection(ctx, c, collectionName)

	log.Printf(msgFmt, "start searcching based on vector similarity")
	sRet := searchSimilarAds(ctx, c, collectionName, "project", embeddingList[len(embeddingList)-1])
	log.Println("results:")
	printResult(&sRet)

	// delete data
	deleteAds(ctx, c, collectionName, []int64{0, 1})

	// drop collection
	// dropAdsCollection(ctx, c, collectionName)
}

func printResult(sRet *client.SearchResult) {
	randoms := make([]string, 0, sRet.ResultCount)
	scores := make([]float32, 0, sRet.ResultCount)

	var projectCol *entity.ColumnVarChar
	for _, field := range sRet.Fields {
		if field.Name() == projectNameCol {
			c, ok := field.(*entity.ColumnVarChar)
			if ok {
				projectCol = c
			}
		}
	}
	for i := 0; i < sRet.ResultCount; i++ {
		val, err := projectCol.ValueByIdx(i)
		if err != nil {
			log.Fatal(err)
		}
		randoms = append(randoms, val)
		scores = append(scores, sRet.Scores[i])
	}
	log.Printf("\trandoms: %v, scores: %v\n", randoms, scores)
}
