# Magento Recommendation API

A microservice for providing personalized product recommendations to Magento e-commerce platforms through REST APIs.

## 📋 Author Information

**Developer:** J S JAIMOHAN  
**Email:** jsjaimohan@gmail.com  
**License:** Private License (see LICENSE file)

## 🚀 Features

- **Personalized Recommendations**: User-based, content-based, and hybrid recommendation algorithms
- **Trending Products**: Real-time trending products based on user behavior
- **Behavior Tracking**: Track user interactions (view, cart, purchase, wishlist)
- **ML Engine**: Machine learning models with scikit-learn
- **RESTful APIs**: Easy integration with Magento
- **Docker Support**: Containerized deployment
- **Database Integration**: MariaDB for persistent storage
- **Caching**: Redis for performance optimization

## 🏗️ Architecture

- **FastAPI**: Modern Python web framework
- **scikit-learn**: Machine learning algorithms
- **MariaDB**: Relational database
- **Redis**: Caching layer
- **Docker**: Containerization

## 📚 Documentation

- [Product Requirements Document](docs/PRD.md)
- [Technical Architecture](docs/ARCHITECTURE.md)
- [API Documentation](docs/API_DOCUMENTATION.md)
- [Implementation Guide](docs/IMPLEMENTATION_GUIDE.md)
- [Testing Guide](docs/TESTING_GUIDE.md)
- [Refactored Structure](docs/REFACTORED_STRUCTURE.md)

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.11+ (for local development)

### Running the Application

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Magento-Recommendation
   ```

2. **Start the services**
   ```bash
   docker-compose up --build -d
   ```

3. **Verify the application**
   ```bash
   curl http://localhost:8000/health
   ```

4. **Run the complete test flow**
   ```bash
   python3 scripts/test_complete_flow.py
   ```

## 📖 API Endpoints

- `GET /health` - Health check
- `POST /train` - Train recommendation models
- `POST /recommendations` - Get personalized recommendations
- `POST /trending-products` - Get trending products
- `POST /behaviors` - Track user behavior
- `GET /behaviors/{user_id}` - Get user behaviors
- `GET /users/{user_id}/stats` - Get user statistics

## 🧪 Testing

The application includes comprehensive testing:
- Automated test scripts
- Sample data generation
- End-to-end testing
- Performance monitoring

## 📄 License

This project is licensed under a Private License. See the [LICENSE](LICENSE) file for details.

**Copyright (c) 2024 J S JAIMOHAN (jsjaimohan@gmail.com)**

## 🤝 Support

For support, questions, or licensing inquiries, please contact:
- **Email:** jsjaimohan@gmail.com
- **Developer:** J S JAIMOHAN
