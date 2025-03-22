import asyncio
import json
import requests
from pprint import pprint
from uuid import UUID

# Base URL for API
BASE_URL = "http://localhost:8000/api/v1"

# Sample LLM configuration
sample_llm_config = {
    "name": "Custom LLM Model",
    "config": {
        "type": "custom",
        "api_key": "abc",
        "model_name": "custom-model",
        "parameters": {
            "temperature": 0.7,
            "max_tokens": 2000
        }
    },
    "is_default": True
}

# Sample data source configuration
sample_datasource_config = {
    "name": "Sample PDF Source",
    "config": {
        "type": "pdf",
        "connection_string": "",
        "source_path": "./sample_pdfs",
        "parameters": {
            "max_files": "10"
        }
    },
    "is_default": True
}

def test_llm_config_api():
    """Test LLM configuration API endpoints"""
    print("\n=== Testing LLM Configuration API ===")
    
    # Create a new LLM configuration
    print("\nCreating LLM configuration...")
    response = requests.post(f"{BASE_URL}/config/llm", json=sample_llm_config)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    config_data = response.json()
    config_id = config_data['id']
    print(f"Created LLM config with ID: {config_id}")
    pprint(config_data)
    
    # Get all LLM configurations
    print("\nGetting all LLM configurations...")
    response = requests.get(f"{BASE_URL}/config/llm")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    configs = response.json()
    print(f"Found {len(configs)} LLM configurations")
    
    # Get default LLM configuration
    print("\nGetting default LLM configuration...")
    response = requests.get(f"{BASE_URL}/config/llm/default")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    default_config = response.json()
    print(f"Default LLM config: {default_config['name']}")
    
    # Update LLM configuration
    print("\nUpdating LLM configuration...")
    update_data = {
        "name": "Updated Custom LLM Model",
        "config": {
            "type": "custom",
            "api_key": "your-custom-api-key",
            "model_name": "custom-model-v2",
            "parameters": {
                "temperature": 0.5,  # Changed from 0.7
                "max_tokens": 3000   # Changed from 2000
            }
        }
    }
    
    response = requests.put(f"{BASE_URL}/config/llm/{config_id}", json=update_data)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    updated_config = response.json()
    print("Updated LLM configuration:")
    pprint(updated_config)
    
    # Delete LLM configuration
    print("\nDeleting LLM configuration...")
    response = requests.delete(f"{BASE_URL}/config/llm/{config_id}")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    print(f"Deleted LLM config with ID: {config_id}")
    
    # Verify deletion
    print("\nVerifying deletion...")
    response = requests.get(f"{BASE_URL}/config/llm")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    configs = response.json()
    print(f"Found {len(configs)} LLM configurations after deletion")


def test_datasource_config_api():
    """Test data source configuration API endpoints"""
    print("\n=== Testing Data Source Configuration API ===")
    
    # Create a new data source configuration
    print("\nCreating data source configuration...")
    response = requests.post(f"{BASE_URL}/config/datasource", json=sample_datasource_config)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    config_data = response.json()
    config_id = config_data['id']
    print(f"Created data source config with ID: {config_id}")
    pprint(config_data)
    
    # Get all data source configurations
    print("\nGetting all data source configurations...")
    response = requests.get(f"{BASE_URL}/config/datasource")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    configs = response.json()
    print(f"Found {len(configs)} data source configurations")
    
    # Get default data source configuration
    print("\nGetting default data source configuration...")
    response = requests.get(f"{BASE_URL}/config/datasource/default")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    default_config = response.json()
    print(f"Default data source config: {default_config['name']}")
    
    # Update data source configuration
    print("\nUpdating data source configuration...")
    update_data = {
        "name": "Updated PDF Source Config",
        "config": {
            "type": "pdf",
            "connection_string": "",
            "source_path": "./updated_pdfs",  # Changed path
            "parameters": {
                "max_files": "20"  # Changed from 10
            }
        }
    }
    
    response = requests.put(f"{BASE_URL}/config/datasource/{config_id}", json=update_data)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    updated_config = response.json()
    print("Updated data source configuration:")
    pprint(updated_config)
    
    # Delete data source configuration
    print("\nDeleting data source configuration...")
    response = requests.delete(f"{BASE_URL}/config/datasource/{config_id}")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    print(f"Deleted data source config with ID: {config_id}")
    
    # Verify deletion
    print("\nVerifying deletion...")
    response = requests.get(f"{BASE_URL}/config/datasource")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    configs = response.json()
    print(f"Found {len(configs)} data source configurations after deletion")


