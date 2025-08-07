# API Documentation

**Developer:** J S JAIMOHAN  
**Email:** jsjaimohan@gmail.com  
**License:** Private License

## Magento Recommendation Microservice

### Base URL
```
Production: https://api.recommendations.magento.com/v1
Development: http://localhost:3000/v1
```

### Authentication (Optional)
For internal Magento integration, authentication is optional. If enabled, use a simple API key:
```
X-API-Key: <your-api-key>
```

**Note**: Since this is a dedicated service for a specific Magento installation, authentication can be disabled for simpler integration.

### 1. User Management APIs

#### 1.1 Create User
```http
POST /users
Content-Type: application/json

{
  "email": "user@example.com",
  "name": "John Doe",
  "preferences": {
    "categories": ["electronics", "books"],
    "price_range": {"min": 10, "max": 500}
  }
}
```

**Response:**
```json
{
  "user_id": "12345",
  "email": "user@example.com",
  "name": "John Doe",
  "preferences": {
    "categories": ["electronics", "books"],
    "price_range": {"min": 10, "max": 500}
  },
  "created_at": "2024-01-15T10:30:00Z"
}
```

#### 1.2 Update User Preferences
```http
PUT /users/{user_id}/preferences
Content-Type: application/json

{
  "categories": ["electronics", "sports"],
  "price_range": {"min": 20, "max": 1000},
  "brands": ["Apple", "Nike"]
}
```

#### 1.3 Get User Profile
```http
GET /users/{user_id}
```

### 2. Behavior Tracking APIs

#### 2.1 Track User Behavior
```http
POST /behaviors
Content-Type: application/json

{
  "user_id": "12345",
  "product_id": "PROD001",
  "behavior_type": "view", // view, cart, purchase, wishlist
  "session_id": "sess_abc123",
  "timestamp": "2024-01-15T10:30:00Z",
  "metadata": {
    "page_url": "/product/PROD001",
    "referrer": "search"
  }
}
```

#### 2.2 Batch Behavior Tracking
```http
POST /behaviors/batch
Content-Type: application/json

{
  "behaviors": [
    {
      "user_id": "12345",
      "product_id": "PROD001",
      "behavior_type": "view",
      "timestamp": "2024-01-15T10:30:00Z"
    },
    {
      "user_id": "12345",
      "product_id": "PROD002",
      "behavior_type": "cart",
      "timestamp": "2024-01-15T10:35:00Z"
    }
  ]
}
```

### 3. Recommendation APIs

#### 3.1 Get Personalized Recommendations
```http
GET /recommendations/{user_id}?limit=10&algorithm=collaborative
```

**Response:**
```json
{
  "user_id": "12345",
  "recommendations": [
    {
      "product_id": "PROD003",
      "score": 0.85,
      "reason": "Users like you also purchased this",
      "algorithm": "collaborative_filtering"
    },
    {
      "product_id": "PROD004",
      "score": 0.72,
      "reason": "Based on your preferences",
      "algorithm": "content_based"
    }
  ],
  "generated_at": "2024-01-15T10:30:00Z"
}
```

#### 3.2 Get Category Recommendations
```http
GET /recommendations/{user_id}/category/{category_id}?limit=5
```

#### 3.3 Get Similar Products
```http
GET /products/{product_id}/similar?limit=5
```

#### 3.4 Get Trending Products
```http
POST /trending-products
Content-Type: application/json

{
  "category": "electronics",
  "limit": 10,
  "timeframe_days": 7
}
```

**Response:**
```json
[
  {
    "product_id": "PROD001",
    "name": "iPhone 15 Pro",
    "category": "electronics",
    "price": 999.99,
    "trending_score": 8.5,
    "trending_rank": 1
  },
  {
    "product_id": "PROD002",
    "name": "MacBook Pro 16",
    "category": "electronics",
    "price": 2499.99,
    "trending_score": 6.0,
    "trending_rank": 2
  }
]
```

**Parameters:**
- `category` (optional): Filter by product category
- `limit` (optional, default: 10): Number of trending products to return
- `timeframe_days` (optional, default: 7): Number of days to analyze for trending

**Behavior Weighting:**
- Purchase: 3.0 points
- Cart: 2.0 points
- Wishlist: 1.5 points
- View: 1.0 point

### 4. Analytics APIs

#### 4.1 Get Recommendation Performance
```http
GET /analytics/recommendations/{user_id}?start_date=2024-01-01&end_date=2024-01-15
```

**Response:**
```json
{
  "user_id": "12345",
  "metrics": {
    "total_recommendations": 150,
    "clicks": 45,
    "conversion_rate": 0.30,
    "revenue_generated": 1250.00
  },
  "period": {
    "start_date": "2024-01-01",
    "end_date": "2024-01-15"
  }
}
```

#### 4.2 Get A/B Test Results
```http
GET /analytics/ab-test/{test_id}
```

### 5. Product Management APIs

#### 5.1 Add Product
```http
POST /products
Content-Type: application/json

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
```

#### 5.2 Update Product
```http
PUT /products/{product_id}
Content-Type: application/json

{
  "price": 899.99,
  "attributes": {
    "brand": "Apple",
    "color": "Titanium",
    "storage": "256GB",
    "availability": "in_stock"
  }
}
```

### 6. Error Responses

#### 6.1 Standard Error Format
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid user_id format",
    "details": {
      "field": "user_id",
      "value": "invalid_id"
    }
  },
  "timestamp": "2024-01-15T10:30:00Z",
  "request_id": "req_abc123"
}
```

#### 6.2 Common Error Codes
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `429` - Rate Limit Exceeded
- `500` - Internal Server Error

### 7. Rate Limiting
- **Standard**: 1000 requests per hour
- **Premium**: 5000 requests per hour
- **Enterprise**: Custom limits

### 8. Webhooks

#### 8.1 Recommendation Generated
```http
POST /webhooks/recommendation-generated
Content-Type: application/json

