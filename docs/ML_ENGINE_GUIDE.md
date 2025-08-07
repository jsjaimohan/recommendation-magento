# ML Engine Guide
## Magento Recommendation Microservice

### Overview
This document explains the Machine Learning (ML) Engine for the recommendation system. We'll use Python with scikit-learn for most algorithms, keeping it simple and beginner-friendly while achieving effective recommendation results.

### 1. Understanding Recommendation Systems

#### 1.1 What is a Recommendation System?
A recommendation system suggests products to users based on their preferences and behavior. Think of it like how Netflix suggests movies or Amazon suggests products.

#### 1.2 Types of Recommendation Algorithms

**Collaborative Filtering**: "Users like you also bought..."
- **User-based**: Find similar users and recommend what they liked
- **Item-based**: Find similar items and recommend them

**Content-based Filtering**: "Based on what you've liked before..."
- Recommends items similar to what the user has already shown interest in

**Hybrid Approach**: Combines both methods for better results

### 2. Python Setup for Beginners

#### 2.1 Required Libraries
```python
# Core libraries
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, precision_score, recall_score

# Recommendation algorithms
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import NMF, TruncatedSVD

# Data processing
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.impute import SimpleImputer

# Visualization (optional)
import matplotlib.pyplot as plt
import seaborn as sns
```

#### 2.2 Installation
```bash
# Install required packages
pip install pandas numpy scikit-learn matplotlib seaborn

# For additional recommendation algorithms
pip install scikit-surprise

# For data visualization
pip install plotly
```

### 3. Data Structure

#### 3.1 User-Item Matrix
This is the foundation of recommendation systems:

```python
# Example user-item matrix (ratings/purchases)
user_item_matrix = {
    'user_1': {'product_A': 1, 'product_B': 0, 'product_C': 1},
    'user_2': {'product_A': 0, 'product_B': 1, 'product_C': 1},
    'user_3': {'product_A': 1, 'product_B': 1, 'product_C': 0},
    'user_4': {'product_A': 0, 'product_B': 0, 'product_C': 1}
}

# Convert to pandas DataFrame
import pandas as pd
df = pd.DataFrame(user_item_matrix).T
print(df)
```

#### 3.2 Data Collection
```python
# Sample data structure from your Magento system
user_behaviors = [
    {'user_id': 'user_1', 'product_id': 'product_A', 'behavior_type': 'purchase', 'timestamp': '2024-01-15'},
    {'user_id': 'user_1', 'product_id': 'product_B', 'behavior_type': 'view', 'timestamp': '2024-01-15'},
    {'user_id': 'user_2', 'product_id': 'product_A', 'behavior_type': 'cart', 'timestamp': '2024-01-15'},
    # ... more data
]

product_data = [
    {'product_id': 'product_A', 'name': 'iPhone 15', 'category': 'electronics', 'price': 999.99},
    {'product_id': 'product_B', 'name': 'Samsung Galaxy', 'category': 'electronics', 'price': 899.99},
    # ... more products
]
```

### 4. Collaborative Filtering (User-Based)

#### 4.1 Simple User-Based Recommendations
```python
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class UserBasedRecommender:
    def __init__(self):
        self.user_item_matrix = None
        self.user_similarities = None
        
    def fit(self, user_behaviors):
        """
        Train the recommender with user behavior data
        """
        # Convert behaviors to user-item matrix
        df = pd.DataFrame(user_behaviors)
        self.user_item_matrix = df.pivot_table(
            index='user_id', 
            columns='product_id', 
            values='behavior_type',
            aggfunc='count',
            fill_value=0
        )
        
        # Calculate user similarities using cosine similarity
        self.user_similarities = cosine_similarity(self.user_item_matrix)
        
    def recommend(self, user_id, n_recommendations=5):
        """
        Get recommendations for a specific user
        """
        if user_id not in self.user_item_matrix.index:
            return []
            
        # Find similar users
        user_idx = self.user_item_matrix.index.get_loc(user_id)
        similar_users = self.user_similarities[user_idx]
        
        # Get top similar users (excluding the user themselves)
        similar_user_indices = np.argsort(similar_users)[::-1][1:6]  # Top 5 similar users
        
        # Get products that similar users liked but current user hasn't interacted with
        user_products = set(self.user_item_matrix.columns[self.user_item_matrix.iloc[user_idx] > 0])
        recommendations = []
        
        for similar_user_idx in similar_user_indices:
            similar_user_id = self.user_item_matrix.index[similar_user_idx]
            similar_user_products = set(self.user_item_matrix.columns[self.user_item_matrix.iloc[similar_user_idx] > 0])
            
            # Products that similar user liked but current user hasn't
            new_products = similar_user_products - user_products
            recommendations.extend(list(new_products))
            
        return list(set(recommendations))[:n_recommendations]

# Usage example
recommender = UserBasedRecommender()
recommender.fit(user_behaviors)
recommendations = recommender.recommend('user_1', n_recommendations=3)
print(f"Recommendations for user_1: {recommendations}")
```

