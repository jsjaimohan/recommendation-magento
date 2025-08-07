# Architecture Documentation

**Developer:** J S JAIMOHAN  
**Email:** jsjaimohan@gmail.com  
**License:** Private License

## Overview

This document provides a comprehensive overview of the Magento Recommendation System architecture, including system design, components, data flow, and deployment.

## 🏗️ System Architecture

### High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Magento       │    │  Recommendation │    │   Database      │
│   Frontend      │◄──►│     API         │◄──►│   (MariaDB)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Cache         │
                       │   (Redis)       │
                       └─────────────────┘
```

### Component Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Application                     │
├─────────────────────────────────────────────────────────────┤
│  Controllers (API Layer)                                  │
│  ├── Health Endpoints                                     │
│  ├── Recommendation Endpoints                             │
│  ├── Behavior Tracking Endpoints                          │
│  └── Model Management Endpoints                           │
├─────────────────────────────────────────────────────────────┤
│  Services (Business Logic)                                │
│  ├── RecommendationService (ML Engine)                    │
│  ├── BehaviorService (User Analytics)                     │
│  └── HealthService (System Monitoring)                    │
├─────────────────────────────────────────────────────────────┤
│  Models (Data Layer)                                      │
│  ├── Pydantic Models (Validation)                         │
│  └── Database Models (Persistence)                        │
├─────────────────────────────────────────────────────────────┤
│  External Dependencies                                    │
│  ├── MariaDB (Data Storage)                               │
│  ├── Redis (Caching)                                      │
│  └── scikit-learn (ML Algorithms)                        │
└─────────────────────────────────────────────────────────────┘
```

## 📁 File Structure

```
Magento-Recommendation/
├── app/
│   ├── main.py                     # Main FastAPI application
│   ├── models.py                   # Pydantic models/schemas
│   ├── recommendation_service.py    # ML and recommendation logic
│   ├── behavior_service.py         # User behavior tracking
│   ├── health_service.py           # Health checks and monitoring
│   └── database.py                 # Database operations
├── docs/
│   ├── Architecture.md             # This document
│   ├── API.md                      # API documentation
│   └── ML.md                       # Machine learning documentation
├── scripts/
│   ├── sample_data.py              # Sample data generation
│   └── test_complete_flow.py       # Comprehensive testing
├── docker-compose.yml              # Multi-service orchestration
├── Dockerfile                      # Application containerization
├── requirements.txt                # Python dependencies
├── init.sql                        # Database schema
├── README.md                       # Project overview
├── LICENSE                         # Private license
└── AUTHOR.md                       # Author information
```

## 🧩 Component Details

### 1. API Layer (`main.py`)

**Purpose**: HTTP endpoints and request handling

**Responsibilities**:
- Route definitions and request/response handling
- Input validation and error management
- Service orchestration
- CORS and middleware configuration

**Key Features**:
- FastAPI framework for high performance
- Automatic API documentation (Swagger/OpenAPI)
- Built-in validation with Pydantic
- Graceful error handling without stack traces

### 2. Service Layer

#### RecommendationService (`recommendation_service.py`)

**Responsibilities**:
- ML model training and management
- Recommendation generation using multiple algorithms
- Trending products calculation
- Model persistence (save/load)

**Key Methods**:
- `prepare_data()` - Data preparation for training
- `train_models()` - Train all recommendation algorithms
- `get_recommendations()` - Generate personalized recommendations
- `get_trending_products()` - Calculate trending products
- `save_model()` / `load_model()` - Model persistence

#### BehaviorService (`behavior_service.py`)

**Responsibilities**:
- User behavior tracking and analytics
- Behavior data validation and storage
- User statistics generation

**Key Methods**:
- `track_behavior()` - Save user behavior to database
- `get_user_behaviors()` - Retrieve user behavior history
- `get_user_stats()` - Generate user analytics

#### HealthService (`health_service.py`)