{
  "event": "recommendation_generated",
  "user_id": "12345",
  "recommendations": [...],
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### 8.2 User Behavior Tracked
```http
POST /webhooks/behavior-tracked
Content-Type: application/json

{
  "event": "behavior_tracked",
  "user_id": "12345",
  "product_id": "PROD001",
  "behavior_type": "purchase",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### 9. Advanced Features

#### 9.1 Real-time Recommendations
```http
GET /recommendations/{user_id}/realtime?context=product_page&product_id=PROD001
```

#### 9.2 Seasonal Recommendations
```http
GET /recommendations/{user_id}/seasonal?season=winter&limit=10
```

#### 9.3 Cross-sell Recommendations
```http
GET /recommendations/{user_id}/cross-sell?product_id=PROD001&limit=5
```

### 10. SDK Examples

#### 10.1 JavaScript SDK
```javascript
const recommendationSDK = new RecommendationSDK({
  apiKey: 'your-api-key',
  baseUrl: 'https://api.recommendations.magento.com/v1'
});

// Get recommendations
const recommendations = await recommendationSDK.getRecommendations('user123', {
  limit: 10,
  algorithm: 'collaborative'
});

// Track behavior
await recommendationSDK.trackBehavior('user123', 'PROD001', 'view');
```

#### 10.2 PHP SDK
```php
$recommendationSDK = new RecommendationSDK([
    'api_key' => 'your-api-key',
    'base_url' => 'https://api.recommendations.magento.com/v1'
]);

// Get recommendations
$recommendations = $recommendationSDK->getRecommendations('user123', [
    'limit' => 10,
    'algorithm' => 'collaborative'
]);

// Track behavior
$recommendationSDK->trackBehavior('user123', 'PROD001', 'view');
```

### 11. Integration Examples

#### 11.1 Magento Integration
```php
// Magento extension example
class RecommendationService
{
    private $apiKey;
    private $baseUrl;

    public function __construct($apiKey, $baseUrl)
    {
        $this->apiKey = $apiKey;
        $this->baseUrl = $baseUrl;
    }

    public function getRecommendations($customerId, $limit = 10)
    {
        $url = $this->baseUrl . "/recommendations/{$customerId}?limit={$limit}";
        
        $headers = [
            'Authorization: Bearer ' . $this->apiKey,
            'Content-Type: application/json'
        ];

        $response = $this->makeRequest($url, 'GET', [], $headers);
        return json_decode($response, true);
    }

    public function trackBehavior($customerId, $productId, $behaviorType)
    {
        $url = $this->baseUrl . "/behaviors";
        
        $data = [
            'user_id' => $customerId,
            'product_id' => $productId,
            'behavior_type' => $behaviorType,
            'timestamp' => date('c')
        ];

        $headers = [
            'Authorization: Bearer ' . $this->apiKey,
            'Content-Type: application/json'
        ];

        $this->makeRequest($url, 'POST', $data, $headers);
    }

    private function makeRequest($url, $method, $data = [], $headers = [])
    {
        $ch = curl_init();
        curl_setopt($ch, CURLOPT_URL, $url);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
        
        if ($method === 'POST') {
            curl_setopt($ch, CURLOPT_POST, true);
            curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
        }
        
        $response = curl_exec($ch);
        curl_close($ch);
        
        return $response;
    }
}
```

#### 11.2 Frontend Integration
```javascript
// Frontend JavaScript integration
class RecommendationWidget {
    constructor(config) {
        this.apiKey = config.apiKey;
        this.baseUrl = config.baseUrl;
        this.userId = config.userId;
    }

    async loadRecommendations(containerId, options = {}) {
        const response = await fetch(
            `${this.baseUrl}/recommendations/${this.userId}?limit=${options.limit || 5}`,
            {
                headers: {
                    'Authorization': `Bearer ${this.apiKey}`,
                    'Content-Type': 'application/json'
                }
            }
        );

        const data = await response.json();
        this.renderRecommendations(containerId, data.recommendations);
    }

    renderRecommendations(containerId, recommendations) {
        const container = document.getElementById(containerId);
        container.innerHTML = '';

        recommendations.forEach(rec => {
            const productElement = document.createElement('div');
            productElement.className = 'recommendation-item';
            productElement.innerHTML = `
                <h3>${rec.product_name}</h3>
                <p>${rec.reason}</p>
                <button onclick="trackBehavior('${rec.product_id}', 'view')">
                    View Product
                </button>
            `;
            container.appendChild(productElement);
        });
    }

    async trackBehavior(productId, behaviorType) {
        await fetch(`${this.baseUrl}/behaviors`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${this.apiKey}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user_id: this.userId,
                product_id: productId,
                behavior_type: behaviorType,
                timestamp: new Date().toISOString()
            })
        });
    }
}

// Usage
const widget = new RecommendationWidget({
    apiKey: 'your-api-key',
    baseUrl: 'https://api.recommendations.magento.com/v1',
    userId: 'user123'
});

widget.loadRecommendations('recommendations-container', { limit: 5 });
```

### 12. Testing APIs

#### 12.1 Health Check
```http
GET /health
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

#### 12.2 API Status
```http
GET /status
```

**Response:**
```json
{
  "api_version": "1.0.0",
  "uptime": "7d 3h 45m",
  "requests_per_minute": 1250,
  "average_response_time": "45ms",
  "error_rate": "0.1%"
}
```

This comprehensive API documentation provides all the necessary endpoints, request/response formats, and integration examples for your Magento Recommendation Microservice.
