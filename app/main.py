from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import NMF
import pickle
import json
import redis
import time
from datetime import datetime
import logging

# Import database module
from database import db_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Magento Recommendation API",
    description="Personalized product recommendations for Magento",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class UserBehavior(BaseModel):
    user_id: str
    product_id: str
    behavior_type: str  # view, cart, purchase, wishlist
    timestamp: Optional[str] = None
    session_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class ProductData(BaseModel):
    product_id: str
    name: str
    category: str
    subcategory: Optional[str] = None
    price: Optional[float] = None
    attributes: Optional[Dict[str, Any]] = None

class RecommendationRequest(BaseModel):
    user_id: str
    algorithm: str = "hybrid"  # user_based, content_based, hybrid
    n_recommendations: int = 5
    category_filter: Optional[str] = None

class RecommendationResponse(BaseModel):
    user_id: str
    recommendations: List[Dict[str, Any]]
    algorithm: str
    generated_at: str
    execution_time: float

class TrainingRequest(BaseModel):
    user_behaviors: List[UserBehavior]
    product_data: List[ProductData]

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str
    services: Dict[str, str]

# Global recommendation engine
class RecommendationEngine:
    def __init__(self):
        self.user_based_model = None
        self.content_based_model = None
        self.user_item_matrix = None
        self.product_data = None
        self.is_trained = False
        self.redis_client = None
        
        # Try to connect to Redis
        try:
            self.redis_client = redis.from_url("redis://redis:6379", decode_responses=True)
            logger.info("Connected to Redis")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}")
    
    def prepare_data(self, user_behaviors: List[UserBehavior], product_data: List[ProductData]):
        """Prepare data for training"""
        logger.info("Preparing data for training...")
        
        # Convert behaviors to DataFrame
        behaviors_df = pd.DataFrame([behavior.dict() for behavior in user_behaviors])
        
        # Create user-item matrix
        self.user_item_matrix = behaviors_df.pivot_table(
            index='user_id',
            columns='product_id',
            values='behavior_type',
            aggfunc='count',
            fill_value=0
        )
        
        # Prepare product data
        self.product_data = pd.DataFrame([product.dict() for product in product_data])
        
        logger.info(f"Data prepared: {len(self.user_item_matrix)} users, {len(self.product_data)} products")
    
    def prepare_data_from_db(self):
        """Prepare data from database for training"""
        logger.info("Loading data from database for training...")
        
        # Get behaviors from database
        behaviors = db_manager.get_all_behaviors(limit=10000)
        if not behaviors:
            logger.warning("No behaviors found in database")
            return False
        
        # Convert to DataFrame
        behaviors_df = pd.DataFrame(behaviors)
        
        # Create user-item matrix
        self.user_item_matrix = behaviors_df.pivot_table(
            index='user_id',
            columns='product_id',
            values='behavior_type',
            aggfunc='count',
            fill_value=0
        )
        
        # Get products from database
        products = db_manager.get_all_products()
        if not products:
            logger.warning("No products found in database")
            return False
        
        # Prepare product data
        self.product_data = pd.DataFrame(products)
        
        logger.info(f"Data prepared from DB: {len(self.user_item_matrix)} users, {len(self.product_data)} products")
        return True
    
    def train_models(self):
        """Train all recommendation models"""
        logger.info("Training recommendation models...")
        
        try:
            # Train user-based model
            self.user_based_model = cosine_similarity(self.user_item_matrix)
            
            # Train content-based model
            product_descriptions = self.product_data['name'] + ' ' + self.product_data['category']
            tfidf = TfidfVectorizer(stop_words='english', max_features=1000)
            product_features = tfidf.fit_transform(product_descriptions)
            self.content_based_model = cosine_similarity(product_features)
            
            # Train matrix factorization model
            n_components = min(20, min(self.user_item_matrix.shape))
            self.mf_model = NMF(n_components=n_components, random_state=42)
            self.user_factors = self.mf_model.fit_transform(self.user_item_matrix)
            self.item_factors = self.mf_model.components_
            
            self.is_trained = True
            logger.info("Models trained successfully")
            
        except Exception as e:
            logger.error(f"Error training models: {e}")
            raise
    
    def get_trending_products(self, category: Optional[str] = None, limit: int = 10, timeframe_days: int = 7):
        """Get trending products based on recent behavior"""
        logger.info(f"Getting trending products - category: {category}, limit: {limit}, timeframe: {timeframe_days} days")
        
        try:
            # Get recent behaviors from database
            recent_behaviors = db_manager.get_recent_behaviors(days=timeframe_days)
            
            if not recent_behaviors:
                logger.warning("No recent behaviors found for trending products")
                return []
            
            # Calculate trending scores
            trending_scores = {}
            
            for behavior in recent_behaviors:
                product_id = behavior['product_id']
                behavior_type = behavior['behavior_type']
                
                # Weight different behavior types
                weights = {
                    'purchase': 3.0,
                    'cart': 2.0,
                    'wishlist': 1.5,
                    'view': 1.0
                }
                
                weight = weights.get(behavior_type, 1.0)
                
                if product_id not in trending_scores:
                    trending_scores[product_id] = 0
                
                trending_scores[product_id] += weight
            
            # Sort by score
            sorted_products = sorted(trending_scores.items(), key=lambda x: x[1], reverse=True)
            
            # Filter by category if specified
            if category:
                filtered_products = []
                for product_id, score in sorted_products:
                    product = self.product_data[self.product_data['product_id'] == product_id]
                    if not product.empty and product.iloc[0]['category'] == category:
                        filtered_products.append((product_id, score))
                sorted_products = filtered_products
            
            # Get top trending products
            trending_product_ids = [product_id for product_id, score in sorted_products[:limit]]
            
            # Add product details
            trending_products = self._add_product_details(trending_product_ids)
            
            # Add trending scores
            for product in trending_products:
                product_id = product['product_id']
                score = trending_scores.get(product_id, 0)
                product['trending_score'] = score
                product['trending_rank'] = sorted_products.index((product_id, score)) + 1
            
            logger.info(f"Found {len(trending_products)} trending products")
            return trending_products
            
        except Exception as e:
            logger.error(f"Error getting trending products: {e}")
            return []
    
    def get_recommendations(self, user_id: str, algorithm: str = "hybrid", n_recommendations: int = 5, category_filter: Optional[str] = None):
        """Get recommendations using specified algorithm"""
        if not self.is_trained:
            raise ValueError("Models must be trained before getting recommendations")
        
        start_time = time.time()
        
        try:
            if algorithm == "user_based":
                recommendations = self._get_user_based_recommendations(user_id, n_recommendations)
            elif algorithm == "content_based":
                recommendations = self._get_content_based_recommendations(user_id, n_recommendations)
            elif algorithm == "hybrid":
                recommendations = self._get_hybrid_recommendations(user_id, n_recommendations)
            else:
                raise ValueError(f"Unknown algorithm: {algorithm}")
            
            # Apply category filter if specified
            if category_filter:
                recommendations = self._filter_by_category(recommendations, category_filter)
            
            # Add product details to recommendations
            recommendations_with_details = self._add_product_details(recommendations)
            
            # Save recommendations to database
            for rec in recommendations_with_details:
                db_manager.save_recommendation(
                    user_id=user_id,
                    product_id=rec["product_id"],
                    score=rec.get("score", 0.8),
                    algorithm=algorithm
                )
            
            execution_time = time.time() - start_time
            
            return {
                "recommendations": recommendations_with_details,
                "algorithm": algorithm,
                "execution_time": execution_time
            }
            
        except Exception as e:
            logger.error(f"Error getting recommendations: {e}")
            raise
    
    def _get_user_based_recommendations(self, user_id: str, n_recommendations: int):
        """User-based collaborative filtering"""
        if user_id not in self.user_item_matrix.index:
            return []
        
        user_idx = self.user_item_matrix.index.get_loc(user_id)
        similar_users = self.user_based_model[user_idx]
        similar_user_indices = np.argsort(similar_users)[::-1][1:6]  # Top 5 similar users
        
        recommendations = []
        user_products = set(self.user_item_matrix.columns[self.user_item_matrix.iloc[user_idx] > 0])
        
        for similar_user_idx in similar_user_indices:
            similar_user_products = set(self.user_item_matrix.columns[self.user_item_matrix.iloc[similar_user_idx] > 0])
            new_products = similar_user_products - user_products
            recommendations.extend(list(new_products))
        
        return list(set(recommendations))[:n_recommendations]
    
    def _get_content_based_recommendations(self, user_id: str, n_recommendations: int):
        """Content-based filtering"""
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
    
    def _get_hybrid_recommendations(self, user_id: str, n_recommendations: int):
        """Hybrid approach combining multiple methods"""
        user_recs = self._get_user_based_recommendations(user_id, n_recommendations)
        content_recs = self._get_content_based_recommendations(user_id, n_recommendations)
        
        # Combine and rank
        all_recs = user_recs + content_recs
        from collections import Counter
        rec_counts = Counter(all_recs)
        
        return [rec for rec, count in rec_counts.most_common(n_recommendations)]
    
    def _filter_by_category(self, recommendations: List[str], category: str):
        """Filter recommendations by category"""
        filtered = []
        for product_id in recommendations:
            product = self.product_data[self.product_data['product_id'] == product_id]
            if not product.empty and product.iloc[0]['category'] == category:
                filtered.append(product_id)
        return filtered
    
    def _add_product_details(self, recommendations: List[str]):
        """Add product details to recommendations"""
        details = []
        for product_id in recommendations:
            product = self.product_data[self.product_data['product_id'] == product_id]
            if not product.empty:
                details.append({
                    "product_id": product_id,
                    "name": product.iloc[0]['name'],
                    "category": product.iloc[0]['category'],
                    "price": product.iloc[0].get('price'),
                    "score": 0.8  # Placeholder score
                })
        return details
    
    def save_model(self, filepath: str):
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
        logger.info(f"Model saved to {filepath}")
    
    def load_model(self, filepath: str):
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
        logger.info(f"Model loaded from {filepath}")

