#!/usr/bin/env python3
"""
Test script for the recommendation API
"""

import requests
import json
import time

# API base URL
BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_model_status():
    """Test model status endpoint"""
    print("Testing model status...")
    response = requests.get(f"{BASE_URL}/models/status")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def load_sample_data():
    """Load sample data from files"""
    try:
        with open("sample_user_behaviors.json", "r") as f:
            user_behaviors = json.load(f)
        
        with open("sample_product_data.json", "r") as f:
            product_data = json.load(f)
        
        return user_behaviors, product_data
    except FileNotFoundError:
        print("Sample data files not found. Please run the sample data generator first.")
        return None, None

def test_training():
    """Test model training"""
    print("Testing model training...")
    
    user_behaviors, product_data = load_sample_data()
    if not user_behaviors or not product_data:
        return
    
    training_data = {
        "user_behaviors": user_behaviors,
        "product_data": product_data
    }
    
    response = requests.post(f"{BASE_URL}/train", json=training_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_recommendations():
    """Test recommendation endpoints"""
    print("Testing recommendation endpoints...")
    
    # Test different algorithms
    algorithms = ["user_based", "content_based", "hybrid"]
    test_users = ["user_001", "user_005", "user_010"]
    
    for algorithm in algorithms:
        print(f"\nTesting {algorithm} algorithm:")
        for user_id in test_users:
            request_data = {
                "user_id": user_id,
                "algorithm": algorithm,
                "n_recommendations": 3
            }
            
            response = requests.post(f"{BASE_URL}/recommendations", json=request_data)
            print(f"  User {user_id}: Status {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"    Recommendations: {len(result['recommendations'])}")
                print(f"    Execution time: {result['execution_time']:.3f}s")
                
                # Show first recommendation
                if result['recommendations']:
                    first_rec = result['recommendations'][0]
                    print(f"    First recommendation: {first_rec['name']} (${first_rec['price']})")
            else:
                print(f"    Error: {response.text}")
    
    print()

def test_behavior_tracking():
    """Test behavior tracking"""
    print("Testing behavior tracking...")
    
    behavior_data = {
        "user_id": "user_001",
        "product_id": "PROD001",
        "behavior_type": "view",
        "timestamp": "2024-01-15T10:30:00Z",
        "session_id": "test_session_001",
        "metadata": {
            "page_url": "/product/PROD001",
            "referrer": "search"
        }
    }
    
    response = requests.post(f"{BASE_URL}/behaviors", json=behavior_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_category_filter():
    """Test category filtering"""
    print("Testing category filtering...")
    
    request_data = {
        "user_id": "user_001",
        "algorithm": "hybrid",
        "n_recommendations": 5,
        "category_filter": "electronics"
    }
    
    response = requests.post(f"{BASE_URL}/recommendations", json=request_data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Electronics recommendations: {len(result['recommendations'])}")
        for rec in result['recommendations']:
            print(f"  - {rec['name']} ({rec['category']})")
    else:
        print(f"Error: {response.text}")
    print()

def main():
    """Run all tests"""
    print("=== Recommendation API Test Suite ===\n")
    
    # Test basic endpoints
    test_health()
    test_model_status()
    
    # Test training
    test_training()
    
    # Wait a moment for training to complete
    time.sleep(2)
    
    # Test recommendations
    test_recommendations()
    
    # Test behavior tracking
    test_behavior_tracking()
    
    # Test category filtering
    test_category_filter()
    
    print("=== Test Suite Complete ===")

if __name__ == "__main__":
    main()
