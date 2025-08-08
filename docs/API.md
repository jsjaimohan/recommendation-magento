# API Documentation

**Developer:** J S JAIMOHAN  
**Email:** jsjaimohan@gmail.com  
**License:** Private License

## Base URL
```
http://localhost:8000
```

## Authentication
For sensitive endpoints, include the API key in headers:
```
X-API-Key: magento-recommendation-key-2024
```

## Rate Limiting
- **User Stats Endpoint:** 10 requests per minute per user
- **Other Endpoints:** No rate limiting currently

## Response Format
All responses are in JSON format with the following structure:
```json
{
  "status": "success|error",
  "data": {...},
  "message": "Optional message"
}
```

## Health Endpoints

### GET /
**Root endpoint with basic information**
```bash
curl http://localhost:8000/
```
**Response:**
```json
{
  "message": "Magento Recommendation API",
  "version": "1.0.0",
  "developer": "J S JAIMOHAN",
  "email": "jsjaimohan@gmail.com",
  "license": "Private License"
}
```

### GET /health
**Health check endpoint**
```bash
curl http://localhost:8000/health
```
**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0",
  "services": {
    "database": "connected",
    "redis": "connected",
    "ml_engine": "ready"
  }
}
```

## Machine Learning Endpoints

### POST /train
**Train recommendation models with provided data**
```bash
curl -X POST http://localhost:8000/train \
  -H "Content-Type: application/json" \
  -d '{
    "user_behaviors": [
      {
        "user_id": "user_001",
        "product_id": "PROD001",
        "behavior_type": "purchase",
        "timestamp": "2024-01-15T10:30:00Z"
      }
    ],
    "product_data": [
      {
        "product_id": "PROD001",
        "name": "iPhone 15 Pro",
        "category": "electronics",
        "price": 999.99
      }
    ]
  }'
```

### POST /train/from-db
**Train models using data from database**
```bash
curl -X POST http://localhost:8000/train/from-db
```

## Recommendation Endpoints

### POST /recommendations
**Get personalized recommendations**
```bash
curl -X POST http://localhost:8000/recommendations \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_001",
    "algorithm": "hybrid",
    "n_recommendations": 5,
    "category_filter": "electronics"
  }'
```
**Response:**
```json
{
  "user_id": "user_001",
  "recommendations": [
    {
      "product_id": "PROD002",
      "product_name": "Samsung Galaxy S24",
      "score": 0.85,
      "reason": "Based on your purchase history"
    }
  ],
  "algorithm": "hybrid",
  "generated_at": "2024-01-15T10:30:00Z",
  "execution_time": 0.15
}
```

### POST /trending-products
**Get trending products**
```bash
curl -X POST http://localhost:8000/trending-products \
  -H "Content-Type: application/json" \
  -d '{
    "category": "electronics",
    "limit": 10,
    "timeframe_days": 7
  }'
```

## Behavior Tracking Endpoints

### POST /behaviors
**Track user behavior**
```bash
curl -X POST http://localhost:8000/behaviors \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_001",
    "product_id": "PROD001",
    "behavior_type": "view",
    "session_id": "session_123",
    "metadata": {
      "page": "product_detail",
      "duration": 30
    }
  }'
```

### GET /behaviors/{user_id}
**Get user behaviors**
```bash
curl http://localhost:8000/behaviors/user_001?limit=100
```

## Secured Endpoints

### GET /users/{user_id}/stats
**Get user statistics (requires API key)**
```bash
curl http://localhost:8000/users/user_001/stats \
  -H "X-API-Key: magento-recommendation-key-2024"