### 5. Content-Based Filtering

#### 5.1 Product Feature Extraction
```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class ContentBasedRecommender:
    def __init__(self):
        self.product_features = None
        self.product_similarities = None
        
    def fit(self, product_data):
        """
        Train the recommender with product data
        """
        # Create product descriptions for feature extraction
        product_descriptions = []
        product_ids = []
        
        for product in product_data:
            # Combine product attributes into a description
            description = f"{product['name']} {product['category']} {product.get('brand', '')}"
            product_descriptions.append(description)
            product_ids.append(product['product_id'])
        
        # Extract features using TF-IDF
        tfidf = TfidfVectorizer(stop_words='english')
        self.product_features = tfidf.fit_transform(product_descriptions)
        
        # Calculate product similarities
        self.product_similarities = cosine_similarity(self.product_features)
        
    def recommend(self, product_id, n_recommendations=5):
        """
        Get similar products based on content
        """
        # Find product index
        product_idx = list(product_ids).index(product_id)
        
        # Get similar products
        similar_products = self.product_similarities[product_idx]
        similar_indices = np.argsort(similar_products)[::-1][1:n_recommendations+1]
        
        return [product_ids[i] for i in similar_indices]

# Usage example
content_recommender = ContentBasedRecommender()
content_recommender.fit(product_data)
similar_products = content_recommender.recommend('product_A', n_recommendations=3)
print(f"Products similar to product_A: {similar_products}")
```

### 6. Matrix Factorization (Advanced)

#### 6.1 Using Non-Negative Matrix Factorization (NMF)
```python
from sklearn.decomposition import NMF

class MatrixFactorizationRecommender:
    def __init__(self, n_components=50):
        self.n_components = n_components
        self.model = NMF(n_components=n_components, random_state=42)
        self.user_factors = None
        self.item_factors = None
        
    def fit(self, user_item_matrix):
        """
        Train the matrix factorization model
        """
        # Fit the model
        self.user_factors = self.model.fit_transform(user_item_matrix)
        self.item_factors = self.model.components_
        
    def predict_rating(self, user_idx, item_idx):
        """
        Predict rating for user-item pair
        """
        return np.dot(self.user_factors[user_idx], self.item_factors[:, item_idx])
    
    def recommend(self, user_id, n_recommendations=5):
        """
        Get recommendations for a user
        """
        if user_id not in self.user_item_matrix.index:
            return []
            
        user_idx = self.user_item_matrix.index.get_loc(user_id)
        
        # Get user's predicted ratings for all items
        predicted_ratings = []
        for item_idx in range(self.item_factors.shape[1]):
            rating = self.predict_rating(user_idx, item_idx)
            predicted_ratings.append((item_idx, rating))
        
        # Sort by predicted rating and get top recommendations
        predicted_ratings.sort(key=lambda x: x[1], reverse=True)
        
        # Filter out items the user has already interacted with
        user_items = set(self.user_item_matrix.columns[self.user_item_matrix.iloc[user_idx] > 0])
        recommendations = []
        
        for item_idx, rating in predicted_ratings:
            item_id = self.user_item_matrix.columns[item_idx]
            if item_id not in user_items:
                recommendations.append(item_id)
                if len(recommendations) >= n_recommendations:
                    break
                    
        return recommendations

# Usage example
mf_recommender = MatrixFactorizationRecommender(n_components=20)
mf_recommender.fit(user_item_matrix)
recommendations = mf_recommender.recommend('user_1', n_recommendations=3)
print(f"Matrix Factorization recommendations: {recommendations}")
```