**Responsibilities**:
- System health monitoring
- Service status checks
- Connection testing

**Key Methods**:
- `get_health_status()` - Comprehensive health check
- `get_root_info()` - Basic API information

### 3. Models Layer (`models.py`)

**Purpose**: Data validation and serialization

**Contains**: All Pydantic models for requests/responses

**Benefits**:
- Type safety and automatic validation
- Clear API contracts
- Automatic documentation generation

## 🔄 Data Flow

### Recommendation Generation Flow

```
1. HTTP Request → FastAPI Route
2. Input Validation → Pydantic Models
3. Service Call → RecommendationService
4. Database Query → MariaDB
5. ML Processing → scikit-learn
6. Cache Check → Redis
7. Response Format → JSON
8. HTTP Response → Client
```

### Behavior Tracking Flow

```
1. User Action → Magento Frontend
2. Behavior Data → API Endpoint
3. Validation → Pydantic Models
4. Storage → MariaDB
5. Analytics → BehaviorService
6. Response → Confirmation
```

## 🗄️ Database Architecture

### MariaDB Schema

```sql
-- Users table (simplified for internal use)
CREATE TABLE users (
    user_id VARCHAR(50) PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Products table
CREATE TABLE products (
    product_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    subcategory VARCHAR(100),
    price DECIMAL(10,2),
    attributes JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User behaviors table
CREATE TABLE user_behaviors (
    behavior_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    product_id VARCHAR(50) NOT NULL,
    behavior_type ENUM('view', 'cart', 'purchase', 'wishlist'),
    session_id VARCHAR(100),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSON,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- Recommendations table
CREATE TABLE recommendations (
    recommendation_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    product_id VARCHAR(50) NOT NULL,
    score DECIMAL(5,4),
    algorithm_used VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- A/B testing table
CREATE TABLE ab_tests (
    test_id INT AUTO_INCREMENT PRIMARY KEY,
    test_name VARCHAR(100) NOT NULL,
    user_id VARCHAR(50) NOT NULL,
    variant VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
```

## 🔧 Technology Stack

### Backend Framework
- **FastAPI**: Modern Python web framework
- **Python 3.11**: Latest stable Python version
- **Uvicorn**: ASGI server for production

### Machine Learning
- **scikit-learn**: Primary ML library
- **pandas**: Data manipulation
- **numpy**: Numerical computations
- **pickle**: Model serialization

### Database & Caching
- **MariaDB**: Primary database
- **Redis**: Caching layer
- **SQLAlchemy**: ORM for database operations

### Containerization
- **Docker**: Application containerization
- **Docker Compose**: Multi-service orchestration

### Development Tools
- **Pydantic**: Data validation
- **Logging**: Python logging module
- **Testing**: pytest (for future implementation)

## 🚀 Deployment Architecture

### Docker Compose Services

