import grpc
from concurrent import futures
from generated import model_pb2
from generated import model_pb2_grpc
from sklearn.linear_model import LinearRegression
import numpy as np
import sys
sys.path.append('./generated')


class ModelTrainer(model_pb2_grpc.GoServiceServicer):
    def SendTrainingData(self, request, context):
        X = np.array(request.values).reshape(1, -1)
        y = np.array([1]) 
        model = LinearRegression().fit(X, y)
        print("Trained model with data:", request.feature_names, request.values)

        #Save hetha fil bd,  
        return model_pb2.TrainingResponse(status="Model trained")

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=5))
    model_pb2_grpc.add_GoServiceServicer_to_server(ModelTrainer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