### 7. Hybrid Recommender

#### 7.1 Combining Multiple Approaches
```python
class HybridRecommender:
    def __init__(self):
        self.user_based = UserBasedRecommender()
        self.content_based = ContentBasedRecommender()
        self.matrix_factorization = MatrixFactorizationRecommender()
        
    def fit(self, user_behaviors, product_data):
        """
        Train all recommendation models
        """
        self.user_based.fit(user_behaviors)
        self.content_based.fit(product_data)
        
        # Create user-item matrix for matrix factorization
        df = pd.DataFrame(user_behaviors)
        user_item_matrix = df.pivot_table(
            index='user_id', 
            columns='product_id', 
            values='behavior_type',
            aggfunc='count',
            fill_value=0
        )
        self.matrix_factorization.fit(user_item_matrix)
        
    def recommend(self, user_id, n_recommendations=5):
        """
        Get hybrid recommendations
        """
        # Get recommendations from all models
        user_recs = self.user_based.recommend(user_id, n_recommendations)
        content_recs = self.content_based.recommend(user_id, n_recommendations)
        mf_recs = self.matrix_factorization.recommend(user_id, n_recommendations)
        
        # Combine and rank recommendations
        all_recs = user_recs + content_recs + mf_recs
        
        # Simple ranking: count frequency of each recommendation
        from collections import Counter
        rec_counts = Counter(all_recs)
        
        # Return top recommendations
        return [rec for rec, count in rec_counts.most_common(n_recommendations)]

# Usage example
hybrid_recommender = HybridRecommender()
hybrid_recommender.fit(user_behaviors, product_data)
recommendations = hybrid_recommender.recommend('user_1', n_recommendations=5)
print(f"Hybrid recommendations: {recommendations}")
```

### 8. Evaluation Metrics

#### 8.1 Simple Evaluation Functions
```python
def evaluate_recommendations(actual_interactions, predicted_recommendations):
    """
    Simple evaluation of recommendation quality
    """
    # Precision: How many recommended items were actually relevant
    relevant_recommendations = 0
    for rec in predicted_recommendations:
        if rec in actual_interactions:
            relevant_recommendations += 1
    
    precision = relevant_recommendations / len(predicted_recommendations) if predicted_recommendations else 0
    
    # Recall: How many relevant items were recommended
    recall = relevant_recommendations / len(actual_interactions) if actual_interactions else 0
    
    # F1 Score: Harmonic mean of precision and recall
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    return {
        'precision': precision,
        'recall': recall,
        'f1_score': f1_score
    }

# Usage example
actual_user_interactions = ['product_A', 'product_B']
predicted_recommendations = ['product_A', 'product_C', 'product_D']
metrics = evaluate_recommendations(actual_user_interactions, predicted_recommendations)
print(f"Evaluation metrics: {metrics}")
```

### 9. Real-World Implementation

