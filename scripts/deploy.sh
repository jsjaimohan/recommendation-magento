#!/bin/bash

# Magento Recommendation System - Deployment Script
# Developer: J S JAIMOHAN (jsjaimohan@gmail.com)
# License: Private License

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="magento-recommendation"
DOCKER_COMPOSE_FILE="docker-compose.yml"
DB_CONTAINER="magento-recommendation-mariadb-1"
API_CONTAINER="magento-recommendation-recommendation-api-1"
REDIS_CONTAINER="magento-recommendation-redis-1"

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO: $1${NC}"
}

# Check if Docker is running
check_docker() {
    log "Checking Docker installation..."
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        error "Docker is not running. Please start Docker first."
        exit 1
    fi
    
    log "Docker is running ✓"
}

# Check if Docker Compose is available
check_docker_compose() {
    log "Checking Docker Compose..."
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    log "Docker Compose is available ✓"
}

# Stop and remove existing containers
cleanup_existing() {
    log "Cleaning up existing containers..."
    docker-compose down --volumes --remove-orphans 2>/dev/null || true
    log "Cleanup completed ✓"
}

# Start the services
start_services() {
    log "Starting services with Docker Compose..."
    docker-compose up --build -d
    
    # Wait for services to be ready
    log "Waiting for services to be ready..."
    sleep 15
    
    # Check if containers are running
    if ! docker ps | grep -q "$DB_CONTAINER"; then
        error "Database container is not running"
        exit 1
    fi
    
    if ! docker ps | grep -q "$API_CONTAINER"; then
        error "API container is not running"
        exit 1
    fi
    
    if ! docker ps | grep -q "$REDIS_CONTAINER"; then
        error "Redis container is not running"
        exit 1
    fi
    
    log "All services are running ✓"
}

# Wait for database to be ready
wait_for_database() {
    log "Waiting for database to be ready..."
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if docker exec "$DB_CONTAINER" mysql -u recommendation_user -ppassword -e "SELECT 1;" &>/dev/null; then
            log "Database is ready ✓"
            return 0
        fi
        
        info "Attempt $attempt/$max_attempts - Database not ready yet..."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    error "Database failed to start within expected time"
    exit 1
}

# Initialize database schema
init_database() {
    log "Initializing database schema..."
    
    # Check if tables already exist
    local table_count=$(docker exec "$DB_CONTAINER" mysql -u recommendation_user -ppassword -e "USE recommendations; SHOW TABLES;" 2>/dev/null | wc -l)
    
    if [ "$table_count" -gt 1 ]; then
        warn "Database tables already exist. Skipping schema initialization."
        return 0
    fi
    
    # Create database schema
    log "Creating database tables..."
    docker exec -i "$DB_CONTAINER" mysql -u recommendation_user -ppassword recommendations < init.sql
    
    if [ $? -eq 0 ]; then
        log "Database schema created successfully ✓"
    else
        error "Failed to create database schema"
        exit 1
    fi
}