# Initialize recommendation engine
engine = RecommendationEngine()

# API Endpoints
@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint"""
    return {"message": "Magento Recommendation API", "version": "1.0.0"}

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    services = {
        "api": "healthy",
        "recommendation_engine": "ready" if engine.is_trained else "not_trained"
    }
    
    # Check database connection
    if db_manager.test_connection():
        services["database"] = "connected"
    else:
        services["database"] = "disconnected"
    
    # Check Redis connection
    if engine.redis_client:
        try:
            engine.redis_client.ping()
            services["redis"] = "connected"
        except:
            services["redis"] = "disconnected"
    else:
        services["redis"] = "not_configured"
    
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version="1.0.0",
        services=services
    )

@app.post("/train")
async def train_models(request: TrainingRequest):
    """Train recommendation models"""
    try:
        engine.prepare_data(request.user_behaviors, request.product_data)
        engine.train_models()
        
        # Save model
        engine.save_model("/app/models/recommendation_model.pkl")
        
        return {
            "message": "Models trained successfully",
            "users_count": len(engine.user_item_matrix),
            "products_count": len(engine.product_data),
            "model_saved": True
        }
    except Exception as e:
        logger.error(f"Training error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/train/from-db")
async def train_models_from_db():
    """Train recommendation models from database data"""
    try:
        success = engine.prepare_data_from_db()
        if not success:
            raise HTTPException(status_code=400, detail="No data available in database")
        
        engine.train_models()
        
        # Save model
        engine.save_model("/app/models/recommendation_model.pkl")
        
        return {
            "message": "Models trained successfully from database",
            "users_count": len(engine.user_item_matrix),
            "products_count": len(engine.product_data),
            "model_saved": True
        }
    except Exception as e:
        logger.error(f"Training from DB error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/recommendations", response_model=RecommendationResponse)
async def get_recommendations(request: RecommendationRequest):
    """Get personalized recommendations"""
    try:
        # Check cache first
        cache_key = f"recommendations:{request.user_id}:{request.algorithm}:{request.n_recommendations}"
        cached_result = None
        
        if engine.redis_client:
            try:
                cached_result = engine.redis_client.get(cache_key)
                if cached_result:
                    cached_data = json.loads(cached_result)
                    cached_data["generated_at"] = datetime.now().isoformat()
                    return RecommendationResponse(**cached_data)
            except Exception as e:
                logger.warning(f"Cache error: {e}")
        
        # Get fresh recommendations
        result = engine.get_recommendations(
            request.user_id,
            algorithm=request.algorithm,
            n_recommendations=request.n_recommendations,
            category_filter=request.category_filter
        )
        
        # Cache the result
        if engine.redis_client:
            try:
                cache_data = {
                    "user_id": request.user_id,
                    "recommendations": result["recommendations"],
                    "algorithm": result["algorithm"],
                    "generated_at": datetime.now().isoformat(),
                    "execution_time": result["execution_time"]
                }
                engine.redis_client.setex(cache_key, 3600, json.dumps(cache_data))  # Cache for 1 hour
            except Exception as e:
                logger.warning(f"Cache save error: {e}")
        
        return RecommendationResponse(
            user_id=request.user_id,
            recommendations=result["recommendations"],
            algorithm=result["algorithm"],
            generated_at=datetime.now().isoformat(),
            execution_time=result["execution_time"]
        )
        
    except Exception as e:
        logger.error(f"Recommendation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/trending-products", response_model=List[Dict[str, Any]])
async def get_trending_products(category: Optional[str] = None, limit: int = 10, timeframe_days: int = 7):
    """Get trending products based on recent user behavior"""
    try:
        trending_products = engine.get_trending_products(category=category, limit=limit, timeframe_days=timeframe_days)
        return trending_products
    except Exception as e:
        logger.error(f"Trending products error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/behaviors")
async def track_behavior(behavior: UserBehavior):
    """Track user behavior"""
    try:
        # Save behavior to database
        behavior_data = {
            "user_id": behavior.user_id,
            "product_id": behavior.product_id,
            "behavior_type": behavior.behavior_type,
            "session_id": behavior.session_id,
            "timestamp": behavior.timestamp,
            "metadata": behavior.metadata
        }
        
        success = db_manager.save_user_behavior(behavior_data)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to save behavior")
        
        logger.info(f"Behavior tracked: {behavior.user_id} -> {behavior.product_id} ({behavior.behavior_type})")
        
        return {
            "message": "Behavior tracked successfully",
            "user_id": behavior.user_id,
            "product_id": behavior.product_id,
            "behavior_type": behavior.behavior_type
        }
    except Exception as e:
        logger.error(f"Behavior tracking error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/behaviors/{user_id}")
async def get_user_behaviors(user_id: str, limit: int = 100):
    """Get user behaviors"""
    try:
        behaviors = db_manager.get_user_behaviors(user_id, limit)
        return {
            "user_id": user_id,
            "behaviors": behaviors,
            "count": len(behaviors)
        }
    except Exception as e:
        logger.error(f"Error getting user behaviors: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/users/{user_id}/stats")
async def get_user_stats(user_id: str):
    """Get user statistics"""
    try:
        stats = db_manager.get_user_stats(user_id)
        return stats
    except Exception as e:
        logger.error(f"Error getting user stats: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/models/status")
async def model_status():
    """Get model training status"""
    return {
        "is_trained": engine.is_trained,
        "users_count": len(engine.user_item_matrix) if engine.user_item_matrix is not None else 0,
        "products_count": len(engine.product_data) if engine.product_data is not None else 0,
        "algorithms_available": ["user_based", "content_based", "hybrid"]
    }

@app.post("/models/load")
async def load_model():
    """Load pre-trained model"""
    try:
        engine.load_model("/app/models/recommendation_model.pkl")
        return {"message": "Model loaded successfully", "is_trained": engine.is_trained}
    except Exception as e:
        logger.error(f"Model loading error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
