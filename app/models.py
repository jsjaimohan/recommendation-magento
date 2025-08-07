from pydantic import BaseModel
from typing import List, Optional, Dict, Any

# Request Models
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

class TrainingRequest(BaseModel):
    user_behaviors: List[UserBehavior]
    product_data: List[ProductData]

# Response Models
class RecommendationResponse(BaseModel):
    user_id: str
    recommendations: List[Dict[str, Any]]
    algorithm: str
    generated_at: str
    execution_time: float

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str
    services: Dict[str, str]
