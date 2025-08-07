# API Documentation

**Developer:** J S JAIMOHAN  
**Email:** jsjaimohan@gmail.com  
**License:** Private License

## Overview

This document provides comprehensive API documentation for the Magento Recommendation System, including all endpoints, request/response formats, authentication, and usage examples.

## 🔗 Base URLs

```
Development: http://localhost:8000
Production: https://api.recommendations.magento.com
```

## 🔐 Authentication

### API Key Authentication

For sensitive endpoints, API key authentication is required:

```bash
# Header format
X-API-Key: magento-recommendation-key-2024
```

**Valid API Keys:**
- `magento-recommendation-key-2024`
- `internal-api-key`

### Rate Limiting

- **General endpoints**: 100 requests per minute
- **User statistics**: 10 requests per minute per user
- **Model training**: 5 requests per minute

## 📊 Response Formats

### Success Response
```json
{
  "status": "success",
  "data": { ... },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Error Response
```json
{
  "status": "error",
  "message": "User-friendly error message",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## 🏥 Health Endpoints

### GET / - Root Endpoint

**Description**: Get basic API information

**Authentication**: None required

**Response**:
```json
{
  "message": "Magento Recommendation API",
  "version": "1.0.0",
  "developer": "J S JAIMOHAN",
  "email": "jsjaimohan@gmail.com",
  "license": "Private License"
}
```

### GET /health - Health Check

**Description**: Comprehensive system health check

**Authentication**: None required

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0",
  "services": {
    "api": "healthy",
    "recommendation_engine": "ready",
    "database": "connected",
    "redis": "connected"
  }
}
```

## 🧠 Machine Learning Endpoints

### POST /train - Train Models

**Description**: Train recommendation models with provided data

**Authentication**: None required

**Request Body**:
```json
{
  "user_behaviors": [
    {
      "user_id": "user_123",
      "product_id": "PROD001",
      "behavior_type": "purchase",
      "timestamp": "2024-01-15T10:30:00Z",
      "session_id": "sess_abc123",
      "metadata": {
        "page_url": "/product/PROD001",
        "referrer": "search"
      }
    }
  ],
  "product_data": [
    {
      "product_id": "PROD001",
      "name": "iPhone 15 Pro",
      "category": "electronics",
      "subcategory": "smartphones",
      "price": 999.99,
      "attributes": {
        "brand": "Apple",
        "color": "Titanium",
        "storage": "256GB"
      }
    }
  ]
}
```

**Response**:
```json
{
  "message": "Models trained successfully",
  "users_count": 20,
  "products_count": 15,
  "model_saved": true
}
```

### POST /train/from-db - Train from Database

**Description**: Train models using existing database data

**Authentication**: None required

**Response**:
```json
{
  "message": "Models trained successfully from database",
  "users_count": 25,
  "products_count": 18,
  "model_saved": true
}
```

### GET /models/status - Model Status

**Description**: Get current model training status

**Authentication**: None required

**Response**:
```json
{
  "is_trained": true,
  "users_count": 25,
  "products_count": 18,
  "algorithms_available": ["user_based", "content_based", "hybrid"]
}
```

### POST /models/load - Load Model

**Description**: Load pre-trained model from file

**Authentication**: None required

**Response**:
```json
{
  "message": "Model loaded successfully",
  "is_trained": true
}
```

## 🎯 Recommendation Endpoints

### POST /recommendations - Get Recommendations

**Description**: Get personalized product recommendations

**Authentication**: None required

**Request Body**:
```json
{
  "user_id": "user_123",
  "algorithm": "hybrid",
  "n_recommendations": 5,
  "category_filter": "electronics"
}
```

**Parameters**:
- `user_id` (string, required): User identifier
- `algorithm` (string, optional): Recommendation algorithm (`user_based`, `content_based`, `hybrid`)
- `n_recommendations` (integer, optional): Number of recommendations (1-20)
- `category_filter` (string, optional): Filter by product category

**Response**:
```json
{
  "user_id": "user_123",
  "recommendations": [
    {
      "product_id": "PROD002",
      "name": "Samsung Galaxy S24",
      "category": "electronics",
      "price": 899.99,
      "score": 0.85
    },
    {
      "product_id": "PROD003",
      "name": "MacBook Air M3",
      "category": "electronics",
      "price": 1199.99,
      "score": 0.78
    }
  ],
  "algorithm": "hybrid",
  "generated_at": "2024-01-15T10:30:00Z",
  "execution_time": 0.045
}
```

### POST /trending-products - Get Trending Products

**Description**: Get trending products based on recent user behavior

**Authentication**: None required

**Request Body**:
```json
{
  "category": "electronics",
  "limit": 10,
  "timeframe_days": 7
}
```

**Parameters**:
- `category` (string, optional): Filter by product category
- `limit` (integer, optional): Number of trending products (1-50)
- `timeframe_days` (integer, optional): Time window in days (1-30)

**Response**:
```json
[
  {
    "product_id": "PROD001",
    "name": "iPhone 15 Pro",
    "category": "electronics",
    "price": 999.99,
    "trending_score": 15.5,
    "trending_rank": 1
  },
  {
    "product_id": "PROD002",
    "name": "Samsung Galaxy S24",
    "category": "electronics",
    "price": 899.99,
    "trending_score": 12.3,
    "trending_rank": 2
  }
]
```

## 📊 Behavior Tracking Endpoints

### POST /behaviors - Track User Behavior

**Description**: Track user behavior for recommendation learning

**Authentication**: None required

**Request Body**:
```json
{
  "user_id": "user_123",
  "product_id": "PROD001",
  "behavior_type": "view",
  "session_id": "sess_abc123",
  "timestamp": "2024-01-15T10:30:00Z",
  "metadata": {
    "page_url": "/product/PROD001",
    "referrer": "search",
    "user_agent": "Mozilla/5.0..."
  }
}
```

**Parameters**:
- `user_id` (string, required): User identifier
- `product_id` (string, required): Product identifier
- `behavior_type` (string, required): Behavior type (`view`, `cart`, `purchase`, `wishlist`)
- `session_id` (string, optional): Session identifier
- `timestamp` (string, optional): ISO timestamp
- `metadata` (object, optional): Additional behavior data

**Response**:
```json
{
  "message": "Behavior tracked successfully",
  "user_id": "user_123",
  "product_id": "PROD001",
  "behavior_type": "view"
}
```

### GET /behaviors/{user_id} - Get User Behaviors

**Description**: Get user behavior history

**Authentication**: None required

**Parameters**:
- `user_id` (path, required): User identifier
- `limit` (query, optional): Number of behaviors to return (1-1000)

**Response**:
```json
{
  "user_id": "user_123",
  "behaviors": [
    {
      "behavior_id": 1,
      "product_id": "PROD001",
      "behavior_type": "view",
      "timestamp": "2024-01-15T10:30:00Z",
      "session_id": "sess_abc123"
    },
    {
      "behavior_id": 2,
      "product_id": "PROD002",
      "behavior_type": "purchase",
      "timestamp": "2024-01-15T11:00:00Z",
      "session_id": "sess_abc123"
    }
  ],
  "count": 2
}
```

## 🔒 Secured Endpoints

### GET /users/{user_id}/stats - Get User Statistics

**Description**: Get user analytics and behavior statistics

**Authentication**: API key required (`X-API-Key` header)

**Rate Limiting**: 10 requests per minute per user

**Parameters**:
- `user_id` (path, required): User identifier (alphanumeric, max 50 chars)

**Response**:
```json
{
  "user_id": "user_123",
  "total_interactions": 68,
  "unique_products": 23,
  "recent_activity_7_days": 15,
  "behavior_summary": {
    "view_count": 45,
    "cart_count": 12,
    "purchase_count": 8,
    "wishlist_count": 3
  }
}
```

**Security Features**:
- Input validation for user ID format
- Rate limiting per user
- API key authentication
- Data sanitization (no raw behavior data)
- Access logging for security monitoring

## 🚨 Error Handling

### HTTP Status Codes

- `200 OK`: Successful request
- `400 Bad Request`: Invalid input parameters
- `401 Unauthorized`: Missing or invalid API key
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error (graceful handling)

### Error Response Format

```json
{
  "detail": "User-friendly error message",
  "status": "error"
}
```

### Common Error Scenarios

#### Invalid User ID Format
```json
{
  "detail": "Invalid user ID format"
}
```

#### Missing API Key
```json
{
  "detail": "API key required for accessing user statistics"
}
```

#### Rate Limit Exceeded
```json
{
  "detail": "Rate limit exceeded. Try again later."
}
```

#### Database Error (Graceful)
```json
{
  "user_id": "user_123",
  "total_interactions": 0,
  "unique_products": 0,
  "recent_activity_7_days": 0,
  "behavior_summary": {
    "view_count": 0,
    "cart_count": 0,
    "purchase_count": 0,
    "wishlist_count": 0
  }
}
```

## 📝 Usage Examples

### Complete Workflow Example

```bash
# 1. Check API health
curl http://localhost:8000/health

