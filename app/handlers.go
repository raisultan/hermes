package main

import (
	"encoding/json"
	"log"
	"net/http"

	"github.com/milvus-io/milvus-sdk-go/v2/entity"
)

func (a *App) sayHello(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode("Hello World!")
}

type InsertAdRequest struct {
	ID          int64  `json:"ID"`
	ProjectName string `json:"projectName"`
	Text        string `json:"text"`
}

type InsertAdResponse struct {
	Status  string `json:"status"`
	Details string `json:"details"`
}

func (a *App) insertAdHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	var ad InsertAdRequest

	err := json.NewDecoder(r.Body).Decode(&ad)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	embedding, err := getEmbedding(ad.Text)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	ids := []int64{ad.ID}
	projectNames := []string{ad.ProjectName}
	embeddings := [][]float32{embedding}
	insertAd(
		r.Context(),
		*a.MilvusClient,
		collectionName,
		ids,
		projectNames,
		embeddings,
	)

	response := InsertAdResponse{
		Status:  "success",
		Details: "Record inserted successfully",
	}

	json.NewEncoder(w).Encode(response)
}

type SearchAdRequest struct {
	ProjectName string `json:"projectName"`
	Text        string `json:"text"`
}

type SearchAdResult struct {
	ID          int64   `json:"id"`
	ProjectName string  `json:"projectName"`
	Distance    float32 `json:"distance"`
}

func (a *App) searchSimilarAdsHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	var ad SearchAdRequest

	err := json.NewDecoder(r.Body).Decode(&ad)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	embedding, err := getEmbedding(ad.Text)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	ctx := r.Context()
	loadAdsCollection(ctx, *a.MilvusClient, collectionName)

	sRet := searchSimilarAds(
		r.Context(),
		*a.MilvusClient,
		collectionName,
		ad.ProjectName,
		embedding,
	)

	searchResults := make([]SearchAdResult, 0, sRet.ResultCount)
	var idValues *entity.ColumnInt64
	var projectNameValues *entity.ColumnVarChar

	for _, field := range sRet.Fields {
		if field.Name() == projectNameCol {
			c, ok := field.(*entity.ColumnVarChar)
			if ok {
				projectNameValues = c
			}
		}
		if field.Name() == idCol {
			c, ok := field.(*entity.ColumnInt64)
			if ok {
				idValues = c
			}
		}
	}
	for i := 0; i < sRet.ResultCount; i++ {
		projectNameValue, err := projectNameValues.ValueByIdx(i)
		if err != nil {
			log.Fatal(err)
		}

		idValue, err := idValues.ValueByIdx(i)
		if err != nil {
			log.Fatal(err)
		}

		searchResults = append(searchResults, SearchAdResult{
			ID: idValue,
			ProjectName: projectNameValue,
			Distance: sRet.Scores[i],
		})
	}

	json.NewEncoder(w).Encode(searchResults)
}