#### 9.1 Complete ML Engine Class
```python
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import NMF
import pickle
import json

class RecommendationEngine:
    def __init__(self):
        self.user_based_model = None
        self.content_based_model = None
        self.hybrid_model = None
        self.is_trained = False
        
    def prepare_data(self, user_behaviors, product_data):
        """
        Prepare data for training
        """
        # Convert behaviors to DataFrame
        behaviors_df = pd.DataFrame(user_behaviors)
        
        # Create user-item matrix
        self.user_item_matrix = behaviors_df.pivot_table(
            index='user_id',
            columns='product_id',
            values='behavior_type',
            aggfunc='count',
            fill_value=0
        )
        
        # Prepare product features
        self.product_data = pd.DataFrame(product_data)
        
    def train_models(self):
        """
        Train all recommendation models
        """
        # Train user-based model
        self.user_based_model = cosine_similarity(self.user_item_matrix)
        
        # Train content-based model
        product_descriptions = self.product_data['name'] + ' ' + self.product_data['category']
        tfidf = TfidfVectorizer(stop_words='english')
        product_features = tfidf.fit_transform(product_descriptions)
        self.content_based_model = cosine_similarity(product_features)
        
        # Train matrix factorization model
        self.mf_model = NMF(n_components=min(20, min(self.user_item_matrix.shape)), random_state=42)
        self.user_factors = self.mf_model.fit_transform(self.user_item_matrix)
        self.item_factors = self.mf_model.components_
        
        self.is_trained = True
        
    def get_recommendations(self, user_id, algorithm='hybrid', n_recommendations=5):
        """
        Get recommendations using specified algorithm
        """
        if not self.is_trained:
            raise ValueError("Models must be trained before getting recommendations")
            
        if algorithm == 'user_based':
            return self._get_user_based_recommendations(user_id, n_recommendations)
        elif algorithm == 'content_based':
            return self._get_content_based_recommendations(user_id, n_recommendations)
        elif algorithm == 'hybrid':
            return self._get_hybrid_recommendations(user_id, n_recommendations)
        else:
            raise ValueError(f"Unknown algorithm: {algorithm}")
    
    def _get_user_based_recommendations(self, user_id, n_recommendations):
        """User-based collaborative filtering"""
        if user_id not in self.user_item_matrix.index:
            return []
            
        user_idx = self.user_item_matrix.index.get_loc(user_id)
        similar_users = self.user_based_model[user_idx]
        similar_user_indices = np.argsort(similar_users)[::-1][1:6]
        
        recommendations = []
        user_products = set(self.user_item_matrix.columns[self.user_item_matrix.iloc[user_idx] > 0])
        
        for similar_user_idx in similar_user_indices:
            similar_user_products = set(self.user_item_matrix.columns[self.user_item_matrix.iloc[similar_user_idx] > 0])
            new_products = similar_user_products - user_products
            recommendations.extend(list(new_products))
            
        return list(set(recommendations))[:n_recommendations]
    
    def _get_content_based_recommendations(self, user_id, n_recommendations):
        """Content-based filtering"""
        # For simplicity, recommend based on user's most recent interaction
        if user_id not in self.user_item_matrix.index:
            return []
            
        user_idx = self.user_item_matrix.index.get_loc(user_id)
        user_products = self.user_item_matrix.columns[self.user_item_matrix.iloc[user_idx] > 0]
        
        if len(user_products) == 0:
            return []
            
        # Get most recent product
        recent_product = user_products[0]
        product_idx = self.product_data[self.product_data['product_id'] == recent_product].index[0]
        
        similar_products = self.content_based_model[product_idx]
        similar_indices = np.argsort(similar_products)[::-1][1:n_recommendations+1]
        
        return self.product_data.iloc[similar_indices]['product_id'].tolist()
    
    def _get_hybrid_recommendations(self, user_id, n_recommendations):
        """Hybrid approach combining multiple methods"""
        user_recs = self._get_user_based_recommendations(user_id, n_recommendations)
        content_recs = self._get_content_based_recommendations(user_id, n_recommendations)
        
        # Combine and rank
        all_recs = user_recs + content_recs
        from collections import Counter
        rec_counts = Counter(all_recs)
        
        return [rec for rec, count in rec_counts.most_common(n_recommendations)]
    
    def save_model(self, filepath):
        """Save trained model to file"""
        model_data = {
            'user_item_matrix': self.user_item_matrix,
            'product_data': self.product_data,
            'user_based_model': self.user_based_model,
            'content_based_model': self.content_based_model,
            'user_factors': self.user_factors,
            'item_factors': self.item_factors,
            'is_trained': self.is_trained
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
    
    def load_model(self, filepath):
        """Load trained model from file"""
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)
            
        self.user_item_matrix = model_data['user_item_matrix']
        self.product_data = model_data['product_data']
        self.user_based_model = model_data['user_based_model']
        self.content_based_model = model_data['content_based_model']
        self.user_factors = model_data['user_factors']
        self.item_factors = model_data['item_factors']
        self.is_trained = model_data['is_trained']

# Usage example
engine = RecommendationEngine()

# Prepare and train
engine.prepare_data(user_behaviors, product_data)
engine.train_models()

# Get recommendations
recommendations = engine.get_recommendations('user_1', algorithm='hybrid', n_recommendations=5)
print(f"Recommendations: {recommendations}")

# Save model
engine.save_model('recommendation_model.pkl')
```

