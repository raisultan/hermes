package main

import (
	"context"
	"fmt"
	"log"
	"net/http"

	"github.com/gorilla/mux"
	"github.com/milvus-io/milvus-sdk-go/v2/client"
)

const (
	milvusAddr     = `localhost:19530`
	dim            = 1536
	collectionName = "ads"

	idCol, projectNameCol, embeddingCol = "ID", "projectName", "embeddings"

	nlist  = 128
	nprobe = 32
	topK   = 3

	openAIEndpoint     = "https://api.openai.com/v1/embeddings"
	embeddingModel     = "text-embedding-ada-002"
	embeddingCtxLength = 8191
	embeddingEncoding  = "cl100k_base"
)

type App struct {
    MilvusClient *client.Client
}

func main() {
	ctx := context.Background()

	milvus, err := client.NewClient(ctx, client.Config{Address: milvusAddr})
	if err != nil {
		log.Fatal("failed to connect to milvus, err: ", err.Error())
	}
	defer milvus.Close()

	app := &App{
		MilvusClient: &milvus,
	}

	r := mux.NewRouter()

	r.HandleFunc("/hello", app.sayHello).Methods("GET")
	r.HandleFunc("/api/ads/insert", app.insertAdHandler).Methods("POST")
	r.HandleFunc("/api/ads/search", app.searchSimilarAdsHandler).Methods("POST")

	http.Handle("/", r)
	fmt.Println("Server started on :8080")
	http.ListenAndServe(":8080", nil)
}
