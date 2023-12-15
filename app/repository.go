package main

import (
	"context"
	"log"
	"time"

	"github.com/milvus-io/milvus-sdk-go/v2/client"
	"github.com/milvus-io/milvus-sdk-go/v2/entity"
)

const (
	nDimensions       = 1536
	adsCollectionName = "ads"

	idColumnName        = "ID"
	projectColumnName   = "projectName"
	embeddingColumnName = "embeddings" // no s in the end

	nClusters      = 128
	nProbes        = 32
	nSearchResults = 3
)

// unused yet but is helpful when initializing the collection
func createAdsCollection(ctx context.Context, c client.Client) {
	schema := entity.NewSchema().
		WithName(adsCollectionName).WithDescription("Ads Collection").
		WithField(
			entity.NewField().
				WithName(idColumnName).
				WithDataType(entity.FieldTypeInt64).
				WithIsPrimaryKey(true).WithIsAutoID(false),
		).
		WithField(
			entity.NewField().
				WithName(projectColumnName).
				WithDataType(entity.FieldTypeVarChar).
				WithMaxLength(256),
		).
		WithField(
			entity.NewField().
				WithName(embeddingColumnName).
				WithDataType(entity.FieldTypeFloatVector).
				WithDim(nDimensions),
		)

	err := c.CreateCollection(ctx, schema, entity.DefaultShardNumber)
	if err != nil {
		log.Fatalf("create collection failed, err: %v", err)
	}
}

func insertAd(
	ctx context.Context,
	c client.Client,
	ids []int64,
	projectNames []string,
	embeddings [][]float32,
) {
	idColData := entity.NewColumnInt64(idColumnName, ids)
	projectNameColData := entity.NewColumnVarChar(projectColumnName, projectNames)
	embeddingColData := entity.NewColumnFloatVector(embeddingColumnName, nDimensions, embeddings)

	_, err := c.Insert(ctx, adsCollectionName, "", idColData, projectNameColData, embeddingColData)
	if err != nil {
		log.Fatalf("failed to insert random data into `hello_milvus, err: %v", err)
	}

	if err := c.Flush(ctx, adsCollectionName, false); err != nil {
		log.Fatalf("failed to flush data, err: %v", err)
	}
}

// unused yet, but is helpful when initializing the collection
func buildAdsIndex(ctx context.Context, c client.Client) {
	idx, err := entity.NewIndexIvfFlat(entity.L2, nClusters)

	if err != nil {
		log.Fatalf("failed to create ivf flat index, err: %v", err)
	}

	if err := c.CreateIndex(ctx, adsCollectionName, embeddingColumnName, idx, false); err != nil {
		log.Fatalf("failed to create index, err: %v", err)
	}
}

func loadAdsCollection(ctx context.Context, c client.Client) {
	err := c.LoadCollection(ctx, adsCollectionName, false)

	if err != nil {
		log.Fatalf("failed to load collection, err: %v", err)
	}
}

func searchSimilarAds(
	ctx context.Context,
	c client.Client,
	projectName string,
	embedding []float32,
) client.SearchResult {
	vec2search := []entity.Vector{entity.FloatVector(embedding)}
	begin := time.Now()
	sp, _ := entity.NewIndexIvfFlatSearchParam(nProbes)
	sRet, err := c.Search(
		ctx,
		adsCollectionName,
		nil,
		"projectName == "+"'"+projectName+"'",
		[]string{idColumnName, projectColumnName},
		vec2search,
		embeddingColumnName,
		entity.L2,
		nSearchResults,
		sp,
	)
	end := time.Now()
	if err != nil {
		log.Fatalf("failed to search collection, err: %v", err)
	}

	log.Printf("\tsearch latency: %dms\n", end.Sub(begin)/time.Millisecond)
	return sRet[0]
}

// unused
func deleteAds(ctx context.Context, c client.Client, ids []int64) {
	pks := entity.NewColumnInt64(idColumnName, ids)
	sRet, err := c.QueryByPks(ctx, adsCollectionName, nil, pks, []string{projectColumnName})
	if err != nil {
		log.Fatalf("failed to query result, err: %v", err)
	}

	log.Println("results:")
	idlist := make([]int64, 0)
	randList := make([]string, 0)

	for _, col := range sRet {
		if col.Name() == idColumnName {
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

	if err := c.DeleteByPks(ctx, adsCollectionName, "", pks); err != nil {
		log.Fatalf("failed to delete by pks, err: %v", err)
	}
	_, err = c.QueryByPks(
		ctx,
		adsCollectionName,
		nil,
		pks,
		[]string{projectColumnName},
		client.WithSearchQueryConsistencyLevel(entity.ClStrong),
	)
	if err != nil {
		log.Printf("failed to query result, err: %v", err)
	}
}

// unused
func dropAdsCollection(ctx context.Context, c client.Client) {
	if err := c.DropCollection(ctx, adsCollectionName); err != nil {
		log.Fatalf("failed to drop collection, err: %v", err)
	}
}

func deleteAd(ctx context.Context, c client.Client, ids []int64) {
	pks := entity.NewColumnInt64(idColumnName, ids)

	if err := c.DeleteByPks(ctx, adsCollectionName, "", pks); err != nil {
		log.Fatalf("failed to delete by pks, err: %v", err)
	}
}