```
**Response:**
```json
{
  "user_id": "user_001",
  "total_interactions": 25,
  "unique_products": 8,
  "recent_activity_7_days": 5,
  "behavior_summary": {
    "view_count": 15,
    "cart_count": 5,
    "purchase_count": 3,
    "wishlist_count": 2
  }
}
```

## Model Management Endpoints

### GET /models/status
**Check model training status**
```bash
curl http://localhost:8000/models/status
```

### POST /models/load
**Load trained models**
```bash
curl -X POST http://localhost:8000/models/load
```

## FBT (Frequently Bought Together) Endpoints

### POST /transactions/purchase
**Track a complete purchase transaction for FBT analysis**
```bash
curl -X POST http://localhost:8000/transactions/purchase \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_001",
    "order_id": "ORDER_12345",
    "products": [
      {
        "product_id": "PROD001",
        "quantity": 1,
        "unit_price": 999.99,
        "total_price": 999.99
      },
      {
        "product_id": "PROD005",
        "quantity": 1,
        "unit_price": 249.99,
        "total_price": 249.99
      }
    ],
    "total_amount": 1249.98,
    "status": "completed"
  }'
```
**Response:**
```json
{
  "message": "Purchase transaction tracked successfully",
  "user_id": "user_001",
  "order_id": "ORDER_12345",
  "transaction_id": "txn_ORDER_12345_1705312200",
  "products_count": 2,
  "total_amount": 1249.98,
  "execution_time": 0.05
}
```

### POST /fbt/generate
**Generate association rules for Frequently Bought Together**
```bash
curl -X POST http://localhost:8000/fbt/generate \
  -H "Content-Type: application/json" \
  -d '{
    "min_support": 0.01,
    "min_confidence": 0.3,
    "clear_existing": true
  }'
```
**Response:**
```json
{
  "status": "success",
  "rules_generated": 15,
  "transactions_processed": 250,
  "frequent_itemsets": 45,
  "min_support": 0.01,
  "min_confidence": 0.3,
  "execution_time": 2.34
}
```

### POST /fbt/recommendations
**Get frequently bought together products for a given product**
```bash
curl -X POST http://localhost:8000/fbt/recommendations \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "PROD001",
    "limit": 5,
    "min_confidence": 0.3
  }'
```
**Response:**
```json
{
  "product_id": "PROD001",
  "associations": [
    {
      "product_id": "PROD005",
      "product_name": "AirPods Pro",
      "category": "electronics",
      "price": 249.99,
      "support": 0.08,
      "confidence": 0.85,
      "lift": 3.2
    },
    {
      "product_id": "PROD013",
      "product_name": "iPhone Case",
      "category": "accessories",
      "price": 19.99,
      "support": 0.09,
      "confidence": 0.92,
      "lift": 4.1
    }
  ],
  "count": 2,
  "min_confidence": 0.3,
  "execution_time": 0.02
}
```

### GET /fbt/rules
**Get all association rules for analysis**
```bash
curl "http://localhost:8000/fbt/rules?min_confidence=0.3&limit=1000"
```
**Response:**
```json
{
  "rules": [
    {
      "product_id": "PROD001",
      "associated_product_id": "PROD005",
      "product_name": "iPhone 15 Pro",
      "associated_product_name": "AirPods Pro",
      "support": 0.08,
      "confidence": 0.85,
      "lift": 3.2
    }
  ],
  "count": 15,
  "min_confidence": 0.3,
  "execution_time": 0.05
}
```

### DELETE /fbt/rules
**Clear all association rules (useful for regeneration)**
```bash
curl -X DELETE http://localhost:8000/fbt/rules
```
**Response:**
```json
{
  "status": "success",
  "message": "Association rules cleared"
}
```

### GET /transactions
**Get purchase transactions for analysis**
```bash
curl "http://localhost:8000/transactions?user_id=user_001&limit=100"
```
**Response:**
```json
{
  "transactions": [
    {
      "transaction_id": "txn_ORDER_12345_1705312200",
      "user_id": "user_001",
      "order_id": "ORDER_12345",
      "purchase_date": "2024-01-15T10:30:00Z",
      "total_amount": 1249.98,
      "status": "completed",
      "items": [
        {
          "product_id": "PROD001",
          "quantity": 1,
          "unit_price": 999.99,
          "total_price": 999.99
        },
        {
          "product_id": "PROD005",
          "quantity": 1,
          "unit_price": 249.99,
          "total_price": 249.99
        }
      ]
    }
  ],
  "count": 1,
  "user_id": "user_001"
}
```

## Error Handling

### Common Error Responses

**400 Bad Request:**
```json
{
  "detail": "Invalid user ID format"
}
```

**401 Unauthorized:**
```json
{
  "detail": "API key required for accessing user statistics"
}
```

**429 Too Many Requests:**
```json
{
  "detail": "Rate limit exceeded. Try again later."
}
```

**500 Internal Server Error:**
```json
{
  "message": "Training failed. Please check your data and try again.",
  "status": "error"
}
```

## Usage Examples

### Python Example
```python
import requests

