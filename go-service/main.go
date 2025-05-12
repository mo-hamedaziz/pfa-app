package main

import (
    "context"
    "encoding/json"
    "log"
    "net/http"
    "time"

    "google.golang.org/grpc"
    pb "go-app/generated/modelpb"
    "fmt"
)

type RequestPayload struct {
    TenantID     string    `json:"tenant_id"` // <-- add this
    FeatureNames []string  `json:"feature_names"`
    Values       []float32 `json:"values"`
}

var grpcClient pb.GoServiceClient

func main() {
    // Set up gRPC connection
    conn, err := grpc.Dial("python-grpc:50051", grpc.WithInsecure())
    if err != nil {
        log.Fatalf("Could not connect to gRPC server: %v", err)
    }
    defer conn.Close()

    grpcClient = pb.NewGoServiceClient(conn)

    // Set up HTTP server
    http.HandleFunc("/train", handleTrainingData)
    log.Println("HTTP server started on :8080")
    log.Fatal(http.ListenAndServe(":8080", nil))
}

func handleTrainingData(w http.ResponseWriter, r *http.Request) {
    if r.Method != http.MethodPost {
        http.Error(w, "Only POST method is allowed", http.StatusMethodNotAllowed)
        return
    }

    var reqData RequestPayload
    decoder := json.NewDecoder(r.Body)
    if err := decoder.Decode(&reqData); err != nil {
        http.Error(w, "Invalid request body", http.StatusBadRequest)
        return
    }

    grpcReq := &pb.TrainingRequest{
        TenantId:     reqData.TenantID, // <-- add this
        FeatureNames: reqData.FeatureNames,
        Values:       reqData.Values,
    }

    fmt.Println(reqData.TenantID)
    fmt.Println(reqData.FeatureNames)
    fmt.Println(reqData.Values)

    

    ctx, cancel := context.WithTimeout(context.Background(), time.Second*3)
    defer cancel()

    grpcRes, err := grpcClient.SendTrainingData(ctx, grpcReq)
    if err != nil {
        http.Error(w, "Failed to call gRPC service: "+err.Error(), http.StatusInternalServerError)
        return
    }

    json.NewEncoder(w).Encode(map[string]string{
        "status": grpcRes.Status,
    })
}
