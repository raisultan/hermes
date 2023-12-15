package main

import (
	"io/ioutil"
	"os"
	"path/filepath"
	"sort"
	"strings"

	"github.com/pdfcpu/pdfcpu/pkg/api"
	"github.com/pdfcpu/pdfcpu/pkg/pdfcpu/model"
)

// ExtractTextFromPDF extracts text content from a PDF file.
func ExtractTextFromPDF(pdfPath string) (string, error) {
    // Configure pdfcpu for text extraction
    config := model.NewDefaultConfiguration()
    config.Cmd = model.EXTRACTCONTENT

    // Extract text to a temporary file
    // tempFile, err := os.CreateTemp("./", "pdfcpu_temp_*.txt")
    // if err != nil {
    //     return "", err
    // }
    // defer tempFile.Close()

    if err := api.ExtractContentFile("oem.pdf", "out", nil, config); err != nil {
        return "", err
    }

    // Read the extracted text from the temporary file
    // textBytes, err := os.ReadFile(tempFile.Name())
    // if err != nil {
    //     return "", err
    // }

    // return string(textBytes), nil
    return "hello", nil
}

func ExtractTextFromPDFVer2(pdfPath string) error {
    inDir := filepath.Join("./")
    inFile := filepath.Join(inDir, "oem.pdf")
    outDir := filepath.Join(inDir, "out")
    err := api.ExtractContentFile(inFile, outDir, nil, nil)
    return err
}

func ExtractTextFromPDFVer3(pdfPath string) (string, error) {
    // Use the provided pdfPath as the input file path
    inFile := pdfPath

    // Create a temporary output directory
    outDir := filepath.Join("./out")
    if err := os.MkdirAll(outDir, os.ModePerm); err != nil {
        return "", err
    }

    // Extract content to the output directory
    err := api.ExtractContentFile(inFile, outDir, nil, nil)
    if err != nil {
        return "", err
    }

    // List files in the output directory
    files, err := ioutil.ReadDir(outDir)
    if err != nil {
        return "", err
    }

    // Filter and sort files based on the naming pattern
    var pageFiles []string
    for _, file := range files {
        if strings.HasPrefix(file.Name(), "aem_Content_page_") && strings.HasSuffix(file.Name(), ".txt") {
            pageFiles = append(pageFiles, filepath.Join(outDir, file.Name()))
        }
    }
    sort.Strings(pageFiles) // Sort files to maintain page order

    // Read and concatenate the contents of each file
    var extractedText strings.Builder
    for _, pageFile := range pageFiles {
        content, err := ioutil.ReadFile(pageFile)
        if err != nil {
            return "", err
        }
        extractedText.Write(content)
    }

    // Return the concatenated content
    return extractedText.String(), nil
}