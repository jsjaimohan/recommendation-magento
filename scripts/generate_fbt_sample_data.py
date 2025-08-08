#!/usr/bin/env python3
"""
Generate sample data for FBT (Frequently Bought Together) testing
"""

import requests
import json
import random
from datetime import datetime, timedelta
import time

# API base URL
BASE_URL = "http://localhost:8000"

def create_product(product_data):
    """Create a product in the database via behavior tracking"""
    try:
        # Create product by tracking a behavior (this will auto-create the product)
        behavior_data = {
            "user_id": "user_001",
            "product_id": product_data["product_id"],
            "behavior_type": "view",
            "session_id": "setup_session",
            "metadata": {
                "product_name": product_data["name"],
                "category": product_data["category"],
                "price": product_data["price"]
            }
        }
        
        response = requests.post(f"{BASE_URL}/behaviors", json=behavior_data)
        if response.status_code == 200:
            # Update the product with proper details
            update_product_details(product_data)
            print(f"✅ Product created: {product_data['name']}")
            return True
        else:
            print(f"❌ Failed to create product {product_data['product_id']}: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error creating product {product_data['product_id']}: {e}")
        return False

def update_product_details(product_data):
    """Update product details in the database"""
    try:
        # Direct database update to ensure product details are saved
        import subprocess
        # Escape single quotes in product name
        escaped_name = product_data['name'].replace("'", "\\'")
        sql_command = f"""
        UPDATE products 
        SET name = '{escaped_name}', 
            category = '{product_data['category']}', 
            price = {product_data['price']}
        WHERE product_id = '{product_data['product_id']}';
        """
        
        # Execute SQL command via docker exec
        result = subprocess.run([
            'docker', 'exec', '-i', 'magento-recommendation-mariadb-1',
            'mysql', '-u', 'recommendation_user', '-ppassword', 'recommendations'
        ], input=sql_command, text=True, capture_output=True)
        
        if result.returncode == 0:
            return True
        else:
            print(f"⚠️ Warning: Could not update product {product_data['product_id']}: {result.stderr}")
            return False
    except Exception as e:
        print(f"⚠️ Warning: Could not update product {product_data['product_id']}: {e}")
        return False

def generate_sample_products():
    """Generate sample products for testing"""
    products = [
        {"product_id": "PROD001", "name": "iPhone 15 Pro", "category": "electronics", "price": 999.99},
        {"product_id": "PROD002", "name": "Samsung Galaxy S24", "category": "electronics", "price": 899.99},
        {"product_id": "PROD003", "name": "MacBook Pro 16", "category": "electronics", "price": 2499.99},
        {"product_id": "PROD004", "name": "Dell XPS 13", "category": "electronics", "price": 1299.99},
        {"product_id": "PROD005", "name": "AirPods Pro", "category": "electronics", "price": 249.99},
        {"product_id": "PROD006", "name": "Sony WH-1000XM5", "category": "electronics", "price": 399.99},
        {"product_id": "PROD007", "name": "iPad Air", "category": "electronics", "price": 599.99},
        {"product_id": "PROD008", "name": "Apple Watch Series 9", "category": "electronics", "price": 399.99},
        {"product_id": "PROD009", "name": "Nike Air Max", "category": "shoes", "price": 129.99},
        {"product_id": "PROD010", "name": "Adidas Ultraboost", "category": "shoes", "price": 179.99},
        {"product_id": "PROD011", "name": "Levi's 501 Jeans", "category": "clothing", "price": 59.99},
        {"product_id": "PROD012", "name": "Nike Dri-FIT Shirt", "category": "clothing", "price": 34.99},
        {"product_id": "PROD013", "name": "iPhone Case", "category": "accessories", "price": 19.99},
        {"product_id": "PROD014", "name": "Screen Protector", "category": "accessories", "price": 9.99},
        {"product_id": "PROD015", "name": "Wireless Charger", "category": "accessories", "price": 29.99},
    ]
    return products

def generate_sample_users():
    """Generate sample users for testing"""
    users = [
        "user_001", "user_002"  # Use existing users
    ]
    return users

