import logging
from typing import Dict, Any
from datetime import datetime

from models import UserBehavior
from database import db_manager

logger = logging.getLogger(__name__)

class BehaviorService:
    def __init__(self):
        pass
    
    def track_behavior(self, behavior: UserBehavior) -> Dict[str, Any]:
        """Track user behavior"""
        try:
            # Save behavior to database
            behavior_data = {
                "user_id": behavior.user_id,
                "product_id": behavior.product_id,
                "behavior_type": behavior.behavior_type,
                "session_id": behavior.session_id,
                "timestamp": behavior.timestamp,
                "metadata": behavior.metadata
            }
            
            success = db_manager.save_user_behavior(behavior_data)
            if not success:
                logger.error(f"Failed to save behavior for {behavior.user_id}")
                return {
                    "message": "Failed to track behavior",
                    "user_id": behavior.user_id,
                    "status": "error"
                }
            
            logger.info(f"Behavior tracked: {behavior.user_id} -> {behavior.product_id} ({behavior.behavior_type})")
            
            return {
                "message": "Behavior tracked successfully",
                "user_id": behavior.user_id,
                "product_id": behavior.product_id,
                "behavior_type": behavior.behavior_type
            }
            
        except Exception as e:
            logger.error(f"Behavior tracking error for {behavior.user_id}: {e}")
            return {
                "message": "Failed to track behavior",
                "user_id": behavior.user_id,
                "status": "error"
            }
    
    def get_user_behaviors(self, user_id: str, limit: int = 100) -> Dict[str, Any]:
        """Get user behaviors"""
        try:
            behaviors = db_manager.get_user_behaviors(user_id, limit)
            return {
                "user_id": user_id,
                "behaviors": behaviors,
                "count": len(behaviors)
            }
        except Exception as e:
            logger.error(f"Error getting user behaviors for {user_id}: {e}")
            # Return safe default instead of raising exception
            return {
                "user_id": user_id,
                "behaviors": [],
                "count": 0
            }
    
    def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """Get user statistics"""
        try:
            stats = db_manager.get_user_stats(user_id)
            return stats
        except Exception as e:
            logger.error(f"Error getting user stats for {user_id}: {e}")
            # Return safe default instead of raising exception
            return {
                "user_id": user_id,
                "behavior_counts": {},
                "unique_products": 0,
                "recent_activity_7_days": 0
            }
