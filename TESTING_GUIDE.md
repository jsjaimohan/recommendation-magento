# Testing Guide
## Magento Recommendation System

### Overview
This guide provides step-by-step instructions for testing the recommendation system. Follow these steps to verify all functionality is working correctly.

---

## 🚀 Quick Start (5 minutes)

### Prerequisites
- Docker and Docker Compose installed
- Python 3.8+ installed
- Internet connection

### Step 1: Start the System
```bash
# Build and start all services
docker-compose up --build -d

# Wait for services to be ready (about 30 seconds)
sleep 30
```

### Step 2: Run Complete Test
```bash
# Install required Python package
pip install requests

# Run the comprehensive test
python scripts/test_complete_flow.py
```

### Step 3: Check Results
If everything works, you should see:
```
🎉 COMPLETE TEST FLOW FINISHED!
✅ The recommendation system is working correctly!
```

---

## 📋 Detailed Testing Steps

### Phase 1: System Setup

#### 1.1 Check Prerequisites
```bash
# Check Docker
docker --version
docker-compose --version

# Check Python
python --version
# or
python3 --version

# Check if you're in the correct directory
ls -la
# Should show: docker-compose.yml, Dockerfile, scripts/, app/, etc.
```

#### 1.2 Start Services
```bash
# Build and start all services
docker-compose up --build -d

# Check if all services are running
docker-compose ps
```

Expected output:
```
Name                    Command               State           Ports
magento-recommendation_mariadb_1            docker-entrypoint.sh mysqld      Up      0.0.0.0:3306->3306/tcp
magento-recommendation_recommendation-api_1 python main.py                  Up      0.0.0.0:8000->8000/tcp
magento-recommendation_redis_1              docker-entrypoint.sh redis ...   Up      0.0.0.0:6379->6379/tcp
```

#### 1.3 Wait for Services to Be Ready
```bash
# Wait 30 seconds for all services to initialize
sleep 30

# Check service health
curl http://localhost:8000/health
```

Expected output:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0",
  "services": {
    "api": "healthy",
    "database": "connected",
    "redis": "connected",
    "recommendation_engine": "not_trained"
  }
}
```

### Phase 2: Data Generation

#### 2.1 Install Python Dependencies
```bash
# Install requests module (needed for API testing)
pip install requests
# or
pip3 install requests
```

#### 2.2 Generate Sample Data
```bash
# Generate sample data for testing
python scripts/sample_data.py
```

Expected output:
```
Generated 150 user behaviors
Generated 15 products
Sample data saved to:
- sample_user_behaviors.json
- sample_product_data.json
```

#### 2.3 Verify Sample Data Files
```bash
# Check that files were created
ls -la sample_*.json

# View sample data structure
head -20 sample_user_behaviors.json
head -20 sample_product_data.json
```

### Phase 3: Model Training

#### 3.1 Train Models from Sample Data
```bash
# Train recommendation models
curl -X POST http://localhost:8000/train \
  -H "Content-Type: application/json" \
  -d @sample_user_behaviors.json
```

Expected output:
```json
{
  "message": "Models trained successfully",
  "users_count": 20,
  "products_count": 15,
  "model_saved": true
}
```

#### 3.2 Check Model Status
```bash
# Check if models are trained
curl http://localhost:8000/models/status
```

Expected output:
```json
{
  "is_trained": true,
  "users_count": 20,
  "products_count": 15,
  "algorithms_available": ["user_based", "content_based", "hybrid"]
}
```

### Phase 4: Behavior Tracking

#### 4.1 Track User Behaviors
```bash
# Track a view behavior
curl -X POST http://localhost:8000/behaviors \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_001",
    "product_id": "PROD001",
    "behavior_type": "view",
    "session_id": "test_session_001"
  }'

# Track a cart behavior
curl -X POST http://localhost:8000/behaviors \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_001",
    "product_id": "PROD002",
    "behavior_type": "cart",
    "session_id": "test_session_001"
  }'

# Track a purchase behavior
curl -X POST http://localhost:8000/behaviors \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_002",
    "product_id": "PROD001",
    "behavior_type": "purchase",
    "session_id": "test_session_002"
  }'
```

Expected output for each:
```json
{
  "message": "Behavior tracked successfully",
  "user_id": "user_001",
  "product_id": "PROD001",
  "behavior_type": "view"
}
```

#### 4.2 Verify Behavior Storage
```bash
# Get user behaviors
curl http://localhost:8000/behaviors/user_001

