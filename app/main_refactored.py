from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
import json
from datetime import datetime
from typing import Dict, List, Any

# Import services
from recommendation_service import RecommendationService
from behavior_service import BehaviorService
from health_service import HealthService

# Import models
from models import (
    RecommendationRequest, RecommendationResponse,
    TrainingRequest, UserBehavior, HealthResponse
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize services
recommendation_service = RecommendationService()
behavior_service = BehaviorService()
health_service = HealthService()

# Create FastAPI app
app = FastAPI(
    title="Magento Recommendation API",
    description="Personalized product recommendations for Magento e-commerce platforms",
    version="1.0.0",
    contact={
        "name": "J S JAIMOHAN",
        "email": "jsjaimohan@gmail.com",
    },
    license_info={
        "name": "Private License",
        "url": "https://github.com/your-repo/LICENSE",
    },
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health endpoints
@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint"""
    return health_service.get_root_info()

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(**health_service.get_health_status())

# Recommendation endpoints
@app.post("/train")
async def train_models(request: TrainingRequest):
    """Train recommendation models"""
    try:
        recommendation_service.prepare_data(request.user_behaviors, request.product_data)
        recommendation_service.train_models()
        
        # Save model
        recommendation_service.save_model("/app/models/recommendation_model.pkl")
        
        return {
            "message": "Models trained successfully",
            "users_count": len(recommendation_service.user_item_matrix),
            "products_count": len(recommendation_service.product_data),
            "model_saved": True
        }
    except Exception as e:
        logger.error(f"Training error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/train/from-db")
async def train_models_from_db():
    """Train recommendation models from database data"""
    try:
        success = recommendation_service.prepare_data_from_db()
        if not success:
            raise HTTPException(status_code=400, detail="No data available in database")
        
        recommendation_service.train_models()
        
        # Save model
        recommendation_service.save_model("/app/models/recommendation_model.pkl")
        
        return {
            "message": "Models trained successfully from database",
            "users_count": len(recommendation_service.user_item_matrix),
            "products_count": len(recommendation_service.product_data),
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
        
        if recommendation_service.redis_client:
            try:
                cached_result = recommendation_service.redis_client.get(cache_key)
                if cached_result:
                    cached_data = json.loads(cached_result)
                    cached_data["generated_at"] = datetime.now().isoformat()
                    return RecommendationResponse(**cached_data)
            except Exception as e:
                logger.warning(f"Cache error: {e}")
        
        # Get fresh recommendations
        result = recommendation_service.get_recommendations(
            request.user_id,
            algorithm=request.algorithm,
            n_recommendations=request.n_recommendations,
            category_filter=request.category_filter
        )
        
        # Cache the result
        if recommendation_service.redis_client:
            try:
                cache_data = {
                    "user_id": request.user_id,
                    "recommendations": result["recommendations"],
                    "algorithm": result["algorithm"],
                    "generated_at": datetime.now().isoformat(),
                    "execution_time": result["execution_time"]
                }
                recommendation_service.redis_client.setex(
                    cache_key, 3600, json.dumps(cache_data)
                )  # Cache for 1 hour
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
async def get_trending_products(category: str = None, limit: int = 10, timeframe_days: int = 7):
    """Get trending products based on recent user behavior"""
    try:
        trending_products = recommendation_service.get_trending_products(
            category=category, limit=limit, timeframe_days=timeframe_days
        )
        return trending_products
    except Exception as e:
        logger.error(f"Trending products error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/models/status")
async def model_status():
    """Get model training status"""
    return recommendation_service.get_model_status()

@app.post("/models/load")
async def load_model():
    """Load pre-trained model"""
    try:
        recommendation_service.load_model("/app/models/recommendation_model.pkl")
        return {"message": "Model loaded successfully", "is_trained": recommendation_service.is_trained}
    except Exception as e:
        logger.error(f"Model loading error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

# Behavior endpoints
@app.post("/behaviors")
async def track_behavior(behavior: UserBehavior):
    """Track user behavior"""
    try:
        result = behavior_service.track_behavior(behavior)
        return result
    except Exception as e:
        logger.error(f"Behavior tracking error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/behaviors/{user_id}")
async def get_user_behaviors(user_id: str, limit: int = 100):
    """Get user behaviors"""
    try:
        result = behavior_service.get_user_behaviors(user_id, limit)
        return result
    except Exception as e:
        logger.error(f"Error getting user behaviors: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/users/{user_id}/stats")
async def get_user_stats(user_id: str):
    """Get user statistics"""
    try:
        stats = behavior_service.get_user_stats(user_id)
        return stats
    except Exception as e:
        logger.error(f"Error getting user stats: {e}")
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
