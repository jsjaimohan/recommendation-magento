from fastapi import FastAPI, HTTPException, Depends, Header, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
import json
import re
from datetime import datetime
from typing import Dict, List, Any, Optional

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

# Security configurations
ALLOWED_USER_ID_PATTERN = re.compile(r'^[a-zA-Z0-9_-]{1,50}$')
MAX_REQUESTS_PER_MINUTE = 10
request_counts = {}

def validate_user_id(user_id: str) -> bool:
    """Validate user ID format and prevent injection attacks"""
    if not user_id or len(user_id) > 50:
        return False
    return bool(ALLOWED_USER_ID_PATTERN.match(user_id))

def check_rate_limit(user_id: str) -> bool:
    """Simple rate limiting for user stats endpoint"""
    current_time = datetime.now().minute
    key = f"{user_id}_{current_time}"
    
    if key not in request_counts:
        request_counts[key] = 0
    
    if request_counts[key] >= MAX_REQUESTS_PER_MINUTE:
        return False
    
    request_counts[key] += 1
    return True

def validate_api_key(x_api_key: Optional[str] = Header(None)) -> bool:
    """Validate API key for sensitive endpoints"""
    # For internal Magento integration, you can set a simple API key
    # In production, use proper authentication
    if not x_api_key:
        return False
    
    # Simple validation - in production, use proper JWT or OAuth
    valid_keys = ["magento-recommendation-key-2024", "internal-api-key"]
    return x_api_key in valid_keys

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
        return {
            "message": "Training failed. Please check your data and try again.",
            "status": "error"
        }

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
        return {
            "message": "Database training failed. Please ensure data is available.",
            "status": "error"
        }

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
        logger.error(f"Recommendation error for user {request.user_id}: {e}")
        return {
            "user_id": request.user_id,
            "recommendations": [],
            "algorithm": request.algorithm,
            "generated_at": datetime.now().isoformat(),
            "execution_time": 0.0,
            "error": "Unable to generate recommendations at this time"
        }

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
        return []

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
        return {
            "message": "Model loading failed. Please ensure model file exists.",
            "is_trained": False,
            "status": "error"
        }

# Behavior endpoints
@app.post("/behaviors")
async def track_behavior(behavior: UserBehavior):
    """Track user behavior"""
    try:
        result = behavior_service.track_behavior(behavior)
        return result
    except Exception as e:
        logger.error(f"Behavior tracking error: {e}")
        return {
            "message": "Failed to track behavior. Please try again.",
            "status": "error"
        }

@app.get("/behaviors/{user_id}")
async def get_user_behaviors(user_id: str, limit: int = 100):
    """Get user behaviors"""
    try:
        # Input validation
        if not validate_user_id(user_id):
            raise HTTPException(status_code=400, detail="Invalid user ID format")
        
        if limit < 1 or limit > 1000:
            raise HTTPException(status_code=400, detail="Limit must be between 1 and 1000")
        
        result = behavior_service.get_user_behaviors(user_id, limit)
        return result
    except Exception as e:
        logger.error(f"Error getting user behaviors for {user_id}: {e}")
        return {
            "user_id": user_id,
            "behaviors": [],
            "count": 0,
            "error": "Unable to retrieve user behaviors at this time"
        }

@app.get("/users/{user_id}/stats")
async def get_user_stats(user_id: str, request: Request, x_api_key: Optional[str] = Header(None)):
    """Get user statistics - SECURED ENDPOINT"""
    try:
        # Security validations
        if not validate_user_id(user_id):
            raise HTTPException(status_code=400, detail="Invalid user ID format")
        
        # Rate limiting
        if not check_rate_limit(user_id):
            raise HTTPException(status_code=429, detail="Rate limit exceeded. Try again later.")
        
        # API key validation for sensitive data
        if not validate_api_key(x_api_key):
            raise HTTPException(
                status_code=401, 
                detail="API key required for accessing user statistics"
            )
        
        # Log access attempt for security monitoring
        logger.info(f"User stats accessed for user_id: {user_id} from IP: {request.client.host if hasattr(request, 'client') else 'unknown'}")
        
        stats = behavior_service.get_user_stats(user_id)
        
        # Sanitize sensitive data before returning
        sanitized_stats = {
            "user_id": stats.get("user_id"),
            "total_interactions": sum(stats.get("behavior_counts", {}).values()),
            "unique_products": stats.get("unique_products", 0),
            "recent_activity_7_days": stats.get("recent_activity_7_days", 0),
            "behavior_summary": {
                "view_count": stats.get("behavior_counts", {}).get("view", 0),
                "cart_count": stats.get("behavior_counts", {}).get("cart", 0),
                "purchase_count": stats.get("behavior_counts", {}).get("purchase", 0),
                "wishlist_count": stats.get("behavior_counts", {}).get("wishlist", 0)
            }
        }
        
        return sanitized_stats
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user stats for user_id {user_id}: {e}")
        # Don't expose internal error details to external users
        return {
            "user_id": user_id,
            "error": "Unable to retrieve user statistics at this time",
            "status": "error"
        }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