def test_saved_generation_api():
    """Test saved generation configuration API endpoints"""
    print("\n=== Testing Saved Generation Configuration API ===")
    
    # First, create LLM and data source configurations to reference
    llm_response = requests.post(f"{BASE_URL}/config/llm", json=sample_llm_config)
    ds_response = requests.post(f"{BASE_URL}/config/datasource", json=sample_datasource_config)
    
    llm_id = llm_response.json()['id']
    ds_id = ds_response.json()['id']
    
    # Create a new saved generation configuration
    print("\nCreating saved generation configuration...")
    saved_config = {
        "name": "My Test Generation",
        "llm_config_id": llm_id,
        "data_source_config_id": ds_id,
        "dataset_type": "qa",  # Using a valid dataset type
        "sample_size": 100
    }
    
    response = requests.post(f"{BASE_URL}/config/saved", json=saved_config)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    config_data = response.json()
    config_id = config_data['id']
    print(f"Created saved generation config with ID: {config_id}")
    pprint(config_data)
    
    # Get all saved generation configurations
    print("\nGetting all saved generation configurations...")
    response = requests.get(f"{BASE_URL}/config/saved")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    configs = response.json()
    print(f"Found {len(configs)} saved generation configurations")
    
    # Get a specific saved generation configuration
    print("\nGetting specific saved generation configuration...")
    response = requests.get(f"{BASE_URL}/config/saved/{config_id}")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    config = response.json()
    print(f"Saved generation config: {config['name']}")
    
    # Update saved generation configuration
    print("\nUpdating saved generation configuration...")
    update_data = {
        "name": "Updated Test Generation",
        "dataset_type": "instruction",  # Changed from qa to instruction
        "sample_size": 200  # Changed from 100
    }
    
    response = requests.put(f"{BASE_URL}/config/saved/{config_id}", json=update_data)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    updated_config = response.json()
    print("Updated saved generation configuration:")
    pprint(updated_config)
    
    # Delete saved generation configuration
    print("\nDeleting saved generation configuration...")
    response = requests.delete(f"{BASE_URL}/config/saved/{config_id}")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    print(f"Deleted saved generation config with ID: {config_id}")
    
    # Verify deletion
    print("\nVerifying deletion...")
    response = requests.get(f"{BASE_URL}/config/saved")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    configs = response.json()
    print(f"Found {len(configs)} saved generation configurations after deletion")
    
    # Clean up the LLM and data source configurations
    requests.delete(f"{BASE_URL}/config/llm/{llm_id}")
    requests.delete(f"{BASE_URL}/config/datasource/{ds_id}")


def test_combined_config_api():
    """Test combined configuration API endpoint"""
    print("\n=== Testing Combined Configuration API ===")
    
    # Create a new LLM configuration
    print("\nCreating LLM configuration...")
    llm_response = requests.post(f"{BASE_URL}/config/llm", json=sample_llm_config)
    assert llm_response.status_code == 200, f"Expected 200, got {llm_response.status_code}: {llm_response.text}"
    
    # Create a new data source configuration
    print("\nCreating data source configuration...")
    ds_response = requests.post(f"{BASE_URL}/config/datasource", json=sample_datasource_config)
    assert ds_response.status_code == 200, f"Expected 200, got {ds_response.status_code}: {ds_response.text}"
    
    # Get all configurations
    print("\nGetting all configurations...")
    response = requests.get(f"{BASE_URL}/config")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    config_data = response.json()
    print(f"Found {len(config_data['llm_configs'])} LLM configurations")
    print(f"Found {len(config_data['data_source_configs'])} data source configurations")
    
    # Clean up
    llm_id = llm_response.json()['id']
    ds_id = ds_response.json()['id']
    
    print("\nCleaning up test data...")
    requests.delete(f"{BASE_URL}/config/llm/{llm_id}")
    requests.delete(f"{BASE_URL}/config/datasource/{ds_id}")


if __name__ == "__main__":
    print("Testing Configuration API endpoints")
    print("Make sure the server is running on http://localhost:8000")
    
    try:
        test_llm_config_api()
        test_datasource_config_api()
        test_saved_generation_api()
        test_combined_config_api()
        print("\nAll tests completed successfully!")
    except Exception as e:
        print(f"\nTest failed: {str(e)}") 