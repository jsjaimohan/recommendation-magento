import logging
import redis
from typing import Dict, Any
from datetime import datetime

from database import db_manager

logger = logging.getLogger(__name__)

class HealthService:
    def __init__(self):
        self.redis_client = None
        
        # Try to connect to Redis
        try:
            self.redis_client = redis.from_url("redis://redis:6379", decode_responses=True)
            logger.info("Health service connected to Redis")
        except Exception as e:
            logger.warning(f"Health service Redis connection failed: {e}")
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get comprehensive health status"""
        services = {
            "api": "healthy",
            "recommendation_engine": "ready"  # Will be updated by recommendation service
        }
        
        # Check database connection
        if db_manager.test_connection():
            services["database"] = "connected"
        else:
            services["database"] = "disconnected"
        
        # Check Redis connection
        if self.redis_client:
            try:
                self.redis_client.ping()
                services["redis"] = "connected"
            except:
                services["redis"] = "disconnected"
        else:
            services["redis"] = "not_configured"
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "services": services
        }
    
    def get_root_info(self) -> Dict[str, str]:
        """Get root endpoint information"""
        return {
            "message": "Magento Recommendation API",
            "version": "1.0.0",
            "developer": "J S JAIMOHAN",
            "email": "jsjaimohan@gmail.com",
            "license": "Private License"
        }