# Get user statistics
curl http://localhost:8000/users/user_001/stats
```

### Phase 5: Recommendation Generation

#### 5.1 Test User-Based Recommendations
```bash
curl -X POST http://localhost:8000/recommendations \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_001",
    "algorithm": "user_based",
    "n_recommendations": 3
  }'
```

#### 5.2 Test Content-Based Recommendations
```bash
curl -X POST http://localhost:8000/recommendations \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_001",
    "algorithm": "content_based",
    "n_recommendations": 3
  }'
```

#### 5.3 Test Hybrid Recommendations
```bash
curl -X POST http://localhost:8000/recommendations \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_001",
    "algorithm": "hybrid",
    "n_recommendations": 5
  }'
```

#### 5.4 Test Category Filtering
```bash
curl -X POST http://localhost:8000/recommendations \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_001",
    "algorithm": "hybrid",
    "n_recommendations": 3,
    "category_filter": "electronics"
  }'
```

#### 5.5 Test Trending Products
```bash
# Get all trending products
curl -X POST http://localhost:8000/trending-products \
  -H "Content-Type: application/json" \
  -d '{
    "limit": 5,
    "timeframe_days": 7
  }'

# Get trending products by category
curl -X POST http://localhost:8000/trending-products \
  -H "Content-Type: application/json" \
  -d '{
    "category": "electronics",
    "limit": 3,
    "timeframe_days": 7
  }'
```

Expected output for trending products:
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

Expected output for recommendations:
```json
{
  "user_id": "user_001",
  "recommendations": [
    {
      "product_id": "PROD003",
      "name": "MacBook Pro 16",
      "category": "electronics",
      "price": 2499.99,
      "score": 0.8
    }
  ],
  "algorithm": "hybrid",
  "generated_at": "2024-01-15T10:30:00Z",
  "execution_time": 0.045
}
```

### Phase 6: Database-Driven Training

#### 6.1 Train from Database Data
```bash
# Train models from accumulated database data
curl -X POST http://localhost:8000/train/from-db
```

Expected output:
```json
{
  "message": "Models trained successfully from database",
  "users_count": 2,
  "products_count": 2,
  "model_saved": true
}
```

### Phase 7: Advanced Testing

#### 7.1 Test API Documentation
Open in browser: http://localhost:8000/docs

#### 7.2 Test Health Monitoring
```bash
# Check detailed health status
curl http://localhost:8000/health | jq

# Check model status
curl http://localhost:8000/models/status | jq
```

#### 7.3 Test Error Handling
```bash
# Test with invalid user
curl -X POST http://localhost:8000/recommendations \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "invalid_user",
    "algorithm": "hybrid",
    "n_recommendations": 5
  }'
```

Expected output:
```json
{
  "detail": "Models must be trained before getting recommendations"
}
```

---

## 🧪 Automated Testing

### Run Complete Test Suite
```bash
# Run the comprehensive automated test
python scripts/test_complete_flow.py
```

This will automatically test:
- ✅ API health and connectivity
- ✅ Sample data generation
- ✅ Model training
- ✅ Behavior tracking
- ✅ Recommendation generation
- ✅ User analytics
- ✅ Database persistence
- ✅ Model status monitoring

### Expected Test Output
```
🚀 Starting Complete Recommendation System Test

============================================================
STEP 1: Testing API Health
============================================================
✅ Health check: 200
   Status: healthy
   Services: {'api': 'healthy', 'database': 'connected', 'redis': 'connected'}

============================================================
STEP 2: Generating Sample Data
============================================================
✅ Sample data generated successfully

============================================================
STEP 3: Loading Sample Data
============================================================
✅ Loaded 150 user behaviors
✅ Loaded 15 products

============================================================
STEP 4: Training Recommendation Models
============================================================
✅ Training response: 200
   Users: 20
   Products: 15
   Model saved: True

============================================================
STEP 5: Testing Behavior Tracking
============================================================
✅ Behavior 1 tracked: user_001 -> PROD001
✅ Behavior 2 tracked: user_001 -> PROD002
✅ Behavior 3 tracked: user_002 -> PROD001
   Successfully tracked 3/3 behaviors