```yaml
services:
  recommendation-api:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - mariadb
      - redis
    environment:
      - DATABASE_URL=mysql://user:password@mariadb:3306/recommendations
      - REDIS_URL=redis://redis:6379

  mariadb:
    image: mariadb:10.11
    environment:
      - MYSQL_ROOT_PASSWORD=rootpassword
      - MYSQL_DATABASE=recommendations
      - MYSQL_USER=user
      - MYSQL_PASSWORD=password
    ports:
      - "3306:3306"
    volumes:
      - mariadb_data:/var/lib/mysql
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

### Production Considerations

1. **Scaling**: Horizontal scaling with load balancers
2. **Monitoring**: Application metrics and health checks
3. **Security**: API key authentication and input validation
4. **Backup**: Database backup strategies
5. **Logging**: Centralized logging and error tracking

## 🔒 Security Architecture

### Authentication & Authorization
- **API Key Authentication**: For sensitive endpoints
- **Input Validation**: Prevents injection attacks
- **Rate Limiting**: Prevents abuse
- **Data Sanitization**: Removes sensitive information

### Data Protection
- **Database Security**: Encrypted connections
- **Cache Security**: Redis authentication
- **Error Handling**: No stack trace exposure
- **Access Logging**: Security monitoring

## 📊 Performance Architecture

### Caching Strategy
- **Redis Caching**: Frequently accessed recommendations
- **Cache TTL**: 1 hour for recommendation results
- **Cache Keys**: User-specific recommendation keys

### Database Optimization
- **Indexed Queries**: Fast user behavior retrieval
- **Connection Pooling**: Efficient database connections
- **Query Optimization**: Minimal database load

### ML Performance
- **Model Caching**: Pre-trained models in memory
- **Batch Processing**: Efficient recommendation generation
- **Algorithm Selection**: Fastest algorithm for user type

## 🔄 Integration Architecture

### Magento Integration
- **RESTful APIs**: Standard HTTP endpoints
- **JSON Responses**: Easy integration with frontend
- **Error Handling**: Graceful failure responses
- **Rate Limiting**: Prevents API abuse

### External Systems
- **Database**: MariaDB for persistent storage
- **Cache**: Redis for performance optimization
- **Monitoring**: Health check endpoints
- **Logging**: Structured logging for debugging

## 🧪 Testing Architecture

### Testing Strategy
- **Unit Tests**: Individual component testing
- **Integration Tests**: Service interaction testing
- **End-to-End Tests**: Complete workflow testing
- **Performance Tests**: Load and stress testing

### Test Data
- **Sample Data Generation**: Realistic test scenarios
- **Database Seeding**: Consistent test environment
- **Mock Services**: Isolated component testing

## 📈 Monitoring & Observability

### Health Checks
- **API Health**: Service availability
- **Database Health**: Connection status
- **Cache Health**: Redis connectivity
- **Model Health**: ML model status

### Metrics
- **Response Times**: API performance
- **Error Rates**: System reliability
- **Cache Hit Rates**: Performance optimization
- **Recommendation Quality**: ML model effectiveness

## 🔧 Configuration Management

### Environment Variables
```bash
# Database Configuration
DATABASE_URL=mysql://user:password@mariadb:3306/recommendations

# Redis Configuration
REDIS_URL=redis://redis:6379

# API Configuration
API_KEY=magento-recommendation-key-2024
MAX_REQUESTS_PER_MINUTE=10

# ML Configuration
MODEL_CACHE_TTL=3600
MAX_RECOMMENDATIONS=10
```

### Configuration Files
- **Docker Compose**: Service orchestration
- **Requirements**: Python dependencies
- **Database Schema**: SQL initialization
- **Logging**: Application logging configuration

## 🚀 Deployment Strategies

### Development Environment
- **Local Docker**: Complete local development
- **Hot Reloading**: Fast development iteration
- **Debug Logging**: Detailed error information

### Production Environment
- **Container Orchestration**: Kubernetes or Docker Swarm
- **Load Balancing**: Multiple API instances
- **Database Clustering**: High availability
- **Monitoring**: Comprehensive observability

## 📋 Best Practices

### Code Organization
- **Service Layer**: Business logic separation
- **Model Layer**: Data validation and contracts
- **API Layer**: HTTP handling and routing
- **Database Layer**: Data persistence

### Error Handling
- **Graceful Degradation**: System continues with errors
- **User-Friendly Messages**: Clear error responses
- **Logging**: Detailed error tracking
- **Monitoring**: Proactive error detection

### Performance
- **Caching**: Reduce database load
- **Connection Pooling**: Efficient resource usage
- **Batch Processing**: Optimize ML operations
- **Async Processing**: Non-blocking operations

## 📞 Support

For architecture-related questions:
- **Email:** jsjaimohan@gmail.com
- **Developer:** J S JAIMOHAN

This architecture is designed for internal Magento integration with focus on simplicity, maintainability, and performance. 