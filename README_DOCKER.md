# Dockerized Recommendation System
## Magento Recommendation Microservice

### Overview
This is a complete, dockerized recommendation system that you can use for PoC with your existing Magento system. The application includes:

- **FastAPI-based REST API** with recommendation endpoints
- **MariaDB database** for persistent data storage
- **Redis caching** for performance
- **Sample data generator** for testing
- **Complete test suite** to validate functionality
- **Docker Compose** for easy deployment

### Quick Start

#### 1. Prerequisites
- Docker and Docker Compose installed
- Git (to clone the repository)

#### 2. Clone and Setup
```bash
# Clone the repository (if not already done)
git clone <repository-url>
cd Magento-Recommendation

# Generate sample data
python scripts/sample_data.py
```

#### 3. Start the Application
```bash
# Build and start all services
docker-compose up --build

# Or run in background
docker-compose up -d --build
```

#### 4. Test the Application
```bash
# Run the test suite
python scripts/test_api.py
```

### Application Structure

```
Magento-Recommendation/
├── app/
│   ├── main.py                 # FastAPI application
│   └── database.py             # Database management
├── scripts/
│   ├── sample_data.py          # Sample data generator
│   └── test_api.py             # API test suite
├── docs/                       # Documentation
├── models/                     # Saved models (created at runtime)
├── Dockerfile                  # Python application container
├── docker-compose.yml          # Multi-service orchestration
├── init.sql                    # Database initialization
├── requirements.txt            # Python dependencies
└── README_DOCKER.md           # This file
```

### Data Persistence

The application now includes **persistent data storage** with MariaDB:

#### **Database Tables:**
- **users**: User profiles and preferences
- **products**: Product catalog
- **user_behaviors**: All user interactions (views, carts, purchases)
- **recommendations**: Generated recommendations with scores
- **ab_tests**: A/B testing configuration

#### **Key Features:**
- **Automatic user creation** when tracking behaviors
- **Automatic product creation** when tracking behaviors
- **Persistent recommendation storage** with scores
- **User statistics** and behavior analytics
- **Database-driven training** from accumulated data

### API Endpoints

#### Health Check
```bash
curl http://localhost:8000/health
```

#### Train Models (from sample data)
```bash
curl -X POST http://localhost:8000/train \
  -H "Content-Type: application/json" \
  -d @sample_data.json
```

#### Train Models (from database)
```bash
curl -X POST http://localhost:8000/train/from-db
```

#### Get Recommendations
```bash
curl -X POST http://localhost:8000/recommendations \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_001",
    "algorithm": "hybrid",
    "n_recommendations": 5
  }'
```

#### Track Behavior
```bash
curl -X POST http://localhost:8000/behaviors \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_001",
    "product_id": "PROD001",
    "behavior_type": "view"
  }'
```

#### Get User Behaviors
```bash
curl http://localhost:8000/behaviors/user_001
```

#### Get User Statistics
```bash
curl http://localhost:8000/users/user_001/stats
```

### API Documentation

Once the application is running, you can access:
- **Interactive API Docs**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc

### Sample Data

The application includes a sample data generator that creates:
- **20 users** with realistic behavior patterns
- **15 products** across different categories
- **Realistic user interactions** (views, carts, purchases)

To generate new sample data:
```bash
python scripts/sample_data.py
```

### Testing the System

#### 1. Automated Test Suite
```bash
# Run the complete test suite
python scripts/test_api.py
```

#### 2. Manual Testing
```bash
# Check if services are running
docker-compose ps

# View logs
docker-compose logs recommendation-api
docker-compose logs mariadb
docker-compose logs redis

# Test health endpoint
curl http://localhost:8000/health
```

#### 3. Integration Testing
```bash
# Test the complete flow with data persistence
# 1. Generate sample data
python scripts/sample_data.py

# 2. Train models from sample data
curl -X POST http://localhost:8000/train \
  -H "Content-Type: application/json" \
  -d @sample_data.json

# 3. Track some behaviors
curl -X POST http://localhost:8000/behaviors \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_001",
    "product_id": "PROD001",
    "behavior_type": "view"
  }'

# 4. Train models from accumulated database data
curl -X POST http://localhost:8000/train/from-db

# 5. Get recommendations
curl -X POST http://localhost:8000/recommendations \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_001",
    "algorithm": "hybrid",
    "n_recommendations": 5
  }'
```

### Configuration

#### Environment Variables
You can customize the application by setting environment variables in `docker-compose.yml`:

```yaml
environment:
  - DATABASE_URL=mysql://recommendation_user:password@mariadb:3306/recommendations
  - REDIS_URL=redis://redis:6379
  - MODEL_PATH=/app/models
  - LOG_LEVEL=INFO
```

#### Database Configuration
The application uses MariaDB for data persistence:
- **Database**: recommendations
- **User**: recommendation_user
- **Password**: password
- **Port**: 3306
- **Data Persistence**: MariaDB data is persisted to volume

### Performance Features

#### 1. Data Persistence
- **MariaDB storage** for all user behaviors
- **Automatic data accumulation** over time
- **Database-driven training** from real user data
- **Recommendation history** tracking

#### 2. Caching
- **Recommendation caching** in Redis
- **1-hour cache TTL** for recommendations
- **Automatic cache invalidation** on model retraining

#### 3. Algorithms
- **User-based collaborative filtering**
- **Content-based filtering**
- **Hybrid approach** (combines both)
- **Category filtering** support