# 2. Train models with sample data
curl -X POST http://localhost:8000/train \
  -H "Content-Type: application/json" \
  -d @sample_data.json

# 3. Track user behavior
curl -X POST http://localhost:8000/behaviors \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "product_id": "PROD001",
    "behavior_type": "view"
  }'

# 4. Get recommendations
curl -X POST http://localhost:8000/recommendations \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "algorithm": "hybrid",
    "n_recommendations": 5
  }'

# 5. Get trending products
curl -X POST http://localhost:8000/trending-products \
  -H "Content-Type: application/json" \
  -d '{
    "category": "electronics",
    "limit": 10,
    "timeframe_days": 7
  }'

# 6. Get user statistics (requires API key)
curl -X GET http://localhost:8000/users/user_123/stats \
  -H "X-API-Key: magento-recommendation-key-2024"
```

### Python Client Example

```python
import requests
import json

BASE_URL = "http://localhost:8000"
API_KEY = "magento-recommendation-key-2024"

# Track behavior
def track_behavior(user_id, product_id, behavior_type):
    response = requests.post(f"{BASE_URL}/behaviors", json={
        "user_id": user_id,
        "product_id": product_id,
        "behavior_type": behavior_type
    })
    return response.json()

# Get recommendations
def get_recommendations(user_id, algorithm="hybrid", limit=5):
    response = requests.post(f"{BASE_URL}/recommendations", json={
        "user_id": user_id,
        "algorithm": algorithm,
        "n_recommendations": limit
    })
    return response.json()