# Track purchase transaction
transaction_data = {
    "user_id": "user_001",
    "order_id": "ORDER_12345",
    "products": [
        {
            "product_id": "PROD001",
            "quantity": 1,
            "unit_price": 999.99,
            "total_price": 999.99
        }
    ],
    "total_amount": 999.99
}

response = requests.post(
    "http://localhost:8000/transactions/purchase",
    json=transaction_data
)
print(response.json())

# Generate FBT rules
fbt_data = {
    "min_support": 0.01,
    "min_confidence": 0.3,
    "clear_existing": True
}

response = requests.post(
    "http://localhost:8000/fbt/generate",
    json=fbt_data
)
print(response.json())

# Get FBT recommendations
fbt_request = {
    "product_id": "PROD001",
    "limit": 5,
    "min_confidence": 0.3
}

response = requests.post(
    "http://localhost:8000/fbt/recommendations",
    json=fbt_request
)
print(response.json())
```

### JavaScript Example
```javascript
// Track purchase transaction
const transactionData = {
  user_id: "user_001",
  order_id: "ORDER_12345",
  products: [
    {
      product_id: "PROD001",
      quantity: 1,
      unit_price: 999.99,
      total_price: 999.99
    }
  ],
  total_amount: 999.99
};

fetch('http://localhost:8000/transactions/purchase', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify(transactionData)
})
.then(response => response.json())
.then(data => console.log(data));

// Generate FBT rules
const fbtData = {
  min_support: 0.01,
  min_confidence: 0.3,
  clear_existing: true
};

fetch('http://localhost:8000/fbt/generate', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify(fbtData)
})
.then(response => response.json())
.then(data => console.log(data));
```

## FBT Algorithm Details

### Association Rules Metrics

**Support:** How often the itemset appears in transactions
- Formula: `Support(X,Y) = Count(X,Y) / Total_Transactions`
- Example: If iPhone + AirPods appear in 80 out of 1000 transactions, support = 0.08

**Confidence:** How likely Y is bought when X is bought
- Formula: `Confidence(X→Y) = Support(X,Y) / Support(X)`
- Example: If 80% of iPhone buyers also buy AirPods, confidence = 0.8

**Lift:** How much more likely the rule is compared to random chance
- Formula: `Lift(X→Y) = Confidence(X→Y) / Support(Y)`
- Example: If lift = 3.2, the combination is 3.2x more likely than random

### Recommended Parameters

**For Small Datasets (< 1000 transactions):**
- `min_support`: 0.05 (5%)
- `min_confidence`: 0.3 (30%)

**For Medium Datasets (1000-10000 transactions):**
- `min_support`: 0.01 (1%)
- `min_confidence`: 0.3 (30%)

**For Large Datasets (> 10000 transactions):**
- `min_support`: 0.005 (0.5%)
- `min_confidence`: 0.2 (20%)

## Performance Considerations

1. **Rule Generation:** Can take 1-5 minutes for large datasets
2. **Recommendation Retrieval:** Typically < 100ms
3. **Transaction Tracking:** < 50ms per transaction
4. **Database Storage:** Optimized with proper indexes

## Security Notes

1. **API Key Protection:** Sensitive endpoints require valid API key
2. **Input Validation:** All user inputs are validated and sanitized
3. **Rate Limiting:** Applied to sensitive endpoints
4. **Error Handling:** Stack traces are not exposed to external users
