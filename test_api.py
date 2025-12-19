import httpx
import asyncio
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

async def test_health():
    '''health check'''
    print("\n" + "="*60)
    print("Testing health check...")
    print("="*60)

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/health")
            print(f"Status: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            return response.status_code == 200
        except Exception as e:
            print(f"Error: {e}")
            return False

async def test_chat_completion():
    """test non-streaming chat completion"""
    print("\n" + "="*60)
    print("💬 Testing Chat Completion (Non-streaming)...")
    print("="*60)
    
    payload = {
        "messages": [
            {"role": "user", "content": "Say hello in 10 words or less"}
        ],
        "temperature": 0.7,
        "max_tokens": 50
    }
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            start_time = datetime.now()
            response = await client.post(
                f"{BASE_URL}/v1/chat/completions",
                json=payload
            )
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            print(f"Status: {response.status_code}")
            print(f"Duration: {duration:.2f}s")
            
            if response.status_code == 200:
                data = response.json()
                print(f"\nModel: {data['model']}")
                print(f"Response: {data['choices'][0]['message']['content']}")
                print(f"Tokens: {data['usage']}")
                return True
            else:
                print(f"Error: {response.text}")
                return False
        except Exception as e:
            print(f"Error: {e}")
            return False

async def test_chat_completion_stream():
    """test streaming chat completion"""
    print("\n" + "="*60)
    print("Testing Chat Completion (Streaming)...")
    print("="*60)
    
    payload = {
        "messages": [
            {"role": "user", "content": "Count from 1 to 5"}
        ],
        "stream": True,
        "max_tokens": 30
    }
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            print("Response: ", end="", flush=True)
            async with client.stream(
                "POST",
                f"{BASE_URL}/v1/chat/completions",
                json=payload
            ) as response:
                if response.status_code == 200:
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data_str = line[6:]  # 去掉 "data: " 前缀
                            if data_str.strip() == "[DONE]":
                                break
                            try:
                                data = json.loads(data_str)
                                if 'choices' in data and len(data['choices']) > 0:
                                    delta = data['choices'][0].get('delta', {})
                                    content = delta.get('content', '')
                                    if content:
                                        print(content, end="", flush=True)
                            except json.JSONDecodeError:
                                pass
                    print("\n")
                    return True
                else:
                    print(f"\nError: Status {response.status_code}")
                    return False
        except Exception as e:
            print(f"\nError: {e}")
            return False

async def test_metrics():
    """test metrics endpoint"""
    print("\n" + "="*60)
    print("Testing Metrics Endpoint...")
    print("="*60)
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/metrics")
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                # only print first 10 metrics
                lines = response.text.split('\n')[:10]
                print("Sample metrics:")
                for line in lines:
                    if line and not line.startswith('#'):
                        print(f"  {line}")
                print("  ...")
                return True
            else:
                print(f"Error: {response.text}")
                return False
        except Exception as e:
            print(f"Error: {e}")
            return False

async def main():
    """run all tests and summarize results"""
    print("\n" + "="*60)
    print("Distributed LLM Serving - API Tests")
    print("="*60)
    print(f"Base URL: {BASE_URL}")
    
    results = []
    
    # test health check
    results.append(("Health Check", await test_health()))
    
    # test metrics
    results.append(("Metrics", await test_metrics()))
    
    # test chat completion
    results.append(("Chat Completion", await test_chat_completion()))
    
    # test streaming chat completion
    results.append(("Streaming", await test_chat_completion_stream()))
    
    # print summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    
    for name, passed in results:
        status = "PASSED" if passed else "FAILED"
        print(f"{name:25} {status}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\nAll tests passed!")
        return 0
    else:
        print("\nSome tests failed. Check the logs above.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)    