### 10. Integration with Your Application

#### 10.1 FastAPI Integration
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="Recommendation API")

# Data models
class RecommendationRequest(BaseModel):
    user_id: str
    algorithm: str = "hybrid"
    n_recommendations: int = 5

class RecommendationResponse(BaseModel):
    user_id: str
    recommendations: list
    algorithm: str

# Initialize recommendation engine
engine = RecommendationEngine()

@app.post("/recommendations", response_model=RecommendationResponse)
async def get_recommendations(request: RecommendationRequest):
    try:
        recommendations = engine.get_recommendations(
            request.user_id,
            algorithm=request.algorithm,
            n_recommendations=request.n_recommendations
        )
        
        return RecommendationResponse(
            user_id=request.user_id,
            recommendations=recommendations,
            algorithm=request.algorithm
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/train")
async def train_models(user_behaviors: list, product_data: list):
    try:
        engine.prepare_data(user_behaviors, product_data)
        engine.train_models()
        return {"message": "Models trained successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 11. Performance Optimization

#### 11.1 Caching Recommendations
```python
import redis
import json

class CachedRecommendationEngine(RecommendationEngine):
    def __init__(self, redis_url="redis://localhost:6379"):
        super().__init__()
        self.redis_client = redis.from_url(redis_url)
        self.cache_ttl = 3600  # 1 hour
        
    def get_recommendations(self, user_id, algorithm='hybrid', n_recommendations=5):
        # Check cache first
        cache_key = f"recommendations:{user_id}:{algorithm}:{n_recommendations}"
        cached_result = self.redis_client.get(cache_key)
        
        if cached_result:
            return json.loads(cached_result)
        
        # Get fresh recommendations
        recommendations = super().get_recommendations(user_id, algorithm, n_recommendations)
        
        # Cache the result
        self.redis_client.setex(cache_key, self.cache_ttl, json.dumps(recommendations))
        
        return recommendations
```

### 12. Monitoring and Evaluation

#### 12.1 Model Performance Tracking
```python
import time
from datetime import datetime

class MonitoredRecommendationEngine(RecommendationEngine):
    def __init__(self):
        super().__init__()
        self.performance_metrics = []
        
    def get_recommendations(self, user_id, algorithm='hybrid', n_recommendations=5):
        start_time = time.time()
        
        try:
            recommendations = super().get_recommendations(user_id, algorithm, n_recommendations)
            
            # Record performance metrics
            execution_time = time.time() - start_time
            self.performance_metrics.append({
                'timestamp': datetime.now(),
                'user_id': user_id,
                'algorithm': algorithm,
                'execution_time': execution_time,
                'recommendations_count': len(recommendations),
                'success': True
            })
            
            return recommendations
            
        except Exception as e:
            # Record error metrics
            self.performance_metrics.append({
                'timestamp': datetime.now(),
                'user_id': user_id,
                'algorithm': algorithm,
                'execution_time': time.time() - start_time,
                'error': str(e),
                'success': False
            })
            raise
    
    def get_performance_summary(self):
        """Get performance summary"""
        if not self.performance_metrics:
            return {}
            
        successful_requests = [m for m in self.performance_metrics if m['success']]
        failed_requests = [m for m in self.performance_metrics if not m['success']]
        
        return {
            'total_requests': len(self.performance_metrics),
            'successful_requests': len(successful_requests),
            'failed_requests': len(failed_requests),
            'success_rate': len(successful_requests) / len(self.performance_metrics),
            'average_execution_time': np.mean([m['execution_time'] for m in successful_requests]),
            'algorithm_distribution': pd.Series([m['algorithm'] for m in self.performance_metrics]).value_counts().to_dict()
        }
```

This comprehensive guide provides everything you need to implement a recommendation system using Python and scikit-learn, even with no prior ML experience. The code is beginner-friendly and includes practical examples for real-world implementation.