def create_purchase_transaction(user_id, order_id, products, total_amount):
    """Create a purchase transaction"""
    url = f"{BASE_URL}/transactions/purchase"
    
    # Convert products to transaction items
    transaction_items = []
    for product in products:
        item = {
            "product_id": product["product_id"],
            "quantity": product.get("quantity", 1),
            "unit_price": product["price"],
            "total_price": product["price"] * product.get("quantity", 1)
        }
        transaction_items.append(item)
    
    payload = {
        "user_id": user_id,
        "order_id": order_id,
        "products": transaction_items,
        "total_amount": total_amount,
        "status": "completed"
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print(f"✅ Transaction created: {order_id} - {user_id} - ${total_amount:.2f}")
            return True
        else:
            print(f"❌ Failed to create transaction {order_id}: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error creating transaction {order_id}: {e}")
        return False

def generate_fbt_scenarios():
    """Generate realistic FBT scenarios"""
    scenarios = [
        # Electronics combinations
        {
            "name": "iPhone + AirPods",
            "products": ["PROD001", "PROD005"],
            "frequency": 0.8  # 80% of iPhone buyers also buy AirPods
        },
        {
            "name": "iPhone + Case + Screen Protector",
            "products": ["PROD001", "PROD013", "PROD014"],
            "frequency": 0.9  # 90% of iPhone buyers buy protection
        },
        {
            "name": "MacBook + AirPods",
            "products": ["PROD003", "PROD005"],
            "frequency": 0.6  # 60% of MacBook buyers also buy AirPods
        },
        {
            "name": "Samsung + Sony Headphones",
            "products": ["PROD002", "PROD006"],
            "frequency": 0.4  # 40% of Samsung buyers buy Sony headphones
        },
        # Clothing combinations
        {
            "name": "Nike Shoes + Nike Shirt",
            "products": ["PROD009", "PROD012"],
            "frequency": 0.7  # 70% of Nike shoe buyers buy Nike shirts
        },
        {
            "name": "Jeans + Shirt",
            "products": ["PROD011", "PROD012"],
            "frequency": 0.5  # 50% of jeans buyers buy shirts
        },
        # Accessories combinations
        {
            "name": "iPhone + Wireless Charger",
            "products": ["PROD001", "PROD015"],
            "frequency": 0.3  # 30% of iPhone buyers buy wireless chargers
        },
        {
            "name": "Screen Protector + Case",
            "products": ["PROD014", "PROD013"],
            "frequency": 0.8  # 80% of screen protector buyers buy cases
        }
    ]
    return scenarios

def setup_products():
    """Setup all required products in the database"""
    print("🔧 Setting up products in database...")
    products = generate_sample_products()
    
    for product in products:
        create_product(product)
        time.sleep(0.1)  # Small delay
    
    print("✅ Product setup completed")

def generate_sample_transactions():
    """Generate realistic sample transactions based on FBT scenarios"""
    products = generate_sample_products()
    users = generate_sample_users()
    scenarios = generate_fbt_scenarios()
    
    transactions_created = 0
    order_counter = 1000
    
    print("🚀 Generating sample FBT transactions...")
    
    # Generate transactions based on scenarios
    for scenario in scenarios:
        scenario_products = [p for p in products if p["product_id"] in scenario["products"]]
        
        # Generate multiple transactions for this scenario
        num_transactions = int(20 * scenario["frequency"])  # Reduced for testing
        
        for i in range(num_transactions):
            user_id = random.choice(users)
            order_id = f"ORDER_{order_counter}"
            order_counter += 1
            
            # Calculate total amount
            total_amount = sum(p["price"] for p in scenario_products)
            
            # Create transaction
            success = create_purchase_transaction(user_id, order_id, scenario_products, total_amount)
            if success:
                transactions_created += 1
            
            time.sleep(0.1)  # Small delay to avoid overwhelming the API
    
    # Generate some random single-product transactions
    for i in range(10):
        user_id = random.choice(users)
        product = random.choice(products)
        order_id = f"ORDER_{order_counter}"
        order_counter += 1
        
        success = create_purchase_transaction(user_id, order_id, [product], product["price"])
        if success:
            transactions_created += 1
        
        time.sleep(0.1)
    
    # Generate some random multi-product transactions
    for i in range(15):
        user_id = random.choice(users)
        num_products = random.randint(2, 4)
        selected_products = random.sample(products, num_products)
        order_id = f"ORDER_{order_counter}"
        order_counter += 1
        
        total_amount = sum(p["price"] for p in selected_products)
        
        success = create_purchase_transaction(user_id, order_id, selected_products, total_amount)
        if success:
            transactions_created += 1
        
        time.sleep(0.1)
    
    print(f"\n✅ Generated {transactions_created} sample transactions")
    return transactions_created

def test_fbt_generation():
    """Test FBT rule generation"""
    print("\n🧪 Testing FBT rule generation...")
    
    url = f"{BASE_URL}/fbt/generate"
    payload = {
        "min_support": 0.01,
        "min_confidence": 0.3,
        "clear_existing": True
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ FBT rules generated successfully!")
            print(f"   - Rules generated: {result.get('rules_generated', 0)}")
            print(f"   - Transactions processed: {result.get('transactions_processed', 0)}")
            print(f"   - Execution time: {result.get('execution_time', 0):.2f}s")
            return True
        else:
            print(f"❌ Failed to generate FBT rules: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error generating FBT rules: {e}")
        return False

def test_fbt_recommendations():
    """Test FBT recommendations"""
    print("\n🧪 Testing FBT recommendations...")
    
    # Test recommendations for iPhone
    url = f"{BASE_URL}/fbt/recommendations"
    payload = {
        "product_id": "PROD001",
        "limit": 5,
        "min_confidence": 0.3
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ FBT recommendations for iPhone:")
            print(f"   - Found {result.get('count', 0)} associations")
            for assoc in result.get('associations', []):
                print(f"   - {assoc.get('product_name', 'Unknown')} (confidence: {assoc.get('confidence', 0):.2f})")
            return True
        else:
            print(f"❌ Failed to get FBT recommendations: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error getting FBT recommendations: {e}")
        return False

def main():
    """Main function"""
    print("🎯 FBT Sample Data Generator")
    print("=" * 50)
    
    # Check if API is running
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code != 200:
            print("❌ API is not running. Please start the application first.")
            return
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        print("Please ensure the application is running on http://localhost:8000")
        return
    
    print("✅ API is running")
    
    # Setup products first
    setup_products()
    
    # Generate sample transactions
    transactions_created = generate_sample_transactions()
    
    if transactions_created > 0:
        # Test FBT generation
        if test_fbt_generation():
            # Test FBT recommendations
            test_fbt_recommendations()
    
    print("\n🎉 FBT sample data generation completed!")

if __name__ == "__main__":
    main()
