#!/usr/bin/env python3
import asyncio
import json
import os
import sys
import argparse
import aiohttp
from typing import Dict, Any

# Test payload for the API
TEST_PAYLOAD = {
    "dataset_type": "qa",
    "data_source": {
        "type": "pdf",
        "connection_string": "",  # Will be set from command line args
        "parameters": {
            "extract_metadata": True,
            "extract_layout": True
        }
    },
    "llm_config": {
        "type": "custom",
        "api_key": "",  # Will be set from command line args or env vars
        "model_name": "hkllm",  # Default to hkllm
        "parameters": {
            "api_base_url": "https://apillm.healthkart.com/v1",  # Default to HealthKart API
            "temperature": 0.7,
            "max_tokens": 1000,
            "top_p": 0.95
        }
    },
    "sample_size": 5,  # Reduced for testing
    "output_format": "json"
}

async def test_api(api_url: str, payload: Dict[str, Any]) -> None:
    """
    Test the API by sending a POST request with the given payload
    """
    print(f"🚀 Testing API at {api_url}")
    print(f"📄 Request payload:")
    print(json.dumps(payload, indent=2))
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(api_url, json=payload) as response:
                status = response.status
                print(f"🔄 Response status: {status}")
                
                if status == 200:
                    result = await response.json()
                    print("✅ Success! Response:")
                    print(json.dumps(result, indent=2))
                    
                    # Print some statistics about the generated data
                    data_count = len(result.get("data", []))
                    print(f"📊 Generated {data_count} synthetic data samples")
                    
                    if data_count > 0 and "question" in result["data"][0]:
                        # Print a sample question-answer pair
                        sample = result["data"][0]
                        print("\n📝 Sample QA pair:")
                        print(f"Q: {sample['question']}")
                        print(f"A: {sample['answer']}")
                else:
                    error_text = await response.text()
                    print(f"❌ Error: {error_text}")
        except Exception as e:
            print(f"❌ Exception: {str(e)}")

def parse_arguments():
    parser = argparse.ArgumentParser(description="Test the synthetic data generator API")
    parser.add_argument("--pdf", required=True, help="Path to PDF file to use as data source")
    parser.add_argument("--model", default="hkllm", help="Model name to use for generation")
    parser.add_argument("--api-key", help="API key (if needed)")
    parser.add_argument("--api-base", default="https://apillm.healthkart.com/v1", help="Base URL for the vLLM API")
    parser.add_argument("--backend-url", default="http://localhost:8000", help="URL of the backend API")
    parser.add_argument("--samples", type=int, default=5, help="Number of samples to generate")
    return parser.parse_args()

async def main():
    args = parse_arguments()
    
    # Update the payload with command line arguments
    TEST_PAYLOAD["data_source"]["connection_string"] = args.pdf
    TEST_PAYLOAD["llm_config"]["model_name"] = args.model
    TEST_PAYLOAD["llm_config"]["parameters"]["api_base_url"] = args.api_base
    TEST_PAYLOAD["sample_size"] = args.samples
    
    # Set API key from args or environment variable
    api_key = args.api_key or os.environ.get("LLM_API_KEY", "")
    if api_key:
        TEST_PAYLOAD["llm_config"]["api_key"] = api_key
    
    # Construct the API URL
    api_url = f"{args.backend_url}/api/v1/generate"
    
    await test_api(api_url, TEST_PAYLOAD)

if __name__ == "__main__":
    asyncio.run(main()) 