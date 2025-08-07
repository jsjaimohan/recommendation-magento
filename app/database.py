"""
Database module for recommendation system
"""

import os
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Dict, Any, Optional
import json
from datetime import datetime

logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "mysql://recommendation_user:password@localhost:3306/recommendations")

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_recycle=300)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class DatabaseManager:
    """Database manager for recommendation system"""
    
    def __init__(self):
        self.engine = engine
        self.SessionLocal = SessionLocal
    
    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            with self.engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            return False
    
    def save_user_behavior(self, behavior_data: Dict[str, Any]) -> bool:
        """Save user behavior to database"""
        try:
            with self.SessionLocal() as session:
                # Check if user exists, create if not
                user_exists = session.execute(
                    text("SELECT 1 FROM users WHERE user_id = :user_id"),
                    {"user_id": behavior_data["user_id"]}
                ).fetchone()
                
                if not user_exists:
                    session.execute(
                        text("""
                            INSERT INTO users (user_id, created_at, updated_at)
                            VALUES (:user_id, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                        """),
                        {"user_id": behavior_data["user_id"]}
                    )
                
                # Check if product exists, create if not
                product_exists = session.execute(
                    text("SELECT 1 FROM products WHERE product_id = :product_id"),
                    {"product_id": behavior_data["product_id"]}
                ).fetchone()
                
                if not product_exists:
                    session.execute(
                        text("""
                            INSERT INTO products (product_id, name, category, created_at, updated_at)
                            VALUES (:product_id, :name, :category, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                        """),
                        {
                            "product_id": behavior_data["product_id"],
                            "name": behavior_data.get("product_name", "Unknown Product"),
                            "category": behavior_data.get("category", "unknown")
                        }
                    )
                
                # Insert behavior
                session.execute(
                    text("""
                        INSERT INTO user_behaviors 
                        (user_id, product_id, behavior_type, session_id, timestamp, metadata)
                        VALUES (:user_id, :product_id, :behavior_type, :session_id, :timestamp, :metadata)
                    """),
                    {
                        "user_id": behavior_data["user_id"],
                        "product_id": behavior_data["product_id"],
                        "behavior_type": behavior_data["behavior_type"],
                        "session_id": behavior_data.get("session_id"),
                        "timestamp": behavior_data.get("timestamp", datetime.now()),
                        "metadata": json.dumps(behavior_data.get("metadata", {})) if behavior_data.get("metadata") else "{}"
                    }
                )
                
                # Update user's last_active_at
                session.execute(
                    text("UPDATE users SET last_active_at = CURRENT_TIMESTAMP WHERE user_id = :user_id"),
                    {"user_id": behavior_data["user_id"]}
                )
                
                session.commit()
                logger.info(f"Behavior saved: {behavior_data['user_id']} -> {behavior_data['product_id']}")
                return True
                
        except SQLAlchemyError as e:
            logger.error(f"Error saving behavior: {e}")
            return False
    
    def get_user_behaviors(self, user_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get user behaviors from database"""
        try:
            with self.SessionLocal() as session:
                result = session.execute(
                    text("""
                        SELECT ub.behavior_id, ub.user_id, ub.product_id, ub.behavior_type,
                               ub.session_id, ub.timestamp, ub.metadata,
                               p.name as product_name, p.category, p.price
                        FROM user_behaviors ub
                        LEFT JOIN products p ON ub.product_id = p.product_id
                        WHERE ub.user_id = :user_id
                        ORDER BY ub.timestamp DESC
                        LIMIT :limit
                    """),
                    {"user_id": user_id, "limit": limit}
                )
                
                behaviors = []
                for row in result:
                    behavior = {
                        "behavior_id": row.behavior_id,
                        "user_id": row.user_id,
                        "product_id": row.product_id,
                        "behavior_type": row.behavior_type,
                        "session_id": row.session_id,
                        "timestamp": row.timestamp.isoformat() if row.timestamp else None,
                        "metadata": json.loads(row.metadata) if row.metadata and row.metadata != "{}" else {},
                        "product_name": row.product_name,
                        "category": row.category,
                        "price": float(row.price) if row.price else None
                    }
                    behaviors.append(behavior)
                
                return behaviors
                
        except SQLAlchemyError as e:
            logger.error(f"Error getting user behaviors: {e}")
            return []
    
    def get_all_behaviors(self, limit: int = 1000) -> List[Dict[str, Any]]:
        """Get all behaviors from database for training"""
        try:
            with self.SessionLocal() as session:
                result = session.execute(
                    text("""
                        SELECT ub.user_id, ub.product_id, ub.behavior_type, ub.timestamp
                        FROM user_behaviors ub
                        ORDER BY ub.timestamp DESC
                        LIMIT :limit
                    """),
                    {"limit": limit}
                )
                
                behaviors = []
                for row in result:
                    behavior = {
                        "user_id": row.user_id,
                        "product_id": row.product_id,
                        "behavior_type": row.behavior_type,
                        "timestamp": row.timestamp.isoformat() if row.timestamp else None
                    }
                    behaviors.append(behavior)
                
                return behaviors
                
        except SQLAlchemyError as e:
            logger.error(f"Error getting all behaviors: {e}")
            return []
    
    def get_all_products(self) -> List[Dict[str, Any]]:
        """Get all products from database"""
        try:
            with self.SessionLocal() as session:
                result = session.execute(
                    text("""
                        SELECT product_id, name, category, subcategory, price, attributes
                        FROM products
                        WHERE status = 'active'
                        ORDER BY name
                    """)
                )
                
                products = []
                for row in result:
                    product = {
                        "product_id": row.product_id,
                        "name": row.name,
                        "category": row.category,
                        "subcategory": row.subcategory,
                        "price": float(row.price) if row.price else None,
                        "attributes": json.loads(row.attributes) if row.attributes and row.attributes != "{}" else {}
                    }
                    products.append(product)
                
                return products
                
        except SQLAlchemyError as e:
            logger.error(f"Error getting products: {e}")
            return []
    
    def get_recent_behaviors(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get recent behaviors from the last N days for trending products"""
        try:
            with self.SessionLocal() as session:
                result = session.execute(
                    text("""
                        SELECT user_id, product_id, behavior_type, timestamp
                        FROM user_behaviors
                        WHERE timestamp >= DATE_SUB(NOW(), INTERVAL :days DAY)
                        ORDER BY timestamp DESC
                    """),
                    {"days": days}
                )
                
                behaviors = []
                for row in result:
                    behavior = {
                        "user_id": row.user_id,
                        "product_id": row.product_id,
                        "behavior_type": row.behavior_type,
                        "timestamp": row.timestamp.isoformat() if row.timestamp else None
                    }
                    behaviors.append(behavior)
                
                logger.info(f"Retrieved {len(behaviors)} recent behaviors from last {days} days")
                return behaviors
                
        except SQLAlchemyError as e:
            logger.error(f"Error getting recent behaviors: {e}")
            return []
    
    def save_recommendation(self, user_id: str, product_id: str, score: float, algorithm: str) -> bool:
        """Save recommendation to database"""
        try:
            with self.SessionLocal() as session:
                session.execute(
                    text("""
                        INSERT INTO recommendations 
                        (user_id, product_id, score, algorithm_used, created_at)
                        VALUES (:user_id, :product_id, :score, :algorithm, CURRENT_TIMESTAMP)
                    """),
                    {
                        "user_id": user_id,
                        "product_id": product_id,
                        "score": score,
                        "algorithm": algorithm
                    }
                )
                session.commit()
                return True
                
        except SQLAlchemyError as e:
            logger.error(f"Error saving recommendation: {e}")
            return False
    
    def get_user_recommendations(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get user's recent recommendations"""
        try:
            with self.SessionLocal() as session:
                result = session.execute(
                    text("""
                        SELECT r.recommendation_id, r.user_id, r.product_id, r.score, 
                               r.algorithm_used, r.created_at,
                               p.name as product_name, p.category, p.price
                        FROM recommendations r
                        LEFT JOIN products p ON r.product_id = p.product_id
                        WHERE r.user_id = :user_id
                        ORDER BY r.created_at DESC
                        LIMIT :limit
                    """),
                    {"user_id": user_id, "limit": limit}
                )
                
                recommendations = []
                for row in result:
                    recommendation = {
                        "recommendation_id": row.recommendation_id,
                        "user_id": row.user_id,
                        "product_id": row.product_id,
                        "score": float(row.score) if row.score else 0.0,
                        "algorithm_used": row.algorithm_used,
                        "created_at": row.created_at.isoformat() if row.created_at else None,
                        "product_name": row.product_name,
                        "category": row.category,
                        "price": float(row.price) if row.price else None
                    }
                    recommendations.append(recommendation)
                
                return recommendations
                
        except SQLAlchemyError as e:
            logger.error(f"Error getting user recommendations: {e}")
            return []
    
    def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """Get user statistics"""
        try:
            with self.SessionLocal() as session:
                # Get behavior counts
                behavior_stats = session.execute(
                    text("""
                        SELECT behavior_type, COUNT(*) as count
                        FROM user_behaviors
                        WHERE user_id = :user_id
                        GROUP BY behavior_type
                    """),
                    {"user_id": user_id}
                ).fetchall()
                
                # Get unique products interacted with
                unique_products = session.execute(
                    text("""
                        SELECT COUNT(DISTINCT product_id) as count
                        FROM user_behaviors
                        WHERE user_id = :user_id
                    """),
                    {"user_id": user_id}
                ).fetchone()
                
                # Get recent activity
                recent_activity = session.execute(
                    text("""
                        SELECT COUNT(*) as count
                        FROM user_behaviors
                        WHERE user_id = :user_id
                        AND timestamp > CURRENT_TIMESTAMP - INTERVAL '7 days'
                    """),
                    {"user_id": user_id}
                ).fetchone()
                
                stats = {
                    "user_id": user_id,
                    "behavior_counts": {row.behavior_type: row.count for row in behavior_stats},
                    "unique_products": unique_products.count if unique_products else 0,
                    "recent_activity_7_days": recent_activity.count if recent_activity else 0
                }
                
                return stats
                
        except SQLAlchemyError as e:
            logger.error(f"Error getting user stats: {e}")
            return {"user_id": user_id, "error": str(e)}

# Global database manager instance
db_manager = DatabaseManager()
