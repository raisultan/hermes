package main

import (
	"context"
	"log"
	"time"

	"github.com/milvus-io/milvus-sdk-go/v2/client"
	"github.com/milvus-io/milvus-sdk-go/v2/entity"
)

func createAdsCollection(ctx context.Context, c client.Client, collectionName string) {
	schema := entity.NewSchema().
		WithName(collectionName).WithDescription("Ads Collection").
		WithField(entity.NewField().WithName(idCol).WithDataType(entity.FieldTypeInt64).WithIsPrimaryKey(true).WithIsAutoID(false)).
		WithField(entity.NewField().WithName(projectNameCol).WithDataType(entity.FieldTypeVarChar).WithMaxLength(256)).
		WithField(entity.NewField().WithName(embeddingCol).WithDataType(entity.FieldTypeFloatVector).WithDim(dim))

	if err := c.CreateCollection(ctx, schema, entity.DefaultShardNumber); err != nil { // use default shard number
		log.Fatalf("create collection failed, err: %v", err)
	}
}

func insertAd(
	ctx context.Context,
	c client.Client,
	collectionName string,
	ids []int64,
	projectNames []string,
	embeddings [][]float32,
) {
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
	idx, err := entity.NewIndexIvfFlat(entity.L2, nlist)

	if err != nil {
		log.Fatalf("failed to create ivf flat index, err: %v", err)
	}

	if err := c.CreateIndex(ctx, collectionName, embeddingCol, idx, false); err != nil {
		log.Fatalf("failed to create index, err: %v", err)
	}
}

func loadAdsCollection(ctx context.Context, c client.Client, collectionName string) {
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
	if err := c.DropCollection(ctx, collectionName); err != nil {
		log.Fatalf("failed to drop collection, err: %v", err)
	}
}
