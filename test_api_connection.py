import requests
import json

def test_backend_connection():
    """Test the connection to the backend API."""
    base_url = "http://localhost:8000"
    
    # Test root endpoint
    try:
        response = requests.get(f"{base_url}/")
        print(f"Root endpoint response: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
        print("-" * 50)
    except Exception as e:
        print(f"Error connecting to root endpoint: {e}")
    
    # Test datasource plugins endpoint
    try:
        response = requests.get(f"{base_url}/datasources/plugins")
        print(f"Datasource plugins endpoint response: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
        print("-" * 50)
    except Exception as e:
        print(f"Error connecting to datasource plugins endpoint: {e}")
    
    # Test LLM plugins endpoint
    try:
        response = requests.get(f"{base_url}/llms/plugins")
        print(f"LLM plugins endpoint response: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
        print("-" * 50)
    except Exception as e:
        print(f"Error connecting to LLM plugins endpoint: {e}")
    
    # Test dataset generators endpoint
    try:
        response = requests.get(f"{base_url}/datasets/generators")
        print(f"Dataset generators endpoint response: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
        print("-" * 50)
    except Exception as e:
        print(f"Error connecting to dataset generators endpoint: {e}")

if __name__ == "__main__":
    test_backend_connection() 