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
                raise Exception("Failed to save behavior")
            
            logger.info(f"Behavior tracked: {behavior.user_id} -> {behavior.product_id} ({behavior.behavior_type})")
            
            return {
                "message": "Behavior tracked successfully",
                "user_id": behavior.user_id,
                "product_id": behavior.product_id,
                "behavior_type": behavior.behavior_type
            }
            
        except Exception as e:
            logger.error(f"Behavior tracking error: {e}")
            raise
    
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
            logger.error(f"Error getting user behaviors: {e}")
            raise
    
    def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """Get user statistics"""
        try:
            stats = db_manager.get_user_stats(user_id)
            return stats
        except Exception as e:
            logger.error(f"Error getting user stats: {e}")
            raise
