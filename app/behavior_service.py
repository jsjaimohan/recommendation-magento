import logging
import time
from typing import Dict, Any, List
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
                "transaction_id": behavior.transaction_id,
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
    
    def track_purchase_transaction(self, user_id: str, order_id: str, 
                                 products: List[Dict[str, Any]], total_amount: float) -> Dict[str, Any]:
        """
        Track a complete purchase transaction for FBT analysis
        """
        try:
            start_time = time.time()
            
            # Generate transaction ID
            transaction_id = f"txn_{order_id}_{int(time.time())}"
            
            # Prepare transaction data
            transaction_data = {
                "transaction_id": transaction_id,
                "user_id": user_id,
                "order_id": order_id,
                "total_amount": total_amount,
                "status": "completed",
                "items": []
            }
            
            # Prepare items
            for product in products:
                item = {
                    "product_id": product["product_id"],
                    "quantity": product.get("quantity", 1),
                    "unit_price": product.get("unit_price", 0),
                    "total_price": product.get("total_price", 0)
                }
                transaction_data["items"].append(item)
            
            # Save transaction
            success = db_manager.save_purchase_transaction(transaction_data)
            
            if not success:
                logger.error(f"Failed to save purchase transaction for {user_id}")
                return {
                    "message": "Failed to track purchase transaction",
                    "user_id": user_id,
                    "order_id": order_id,
                    "status": "error"
                }
            
            # Track individual purchase behaviors with transaction_id
            for product in products:
                behavior_data = {
                    "user_id": user_id,
                    "product_id": product["product_id"],
                    "behavior_type": "purchase",
                    "transaction_id": transaction_id,
                    "session_id": f"session_{order_id}",
                    "metadata": {
                        "quantity": product.get("quantity", 1),
                        "unit_price": product.get("unit_price", 0),
                        "order_id": order_id,
                        "transaction_id": transaction_id
                    }
                }
                
                db_manager.save_user_behavior(behavior_data)
            
            execution_time = time.time() - start_time
            
            logger.info(f"Purchase transaction tracked: {user_id} -> {order_id} ({len(products)} products)")
            
            return {
                "message": "Purchase transaction tracked successfully",
                "user_id": user_id,
                "order_id": order_id,
                "transaction_id": transaction_id,
                "products_count": len(products),
                "total_amount": total_amount,
                "execution_time": execution_time
            }
            
        except Exception as e:
            logger.error(f"Error tracking purchase transaction for {user_id}: {e}")
            return {
                "message": "Failed to track purchase transaction",
                "user_id": user_id,
                "order_id": order_id,
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
    
    def get_purchase_transactions(self, user_id: str = None, limit: int = 100) -> Dict[str, Any]:
        """
        Get purchase transactions for FBT analysis
        """
        try:
            transactions = db_manager.get_purchase_transactions(limit=limit)
            
            # Filter by user if specified
            if user_id:
                transactions = [txn for txn in transactions if txn["user_id"] == user_id]
            
            return {
                "transactions": transactions,
                "count": len(transactions),
                "user_id": user_id
            }
            
        except Exception as e:
            logger.error(f"Error getting purchase transactions: {e}")
            return {
                "transactions": [],
                "count": 0,
                "user_id": user_id,
                "error": str(e)
            }
