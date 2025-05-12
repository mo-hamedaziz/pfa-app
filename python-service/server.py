import grpc
from concurrent import futures
import sys
sys.path.append('./generated')
import psycopg2
import logging
from generated import model_pb2
from generated import model_pb2_grpc
from sklearn.linear_model import LinearRegression
import numpy as np
import os


print("here")

DB_PARAMS = {
    "dbname": os.getenv("DB_NAME", "ml_tenants"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "postgres"),
    "host": os.getenv("DB_HOST", "postgres"),
    "port": 5432,
}

class ModelTrainer(model_pb2_grpc.GoServiceServicer):
    def SendTrainingData(self, request, context):
        tenant_id = request.tenant_id
        schema_name = f"tenant_{tenant_id}"
        print("stargin to create schema")
        # Train model
        X = np.array(request.values).reshape(1, -1)
        y = np.array([1])  # Dummy label for now
        model = LinearRegression().fit(X, y)
        print("Trained model with data:", request.feature_names, request.values)

        # Connect to DB
        try:
            conn = psycopg2.connect(**DB_PARAMS)
            conn.autocommit = True
            cursor = conn.cursor()

            print("Connected to database")

            # Create schema if not exists
            cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {schema_name}")
            print("created schema")
            # Create table if not exists
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {schema_name}.result (
                    id SERIAL PRIMARY KEY,
                    value FLOAT
                )
            """)


            # Insert y value
            cursor.execute(f"INSERT INTO {schema_name}.result (value) VALUES (%s)", (float(y[0]),))
            print("inserted into schema")
            cursor.close()
            conn.close()

        except Exception as e:
            print("Database error:", e)
            return model_pb2.TrainingResponse(status="Error storing result")

        return model_pb2.TrainingResponse(status="Model trained and result saved")

def serve():
    print("starting grpc server")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=5))
    print("srater grpc server")
    model_pb2_grpc.add_GoServiceServicer_to_server(ModelTrainer(), server)
    print("doing other stuff")
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()
    print("finished dowing oter stuff")

if __name__ == '__main__':
    print("Accepting connections")
    serve()