# Create FBT-specific tables
create_fbt_tables() {
    log "Creating FBT (Frequently Bought Together) tables..."
    
    # Check if FBT tables exist
    local fbt_table_count=$(docker exec "$DB_CONTAINER" mysql -u recommendation_user -ppassword -e "USE recommendations; SHOW TABLES LIKE '%purchase%';" 2>/dev/null | wc -l)
    
    if [ "$fbt_table_count" -gt 1 ]; then
        warn "FBT tables already exist. Skipping FBT table creation."
        return 0
    fi
    
    # Create FBT tables
    docker exec -i "$DB_CONTAINER" mysql -u recommendation_user -ppassword recommendations << 'EOF'
-- Purchase transactions table (NEW for FBT)
CREATE TABLE IF NOT EXISTS purchase_transactions (
    transaction_id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255),
    order_id VARCHAR(255),
    purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_amount DECIMAL(10,2),
    status VARCHAR(50) DEFAULT 'completed',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Transaction items table (NEW for FBT)
CREATE TABLE IF NOT EXISTS transaction_items (
    transaction_id VARCHAR(255),
    product_id VARCHAR(255),
    quantity INT DEFAULT 1,
    unit_price DECIMAL(10,2),
    total_price DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (transaction_id, product_id),
    FOREIGN KEY (transaction_id) REFERENCES purchase_transactions(transaction_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
);

-- Product associations table (NEW for FBT)
CREATE TABLE IF NOT EXISTS product_associations (
    product_id VARCHAR(255),
    associated_product_id VARCHAR(255),
    support DECIMAL(5,4),      -- How often they appear together
    confidence DECIMAL(5,4),    -- How likely Y is bought with X
    lift DECIMAL(5,4),         -- How much more likely than random
    rule_type VARCHAR(50) DEFAULT 'frequently_bought_together',
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (product_id, associated_product_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE,
    FOREIGN KEY (associated_product_id) REFERENCES products(product_id) ON DELETE CASCADE
);

-- Add transaction_id to user_behaviors for FBT
ALTER TABLE user_behaviors ADD COLUMN IF NOT EXISTS transaction_id VARCHAR(255) NULL;
ALTER TABLE user_behaviors ADD INDEX IF NOT EXISTS idx_user_behaviors_transaction (transaction_id);

-- NEW: Indexes for FBT tables
CREATE INDEX IF NOT EXISTS idx_purchase_transactions_user_id ON purchase_transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_purchase_transactions_date ON purchase_transactions(purchase_date);
CREATE INDEX IF NOT EXISTS idx_purchase_transactions_order_id ON purchase_transactions(order_id);

CREATE INDEX IF NOT EXISTS idx_transaction_items_product_id ON transaction_items(product_id);
CREATE INDEX IF NOT EXISTS idx_transaction_items_transaction_id ON transaction_items(transaction_id);

CREATE INDEX IF NOT EXISTS idx_product_associations_support ON product_associations(support DESC);
CREATE INDEX IF NOT EXISTS idx_product_associations_confidence ON product_associations(confidence DESC);
CREATE INDEX IF NOT EXISTS idx_product_associations_lift ON product_associations(lift DESC);
CREATE INDEX IF NOT EXISTS idx_product_associations_product_id ON product_associations(product_id);
EOF

    if [ $? -eq 0 ]; then
        log "FBT tables created successfully ✓"
    else
        error "Failed to create FBT tables"
        exit 1
    fi
}

# Verify database setup
verify_database() {
    log "Verifying database setup..."
    
    # Check if all required tables exist
    local required_tables=("users" "products" "user_behaviors" "recommendations" "purchase_transactions" "transaction_items" "product_associations")
    
    for table in "${required_tables[@]}"; do
        local table_exists=$(docker exec "$DB_CONTAINER" mysql -u recommendation_user -ppassword -e "USE recommendations; SHOW TABLES LIKE '$table';" 2>/dev/null | wc -l)
        
        if [ "$table_exists" -eq 1 ]; then
            log "✓ Table '$table' exists"
        else
            error "✗ Table '$table' is missing"
            exit 1
        fi
    done
    
    log "Database verification completed ✓"
}

# Wait for API to be ready
wait_for_api() {
    log "Waiting for API to be ready..."
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s http://localhost:8000/health &>/dev/null; then
            log "API is ready ✓"
            return 0
        fi
        
        info "Attempt $attempt/$max_attempts - API not ready yet..."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    error "API failed to start within expected time"
    exit 1
}

# Test API endpoints
test_api() {
    log "Testing API endpoints..."
    
    # Test health endpoint
    local health_response=$(curl -s http://localhost:8000/health)
    if echo "$health_response" | grep -q "healthy"; then
        log "✓ Health endpoint working"
    else
        error "✗ Health endpoint failed"
        exit 1
    fi
    
    # Test root endpoint
    local root_response=$(curl -s http://localhost:8000/)
    if echo "$root_response" | grep -q "Magento Recommendation API"; then
        log "✓ Root endpoint working"
    else
        error "✗ Root endpoint failed"
        exit 1
    fi
    
    log "API testing completed ✓"
}

# Generate sample data (optional)
generate_sample_data() {
    log "Generating sample data..."
    
    if [ -f "scripts/generate_fbt_sample_data.py" ]; then
        python3 scripts/generate_fbt_sample_data.py
        log "Sample data generation completed ✓"
    else
        warn "Sample data generation script not found. Skipping."
    fi
}

# Display deployment information
show_deployment_info() {
    echo ""
    echo "🎉 Deployment completed successfully!"
    echo "=================================="
    echo ""
    echo "📊 Services Status:"
    echo "  • Database: Running on localhost:3306"
    echo "  • API: Running on http://localhost:8000"
    echo "  • Redis: Running on localhost:6379"
    echo ""
    echo "🔗 API Endpoints:"
    echo "  • Health Check: http://localhost:8000/health"
    echo "  • API Documentation: http://localhost:8000/docs"
    echo "  • FBT Generation: POST http://localhost:8000/fbt/generate"
    echo "  • FBT Recommendations: POST http://localhost:8000/fbt/recommendations"
    echo ""
    echo "📚 Documentation:"
    echo "  • API Documentation: docs/API.md"
    echo "  • Architecture: docs/Architecture.md"
    echo "  • ML Guide: docs/ML.md"
    echo ""
    echo "🛠️  Useful Commands:"
    echo "  • View logs: docker-compose logs -f"
    echo "  • Stop services: docker-compose down"
    echo "  • Restart services: docker-compose restart"
    echo "  • Generate sample data: python3 scripts/generate_fbt_sample_data.py"
    echo ""
    echo "👨‍💻 Developer: J S JAIMOHAN (jsjaimohan@gmail.com)"
    echo "📄 License: Private License"
    echo ""
}

# Main deployment function
deploy() {
    echo "🚀 Magento Recommendation System - Deployment Script"
    echo "=================================================="
    echo "Developer: J S JAIMOHAN (jsjaimohan@gmail.com)"
    echo "License: Private License"
    echo ""
    
    # Check prerequisites
    check_docker
    check_docker_compose
    
    # Cleanup and start services
    cleanup_existing
    start_services
    
    # Initialize database
    wait_for_database
    init_database
    create_fbt_tables
    verify_database
    
    # Test API
    wait_for_api
    test_api
    
    # Generate sample data (optional)
    if [ "$1" = "--with-sample-data" ]; then
        generate_sample_data
    fi
    
    # Show deployment information
    show_deployment_info
}

# Help function
show_help() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --with-sample-data    Generate sample data after deployment"
    echo "  --help, -h            Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                    Deploy without sample data"
    echo "  $0 --with-sample-data Deploy with sample data generation"
    echo ""
}

# Parse command line arguments
case "${1:-}" in
    --help|-h)
        show_help
        exit 0
        ;;
    --with-sample-data)
        deploy "$1"
        ;;
    "")
        deploy
        ;;
    *)
        error "Unknown option: $1"
        show_help
        exit 1
        ;;
esac
