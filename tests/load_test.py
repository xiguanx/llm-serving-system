from locust import HttpUser, task, between
import json

class LLMUser(HttpUser):
    """Load testing user for LLM API"""
    
    wait_time = between(1, 3)  # requests
    
    @task(3)  # weight 3: non-streaming requests are more common
    def chat_completion(self):
        """test non-streaming chat completion"""
        payload = {
            "messages": [
                {"role": "user", "content": "Explain machine learning briefly"}
            ],
            "temperature": 0.7,
            "max_tokens": 100
        }
        
        with self.client.post(
            "/v1/chat/completions",
            json=payload,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Got status {response.status_code}")
    
    @task(1)  # weight 1: streaming requests are less common
    def chat_completion_stream(self):
        """test streaming chat completion"""
        payload = {
            "messages": [
                {"role": "user", "content": "Tell me about Docker"}
            ],
            "stream": True,
            "max_tokens": 50
        }
        
        with self.client.post(
            "/v1/chat/completions",
            json=payload,
            stream=True,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                # read streaming response
                for chunk in response.iter_lines():
                    if chunk:
                        pass  # deal with chunk
                response.success()
            else:
                response.failure(f"Got status {response.status_code}")
    
    @task(1)
    def health_check(self):
        """test health check endpoint"""
        with self.client.get("/health", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Got status {response.status_code}")

# run the following command in terminal:
# locust -f load_test.py --host http://localhost:8000
# then visit http://localhost:8089 set user count and spawn rate