============================================================
STEP 6: Testing Recommendation Generation
============================================================
✅ User-based recommendations: 3 recommendations
✅ Content-based recommendations: 3 recommendations
✅ Hybrid recommendations: 5 recommendations
✅ Category-filtered recommendations: 2 recommendations
   Successfully generated recommendations for 4/4 test cases

============================================================
STEP 7: Testing User Analytics
============================================================
✅ User user_001 behaviors: 3 interactions
✅ User user_002 behaviors: 1 interactions
✅ User statistics: 2 unique products

============================================================
STEP 8: Testing Database-Driven Training
============================================================
✅ Database training response: 200
   Users: 2
   Products: 2
   Model saved: True

============================================================
STEP 9: Testing Model Status
============================================================
✅ Model status response: 200
   Trained: True
   Users: 2
   Products: 2
   Algorithms: ['user_based', 'content_based', 'hybrid']

============================================================
🎉 COMPLETE TEST FLOW FINISHED!
============================================================
✅ The recommendation system is working correctly!
```

---

## 🔧 Troubleshooting

### Common Issues

#### Issue 1: "docker: command not found"
```bash
# Install Docker
# Follow instructions at: https://docs.docker.com/get-docker/
```

#### Issue 2: "python: command not found"
```bash
# Try these commands:
python3 --version
python3.11 --version
python3.10 --version

# Install Python if needed
# Follow instructions at: https://www.python.org/downloads/
```

#### Issue 3: "ModuleNotFoundError: No module named 'requests'"
```bash
# Install requests
pip install requests
# or
pip3 install requests
```

#### Issue 4: "Connection refused" on health check
```bash
# Wait longer for services to start
sleep 60

# Check service logs
docker-compose logs recommendation-api
docker-compose logs mariadb
docker-compose logs redis
```

#### Issue 5: "Port already in use"
```bash
# Check what's using the port
lsof -i :8000
lsof -i :3306
lsof -i :6379

# Stop conflicting services or change ports in docker-compose.yml
```

### Debug Commands

#### Check Service Status
```bash
# Check if all services are running
docker-compose ps

# Check service logs
docker-compose logs recommendation-api
docker-compose logs mariadb
docker-compose logs redis

# Follow logs in real-time
docker-compose logs -f recommendation-api
```

#### Check Database Connection
```bash
# Connect to MariaDB
docker-compose exec mariadb mysql -u recommendation_user -p recommendations

# Check tables
SHOW TABLES;
SELECT COUNT(*) FROM user_behaviors;
SELECT COUNT(*) FROM products;
```

#### Check Redis Connection
```bash
# Connect to Redis
docker-compose exec redis redis-cli

# Test Redis
PING
KEYS *
```

---

## 📊 Performance Testing

### Load Testing
```bash
# Test multiple concurrent requests
for i in {1..10}; do
  curl -X POST http://localhost:8000/recommendations \
    -H "Content-Type: application/json" \
    -d '{"user_id": "user_001", "algorithm": "hybrid", "n_recommendations": 5}' &
done
wait
```

### Response Time Testing
```bash
# Test response times
time curl -X POST http://localhost:8000/recommendations \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user_001", "algorithm": "hybrid", "n_recommendations": 5}'
```

---

## 🎯 Success Criteria

The system is working correctly if:

1. ✅ **Health Check**: All services show "connected" or "healthy"
2. ✅ **Data Generation**: Sample data files are created successfully
3. ✅ **Model Training**: Training completes without errors
4. ✅ **Behavior Tracking**: Behaviors are saved to database
5. ✅ **Recommendations**: All algorithms return recommendations
6. ✅ **Analytics**: User statistics are calculated correctly
7. ✅ **Database Training**: Models can be trained from database data
8. ✅ **Error Handling**: Invalid requests return appropriate errors

---

## 📞 Support

If you encounter issues:

1. **Check the troubleshooting section** above
2. **Review service logs**: `docker-compose logs`
3. **Verify prerequisites**: Docker, Python, network connectivity
4. **Test step by step**: Follow the detailed testing phases
5. **Check file permissions**: Ensure scripts are executable

---

## 🚀 Next Steps

After successful testing:

1. **Integration**: Connect to your Magento system
2. **Customization**: Modify algorithms and parameters
3. **Scaling**: Deploy to production environment
4. **Monitoring**: Set up alerts and dashboards
5. **Optimization**: Tune performance based on usage patterns

---

**Happy Testing! 🎉**