# Get user statistics
def get_user_stats(user_id):
    headers = {"X-API-Key": API_KEY}
    response = requests.get(f"{BASE_URL}/users/{user_id}/stats", headers=headers)
    return response.json()

# Usage
track_behavior("user_123", "PROD001", "view")
recommendations = get_recommendations("user_123")
stats = get_user_stats("user_123")
```

### JavaScript Client Example

```javascript
const BASE_URL = 'http://localhost:8000';
const API_KEY = 'magento-recommendation-key-2024';

// Track behavior
async function trackBehavior(userId, productId, behaviorType) {
    const response = await fetch(`${BASE_URL}/behaviors`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            user_id: userId,
            product_id: productId,
            behavior_type: behaviorType
        })
    });
    return await response.json();
}

// Get recommendations
async function getRecommendations(userId, algorithm = 'hybrid', limit = 5) {
    const response = await fetch(`${BASE_URL}/recommendations`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            user_id: userId,
            algorithm: algorithm,
            n_recommendations: limit
        })
    });
    return await response.json();
}

// Get user statistics
async function getUserStats(userId) {
    const response = await fetch(`${BASE_URL}/users/${userId}/stats`, {
        headers: {
            'X-API-Key': API_KEY
        }
    });
    return await response.json();
}

// Usage
trackBehavior('user_123', 'PROD001', 'view');
getRecommendations('user_123').then(console.log);
getUserStats('user_123').then(console.log);
```

## 🔧 Configuration

### Environment Variables

```bash
# API Configuration
API_KEY=magento-recommendation-key-2024
MAX_REQUESTS_PER_MINUTE=10

# Database Configuration
DATABASE_URL=mysql://user:password@mariadb:3306/recommendations

# Redis Configuration
REDIS_URL=redis://redis:6379

# ML Configuration
MODEL_CACHE_TTL=3600
MAX_RECOMMENDATIONS=10
```

## 📊 Performance Guidelines

### Response Time Targets
- **Health checks**: < 50ms
- **Behavior tracking**: < 100ms
- **Recommendations**: < 200ms
- **User statistics**: < 150ms

### Best Practices
1. **Use caching**: Recommendations are cached for 1 hour
2. **Batch operations**: Track multiple behaviors efficiently
3. **Error handling**: Always handle potential errors gracefully
4. **Rate limiting**: Respect API rate limits
5. **Input validation**: Validate data before sending

## 📞 Support

For API-related questions or issues:
- **Email:** jsjaimohan@gmail.com
- **Developer:** J S JAIMOHAN

This API is designed for internal Magento integration with focus on simplicity and performance.
