package main

import (
	"context"
	"fmt"
	"log"
	"net/http"
	"os"

	"github.com/gorilla/mux"
	"github.com/joho/godotenv"
	"github.com/milvus-io/milvus-sdk-go/v2/client"
)

type Config struct {
	MilvusAddr   string
	OpenAIApiKey string
}

func NewConfig() (*Config, error) {
	if err := godotenv.Load(); err != nil {
		panic("Error loading .env file")
	}

	openAiApiKey := os.Getenv("OPENAI_API_KEY")
	if openAiApiKey == "" {
		panic("OPENAI_API_KEY is not set in environment variables or .env file")
	}

	cfg := &Config{
		MilvusAddr:   `localhost:19530`,
		OpenAIApiKey: openAiApiKey,
	}

	return cfg, nil
}

type App struct {
	MilvusClient *client.Client
	Config       *Config
}

func main() {
	ctx := context.Background()
	config, _ := NewConfig()

	milvusClient, err := client.NewClient(ctx, client.Config{Address: config.MilvusAddr})
	if err != nil {
		log.Fatal("failed to connect to milvus, err: ", err)
	}
	defer milvusClient.Close()

	app := &App{
		MilvusClient: &milvusClient,
		Config:       config,
	}

	r := mux.NewRouter()

	r.HandleFunc("/hello", app.sayHello).Methods("GET")
	r.HandleFunc("/api/insert", app.insertHandler).Methods("POST")
	r.HandleFunc("/api/search", app.searchHandler).Methods("POST")
	r.HandleFunc("/api/delete", app.deleteHandler).Methods("DELETE")

	text, err := ExtractTextFromPDFVer3("./aem.pdf")
	if err != nil {
		panic(err)
	}
	fmt.Println(text)

	http.Handle("/", r)
	fmt.Println("Server started on :8080")
	http.ListenAndServe(":8080", nil)
}
