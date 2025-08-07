#!/usr/bin/env python3
"""
Sample data generator for the recommendation system
"""

import json
import random
from datetime import datetime, timedelta

def generate_sample_data():
    """Generate sample user behaviors and product data"""
    
    # Sample products
    products = [
        {"product_id": "PROD001", "name": "iPhone 15 Pro", "category": "electronics", "subcategory": "smartphones", "price": 999.99},
        {"product_id": "PROD002", "name": "Samsung Galaxy S24", "category": "electronics", "subcategory": "smartphones", "price": 899.99},
        {"product_id": "PROD003", "name": "MacBook Pro 16", "category": "electronics", "subcategory": "laptops", "price": 2499.99},
        {"product_id": "PROD004", "name": "Dell XPS 15", "category": "electronics", "subcategory": "laptops", "price": 1899.99},
        {"product_id": "PROD005", "name": "Nike Air Max", "category": "sports", "subcategory": "shoes", "price": 129.99},
        {"product_id": "PROD006", "name": "Adidas Ultraboost", "category": "sports", "subcategory": "shoes", "price": 179.99},
        {"product_id": "PROD007", "name": "Harry Potter Book Set", "category": "books", "subcategory": "fiction", "price": 89.99},
        {"product_id": "PROD008", "name": "Lord of the Rings Trilogy", "category": "books", "subcategory": "fiction", "price": 79.99},
        {"product_id": "PROD009", "name": "Coffee Maker", "category": "home", "subcategory": "kitchen", "price": 149.99},
        {"product_id": "PROD010", "name": "Blender", "category": "home", "subcategory": "kitchen", "price": 89.99},
        {"product_id": "PROD011", "name": "Wireless Headphones", "category": "electronics", "subcategory": "audio", "price": 199.99},
        {"product_id": "PROD012", "name": "Smart Watch", "category": "electronics", "subcategory": "wearables", "price": 299.99},
        {"product_id": "PROD013", "name": "Yoga Mat", "category": "sports", "subcategory": "fitness", "price": 29.99},
        {"product_id": "PROD014", "name": "Dumbbells Set", "category": "sports", "subcategory": "fitness", "price": 89.99},
        {"product_id": "PROD015", "name": "Cookbook Collection", "category": "books", "subcategory": "non-fiction", "price": 59.99}
    ]
    
    # Sample users
    users = [f"user_{i:03d}" for i in range(1, 21)]
    
    # Behavior types and their weights
    behavior_types = ["view", "cart", "purchase", "wishlist"]
    behavior_weights = [0.4, 0.3, 0.2, 0.1]  # More views, fewer purchases
    
    # Generate user behaviors
    behaviors = []
    base_date = datetime.now() - timedelta(days=30)
    
    for user in users:
        # Each user interacts with 3-8 products
        num_interactions = random.randint(3, 8)
        user_products = random.sample(products, num_interactions)
        
        for i, product in enumerate(user_products):
            # Generate multiple behaviors for some products
            num_behaviors = random.choices([1, 2, 3], weights=[0.6, 0.3, 0.1])[0]
            
            for j in range(num_behaviors):
                behavior_type = random.choices(behavior_types, weights=behavior_weights)[0]
                timestamp = base_date + timedelta(
                    days=random.randint(0, 30),
                    hours=random.randint(0, 23),
                    minutes=random.randint(0, 59)
                )
                
                behavior = {
                    "user_id": user,
                    "product_id": product["product_id"],
                    "behavior_type": behavior_type,
                    "timestamp": timestamp.isoformat(),
                    "session_id": f"sess_{user}_{i}_{j}",
                    "metadata": {
                        "page_url": f"/product/{product['product_id']}",
                        "referrer": random.choice(["search", "category", "homepage", "email"])
                    }
                }
                behaviors.append(behavior)
    
    return {
        "user_behaviors": behaviors,
        "product_data": products
    }

def save_sample_data():
    """Save sample data to JSON files"""
    data = generate_sample_data()
    
    # Save user behaviors
    with open("sample_user_behaviors.json", "w") as f:
        json.dump(data["user_behaviors"], f, indent=2)
    
    # Save product data
    with open("sample_product_data.json", "w") as f:
        json.dump(data["product_data"], f, indent=2)
    
    print(f"Generated {len(data['user_behaviors'])} user behaviors")
    print(f"Generated {len(data['product_data'])} products")
    print("Sample data saved to:")
    print("- sample_user_behaviors.json")
    print("- sample_product_data.json")

if __name__ == "__main__":
    save_sample_data()