#### 4. Monitoring
- **Health check endpoints**
- **Performance metrics** (execution time)
- **Model status monitoring**
- **Database connection monitoring**

### Integration with Magento

#### 1. API Integration
```php
// PHP example for Magento integration
class RecommendationService
{
    private $apiUrl = 'http://localhost:8000';
    
    public function getRecommendations($customerId, $limit = 5)
    {
        $data = [
            'user_id' => $customerId,
            'algorithm' => 'hybrid',
            'n_recommendations' => $limit
        ];
        
        $response = $this->makeRequest('/recommendations', 'POST', $data);
        return json_decode($response, true);
    }
    
    public function trackBehavior($customerId, $productId, $behaviorType)
    {
        $data = [
            'user_id' => $customerId,
            'product_id' => $productId,
            'behavior_type' => $behaviorType
        ];
        
        return $this->makeRequest('/behaviors', 'POST', $data);
    }
    
    private function makeRequest($endpoint, $method, $data = [])
    {
        $ch = curl_init();
        curl_setopt($ch, CURLOPT_URL, $this->apiUrl . $endpoint);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type: application/json']);
        
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

#### 2. JavaScript Integration
```javascript
// Frontend integration
class RecommendationWidget {
    constructor(apiUrl = 'http://localhost:8000') {
        this.apiUrl = apiUrl;
    }
    
    async getRecommendations(userId, limit = 5) {
        const response = await fetch(`${this.apiUrl}/recommendations`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user_id: userId,
                algorithm: 'hybrid',
                n_recommendations: limit
            })
        });
        
        return response.json();
    }
    
    async trackBehavior(userId, productId, behaviorType) {
        await fetch(`${this.apiUrl}/behaviors`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user_id: userId,
                product_id: productId,
                behavior_type: behaviorType
            })
        });
    }
}

// Usage
const widget = new RecommendationWidget();
const recommendations = await widget.getRecommendations('user_001', 5);
console.log('Recommendations:', recommendations);
```

### Troubleshooting

#### Common Issues

1. **Port already in use**
   ```bash
   # Check what's using port 8000
   lsof -i :8000
   
   # Change port in docker-compose.yml
   ports:
     - "8001:8000"  # Use port 8001 instead
   ```

2. **MariaDB connection failed**
   ```bash
   # Check MariaDB logs
   docker-compose logs mariadb
   
   # Restart MariaDB
   docker-compose restart mariadb
   ```

3. **Redis connection failed**
   ```bash
   # Check Redis logs
   docker-compose logs redis
   
   # Restart Redis
   docker-compose restart redis
   ```

4. **Model training fails**
   ```bash
   # Check application logs
   docker-compose logs recommendation-api
   
   # Ensure sample data exists
   ls -la sample_*.json
   ```

#### Debug Mode
```bash
# Run with debug logging
docker-compose up --build -d
docker-compose logs -f recommendation-api
```

### Production Deployment

#### 1. Environment Variables
```bash
# Create .env file
DATABASE_URL=mysql://user:password@your-mariadb-server:3306/recommendations
REDIS_URL=redis://your-redis-server:6379
LOG_LEVEL=WARNING
MODEL_PATH=/app/models
```

#### 2. Security Considerations
- **Network isolation** (internal network only)
- **API key validation** (if needed)
- **Rate limiting** (implement in nginx)
- **HTTPS** (use reverse proxy)

#### 3. Scaling
```yaml
# docker-compose.yml
services:
  recommendation-api:
    deploy:
      replicas: 3
    environment:
      - DATABASE_URL=mysql://user:password@mariadb-cluster:3306/recommendations
```

### Development

#### 1. Local Development
```bash
# Run without Docker
pip install -r requirements.txt
python app/main.py
```

#### 2. Code Changes
```bash
# The app directory is mounted as a volume
# Changes are reflected immediately
docker-compose up --build
```

#### 3. Adding New Features
1. Modify `app/main.py`
2. Add new endpoints
3. Test with `scripts/test_api.py`
4. Deploy with `docker-compose up --build`

### Monitoring and Logs

#### 1. View Logs
```bash
# All services
docker-compose logs

# Specific service
docker-compose logs recommendation-api
docker-compose logs mariadb
docker-compose logs redis

# Follow logs
docker-compose logs -f recommendation-api
```

#### 2. Health Monitoring
```bash
# Check service health
curl http://localhost:8000/health

# Check model status
curl http://localhost:8000/models/status
```

### Performance Optimization

#### 1. Caching Strategy
- **Recommendation caching**: 1 hour TTL
- **Model caching**: Persistent storage
- **Redis optimization**: Configure memory limits

#### 2. Algorithm Tuning
- **User-based**: Adjust similarity threshold
- **Content-based**: Tune TF-IDF parameters
- **Hybrid**: Weight different algorithms

#### 3. Resource Limits
```yaml
# docker-compose.yml
services:
  recommendation-api:
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
```

### Data Management

#### 1. Database Backup
```bash
# Backup MariaDB data
docker-compose exec mariadb mysqldump -u recommendation_user -p recommendations > backup.sql

# Restore from backup
docker-compose exec -T mariadb mysql -u recommendation_user -p recommendations < backup.sql
```

#### 2. Data Migration
```bash
# Export data
docker-compose exec mariadb mysqldump -u recommendation_user -p recommendations > data_export.sql

# Import data
docker-compose exec -T mariadb mysql -u recommendation_user -p recommendations < data_export.sql
```

This dockerized application provides a complete PoC environment for your Magento recommendation system with persistent data storage. You can easily test, modify, and deploy it to production.
