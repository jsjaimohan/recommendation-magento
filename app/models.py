from pydantic import BaseModel
from typing import List, Optional, Dict, Any

# Request Models
class UserBehavior(BaseModel):
    user_id: str
    product_id: str
    behavior_type: str  # view, cart, purchase, wishlist
    timestamp: Optional[str] = None
    session_id: Optional[str] = None
    transaction_id: Optional[str] = None  # NEW: For FBT tracking
    metadata: Optional[Dict[str, Any]] = None

class ProductData(BaseModel):
    product_id: str
    name: str
    category: str
    subcategory: Optional[str] = None
    price: Optional[float] = None
    attributes: Optional[Dict[str, Any]] = None

class ProductCreateRequest(BaseModel):
    product_id: str
    name: str
    category: str
    subcategory: Optional[str] = None
    price: Optional[float] = None
    attributes: Optional[Dict[str, Any]] = None
    description: Optional[str] = None
    brand: Optional[str] = None
    tags: Optional[List[str]] = None

class ProductUpdateRequest(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    price: Optional[float] = None
    attributes: Optional[Dict[str, Any]] = None
    description: Optional[str] = None
    brand: Optional[str] = None
    tags: Optional[List[str]] = None

class ProductResponse(BaseModel):
    product_id: str
    name: str
    category: str
    subcategory: Optional[str] = None
    price: Optional[float] = None
    attributes: Optional[Dict[str, Any]] = None
    description: Optional[str] = None
    brand: Optional[str] = None
    tags: Optional[List[str]] = None
    created_at: str
    updated_at: str
    message: str
    status: str

class RecommendationRequest(BaseModel):
    user_id: str
    algorithm: str = "hybrid"  # user_based, content_based, hybrid
    n_recommendations: int = 5
    category_filter: Optional[str] = None

class TrainingRequest(BaseModel):
    user_behaviors: List[UserBehavior]
    product_data: List[ProductData]

# FBT-SPECIFIC MODELS
class TransactionItem(BaseModel):
    product_id: str
    quantity: int = 1
    unit_price: float = 0.0
    total_price: float = 0.0

class PurchaseTransactionRequest(BaseModel):
    user_id: str
    order_id: str
    products: List[TransactionItem]
    total_amount: float
    status: str = "completed"

class FBTGenerationRequest(BaseModel):
    min_support: Optional[float] = 0.01
    min_confidence: Optional[float] = 0.3
    clear_existing: bool = False

class FBTRequest(BaseModel):
    product_id: str
    limit: int = 10
    min_confidence: float = 0.3

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

# FBT-SPECIFIC RESPONSE MODELS
class FBTGenerationResponse(BaseModel):
    status: str
    rules_generated: int
    transactions_processed: int
    frequent_itemsets: int
    min_support: float
    min_confidence: float
    execution_time: float
    message: Optional[str] = None

class FBTResponse(BaseModel):
    product_id: str
    associations: List[Dict[str, Any]]
    count: int
    min_confidence: float
    execution_time: float

class TransactionResponse(BaseModel):
    message: str
    user_id: str
    order_id: str
    transaction_id: str
    products_count: int
    total_amount: float
    execution_time: float

class AssociationRuleResponse(BaseModel):
    rules: List[Dict[str, Any]]
    count: int
    min_confidence: float
    execution_time: float
