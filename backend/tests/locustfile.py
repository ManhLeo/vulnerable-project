from locust import HttpUser, task, between

class APIUser(HttpUser):
    wait_time = between(1, 2)
    
    @task(3)
    def scan_code(self):
        payload = {
            "source_code": "def example():\n    eval(request.GET['cmd'])",
            "language": "python"
        }
        self.client.post("/api/v1/scan/code", json=payload)
    
    @task(1)
    def health_check(self):
        self.client.get("/api/v1/health")
