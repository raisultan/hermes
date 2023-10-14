package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"net/http"

	"github.com/gorilla/mux"
	"github.com/milvus-io/milvus-sdk-go/v2/client"
)

const (
	milvusAddr     = `localhost:19530`

	openAIEndpoint     = "https://api.openai.com/v1/embeddings"
	embeddingModel     = "text-embedding-ada-002"
	embeddingCtxLength = 8191
	embeddingEncoding  = "cl100k_base"
)

type App struct {
    MilvusClient *client.Client
}

func main() {
	// milvus()

	ctx := context.Background()

	milvus, err := client.NewClient(ctx, client.Config{Address: milvusAddr})
	if err != nil {
		log.Fatal("failed to connect to milvus, err: ", err.Error())
	}

	app := &App{
		MilvusClient: &milvus,
	}

	r := mux.NewRouter()

	r.HandleFunc("/hello", app.sayHello).Methods("GET")
	r.HandleFunc("/api/ads/insert", app.insertAd).Methods("POST")

	http.Handle("/", r)
	fmt.Println("Server started on :8080")
	http.ListenAndServe(":8080", nil)
}

func (a *App) sayHello(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode("Hello World!")
}

type Ad struct {
    ID          int64  `json:"ID"`
    ProjectName string `json:"projectName"`
    Text        string `json:"text"`
}

type InsertResponse struct {
    Status  string `json:"status"`
    Details string `json:"details"`
}

func (a *App) insertAd(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	var ad Ad

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
	insertAds(
		r.Context(),
		*a.MilvusClient,
		collectionName,
		ids,
		projectNames,
		embeddings,
	)

	response := InsertResponse{
		Status:  "success",
		Details: "Record inserted successfully",
	}

    json.NewEncoder(w).Encode(response)
}
