package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"os"

	"github.com/joho/godotenv"
)

type Response struct {
	Data   []DataItem `json:"data"`
	Model  string     `json:"model"`
	Object string     `json:"object"`
	Usage  Usage      `json:"usage"`
}

type DataItem struct {
	Embedding []float32 `json:"embedding"`
	Index     int       `json:"index"`
	Object    string    `json:"object"`
}

type Usage struct {
	PromptTokens int `json:"prompt_tokens"`
	TotalTokens  int `json:"total_tokens"`
}

func getEmbedding(text string) ([]float32, error) {
	if err := godotenv.Load(); err != nil {
        panic("Error loading .env file")
    }

    openAiApiKey := os.Getenv("OPENAI_API_KEY")
    if openAiApiKey == "" {
        panic("OPENAI_API_KEY is not set in environment variables or .env file")
    }

	data := map[string]string{"input": text, "model": embeddingModel}
	jsonData, err := json.Marshal(data)
	if err != nil {
		return nil, err
	}

	// Make the HTTP request
	req, err := http.NewRequest("POST", openAIEndpoint, bytes.NewBuffer(jsonData))
	if err != nil {
		return nil, err
	}
	req.Header.Set("Authorization", "Bearer " + openAiApiKey)
	req.Header.Set("Content-Type", "application/json")

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	body, _ := ioutil.ReadAll(resp.Body)

	var response Response
	if err = json.Unmarshal(body, &response); err != nil {
		return nil, err
	}

	if len(response.Data) == 0 {
		return nil, fmt.Errorf("no data items in the response")
	}

	embedding := response.Data[0].Embedding
	return embedding, nil
}
