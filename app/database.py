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
                
                # Insert behavior with transaction_id support
                session.execute(
                    text("""
                        INSERT INTO user_behaviors 
                        (user_id, product_id, behavior_type, session_id, transaction_id, timestamp, metadata)
                        VALUES (:user_id, :product_id, :behavior_type, :session_id, :transaction_id, :timestamp, :metadata)
                    """),
                    {
                        "user_id": behavior_data["user_id"],
                        "product_id": behavior_data["product_id"],
                        "behavior_type": behavior_data["behavior_type"],
                        "session_id": behavior_data.get("session_id"),
                        "transaction_id": behavior_data.get("transaction_id"),
                        "timestamp": behavior_data.get("timestamp", datetime.now()),
                        "metadata": json.dumps(behavior_data.get("metadata", {}))
                    }
                )
                session.commit()
                return True
        except SQLAlchemyError as e:
            logger.error(f"Error saving user behavior: {e}")
            return False
    
    # FBT-SPECIFIC METHODS
    
    def save_purchase_transaction(self, transaction_data: Dict[str, Any]) -> bool:
        """Save purchase transaction to database"""
        try:
            with self.SessionLocal() as session:
                # Save transaction
                session.execute(
                    text("""
                        INSERT INTO purchase_transactions 
                        (transaction_id, user_id, order_id, total_amount, status)
                        VALUES (:transaction_id, :user_id, :order_id, :total_amount, :status)
                    """),
                    {
                        "transaction_id": transaction_data["transaction_id"],
                        "user_id": transaction_data["user_id"],
                        "order_id": transaction_data["order_id"],
                        "total_amount": transaction_data["total_amount"],
                        "status": transaction_data.get("status", "completed")
                    }
                )
                
                # Save transaction items
                for item in transaction_data.get("items", []):
                    session.execute(
                        text("""
                            INSERT INTO transaction_items 
                            (transaction_id, product_id, quantity, unit_price, total_price)
                            VALUES (:transaction_id, :product_id, :quantity, :unit_price, :total_price)
                        """),
                        {
                            "transaction_id": transaction_data["transaction_id"],
                            "product_id": item["product_id"],
                            "quantity": item.get("quantity", 1),
                            "unit_price": item.get("unit_price", 0),
                            "total_price": item.get("total_price", 0)
                        }
                    )
                
                session.commit()
                return True
        except SQLAlchemyError as e:
            logger.error(f"Error saving purchase transaction: {e}")
            return False
    
    def get_purchase_transactions(self, limit: int = 10000, days: int = 365) -> List[Dict[str, Any]]:
        """Get purchase transactions with items for FBT analysis"""
        try:
            with self.SessionLocal() as session:
                result = session.execute(
                    text("""
                        SELECT 
                            pt.transaction_id, pt.user_id, pt.order_id, 
                            pt.purchase_date, pt.total_amount, pt.status,
                            ti.product_id, ti.quantity, ti.unit_price, ti.total_price
                        FROM purchase_transactions pt
                        LEFT JOIN transaction_items ti ON pt.transaction_id = ti.transaction_id
                        WHERE pt.purchase_date >= DATE_SUB(NOW(), INTERVAL :days DAY)
                        ORDER BY pt.purchase_date DESC
                        LIMIT :limit
                    """),
                    {"limit": limit, "days": days}
                )
                
                # Group by transaction
                transactions = {}
                for row in result:
                    if row.transaction_id not in transactions:
                        transactions[row.transaction_id] = {
                            "transaction_id": row.transaction_id,
                            "user_id": row.user_id,
                            "order_id": row.order_id,
                            "purchase_date": row.purchase_date.isoformat() if row.purchase_date else None,
                            "total_amount": float(row.total_amount) if row.total_amount else 0,
                            "status": row.status,
                            "items": []
                        }
                    
                    if row.product_id:
                        transactions[row.transaction_id]["items"].append({
                            "product_id": row.product_id,
                            "quantity": row.quantity,
                            "unit_price": float(row.unit_price) if row.unit_price else 0,
                            "total_price": float(row.total_price) if row.total_price else 0
                        })
                
                return list(transactions.values())
                
        except SQLAlchemyError as e:
            logger.error(f"Error getting purchase transactions: {e}")
            return []
    
    def save_association_rules(self, rules: List[Dict[str, Any]]) -> bool:
        """Save association rules to database"""
        try:
            with self.SessionLocal() as session:
                for rule in rules:
                    # Save each product pair
                    for antecedent_product in rule["antecedent"]:
                        for consequent_product in rule["consequent"]:
                            # Use REPLACE INTO instead of INSERT ... ON DUPLICATE KEY UPDATE
                            session.execute(
                                text("""
                                    REPLACE INTO product_associations 
                                    (product_id, associated_product_id, support, confidence, lift)
                                    VALUES (:product_id, :associated_product_id, :support, :confidence, :lift)
                                """),
                                {
                                    "product_id": antecedent_product,
                                    "associated_product_id": consequent_product,
                                    "support": rule["support"],
                                    "confidence": rule["confidence"],
                                    "lift": rule["lift"]
                                }
                            )
                session.commit()
                return True
        except SQLAlchemyError as e:
            logger.error(f"Error saving association rules: {e}")
            return False
    
    def get_product_associations(self, product_id: str, limit: int = 10, min_confidence: float = 0.3) -> List[Dict[str, Any]]:
        """Get frequently bought together products for a given product"""
        try:
            with self.SessionLocal() as session:
                result = session.execute(
                    text("""
                        SELECT 
                            pa.associated_product_id,
                            pa.support,
                            pa.confidence,
                            pa.lift,
                            p.name as product_name,
                            p.category,
                            p.price
                        FROM product_associations pa
                        JOIN products p ON pa.associated_product_id = p.product_id
                        WHERE pa.product_id = :product_id 
                        AND pa.confidence >= :min_confidence
                        ORDER BY pa.confidence DESC, pa.lift DESC
                        LIMIT :limit
                    """),
                    {
                        "product_id": product_id,
                        "min_confidence": min_confidence,
                        "limit": limit
                    }
                )
                
                associations = []
                for row in result:
                    associations.append({
                        "product_id": row.associated_product_id,
                        "product_name": row.product_name,
                        "category": row.category,
                        "price": float(row.price) if row.price else 0,
                        "support": float(row.support),
                        "confidence": float(row.confidence),
                        "lift": float(row.lift)
                    })
                
                return associations
                
        except SQLAlchemyError as e:
            logger.error(f"Error getting product associations: {e}")
            return []
    
    def get_all_association_rules(self, min_confidence: float = 0.3, limit: int = 1000) -> List[Dict[str, Any]]:
        """Get all association rules for analysis"""
        try:
            with self.SessionLocal() as session:
                result = session.execute(
                    text("""
                        SELECT 
                            pa.product_id,
                            pa.associated_product_id,
                            pa.support,
                            pa.confidence,
                            pa.lift,
                            p1.name as product_name,
                            p2.name as associated_product_name
                        FROM product_associations pa
                        JOIN products p1 ON pa.product_id = p1.product_id
                        JOIN products p2 ON pa.associated_product_id = p2.product_id
                        WHERE pa.confidence >= :min_confidence
                        ORDER BY pa.confidence DESC, pa.lift DESC
                        LIMIT :limit
                    """),
                    {
                        "min_confidence": min_confidence,
                        "limit": limit
                    }
                )
                
                rules = []
                for row in result:
                    rules.append({
                        "product_id": row.product_id,
                        "associated_product_id": row.associated_product_id,
                        "product_name": row.product_name,
                        "associated_product_name": row.associated_product_name,
                        "support": float(row.support),
                        "confidence": float(row.confidence),
                        "lift": float(row.lift)
                    })
                
                return rules
                
        except SQLAlchemyError as e:
            logger.error(f"Error getting all association rules: {e}")
            return []
    
    def clear_association_rules(self) -> bool:
        """Clear all association rules (useful for regeneration)"""
        try:
            with self.SessionLocal() as session:
                session.execute(text("DELETE FROM product_associations"))
                session.commit()
                return True
        except SQLAlchemyError as e:
            logger.error(f"Error clearing association rules: {e}")
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
    
    def create_product(self, product_data: Dict[str, Any]) -> bool:
        """Create a new product in the database"""
        try:
            with self.SessionLocal() as session:
                # Check if product already exists
                existing_product = session.execute(
                    text("SELECT 1 FROM products WHERE product_id = :product_id"),
                    {"product_id": product_data["product_id"]}
                ).fetchone()
                
                if existing_product:
                    logger.warning(f"Product {product_data['product_id']} already exists")
                    return False
                
                # Insert new product
                session.execute(
                    text("""
                        INSERT INTO products 
                        (product_id, name, category, subcategory, price, attributes, 
                         description, brand, tags, status, created_at, updated_at)
                        VALUES (:product_id, :name, :category, :subcategory, :price, :attributes,
                                :description, :brand, :tags, 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                    """),
                    {
                        "product_id": product_data["product_id"],
                        "name": product_data["name"],
                        "category": product_data["category"],
                        "subcategory": product_data.get("subcategory"),
                        "price": product_data.get("price"),
                        "attributes": json.dumps(product_data.get("attributes", {})),
                        "description": product_data.get("description"),
                        "brand": product_data.get("brand"),
                        "tags": json.dumps(product_data.get("tags", []))
                    }
                )
                session.commit()
                logger.info(f"Product {product_data['product_id']} created successfully")
                return True
                
        except SQLAlchemyError as e:
            logger.error(f"Error creating product: {e}")
            return False
    
    def update_product(self, product_id: str, product_data: Dict[str, Any]) -> bool:
        """Update an existing product in the database"""
        try:
            with self.SessionLocal() as session:
                # Check if product exists
                existing_product = session.execute(
                    text("SELECT 1 FROM products WHERE product_id = :product_id"),
                    {"product_id": product_id}
                ).fetchone()
                
                if not existing_product:
                    logger.warning(f"Product {product_id} does not exist")
                    return False
                
                # Build update query dynamically
                update_fields = []
                params = {"product_id": product_id}
                
                if "name" in product_data:
                    update_fields.append("name = :name")
                    params["name"] = product_data["name"]
                
                if "category" in product_data:
                    update_fields.append("category = :category")
                    params["category"] = product_data["category"]
                
                if "subcategory" in product_data:
                    update_fields.append("subcategory = :subcategory")
                    params["subcategory"] = product_data["subcategory"]
                
                if "price" in product_data:
                    update_fields.append("price = :price")
                    params["price"] = product_data["price"]
                
                if "attributes" in product_data:
                    update_fields.append("attributes = :attributes")
                    params["attributes"] = json.dumps(product_data["attributes"])
                
                if "description" in product_data:
                    update_fields.append("description = :description")
                    params["description"] = product_data["description"]
                
                if "brand" in product_data:
                    update_fields.append("brand = :brand")
                    params["brand"] = product_data["brand"]
                
                if "tags" in product_data:
                    update_fields.append("tags = :tags")
                    params["tags"] = json.dumps(product_data["tags"])
                
                if not update_fields:
                    logger.warning("No fields to update")
                    return False
                
                update_fields.append("updated_at = CURRENT_TIMESTAMP")
                
                query = f"""
                    UPDATE products 
                    SET {', '.join(update_fields)}
                    WHERE product_id = :product_id
                """
                
                session.execute(text(query), params)
                session.commit()
                logger.info(f"Product {product_id} updated successfully")
                return True
                
        except SQLAlchemyError as e:
            logger.error(f"Error updating product: {e}")
            return False
    
    def get_product(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific product by ID"""
        try:
            with self.SessionLocal() as session:
                result = session.execute(
                    text("""
                        SELECT product_id, name, category, subcategory, price, attributes,
                               description, brand, tags, status, created_at, updated_at
                        FROM products
                        WHERE product_id = :product_id
                    """),
                    {"product_id": product_id}
                ).fetchone()
                
                if not result:
                    return None
                
                return {
                    "product_id": result.product_id,
                    "name": result.name,
                    "category": result.category,
                    "subcategory": result.subcategory,
                    "price": float(result.price) if result.price else None,
                    "attributes": json.loads(result.attributes) if result.attributes and result.attributes != "{}" else {},
                    "description": result.description,
                    "brand": result.brand,
                    "tags": json.loads(result.tags) if result.tags and result.tags != "[]" else [],
                    "status": result.status,
                    "created_at": result.created_at.isoformat() if result.created_at else None,
                    "updated_at": result.updated_at.isoformat() if result.updated_at else None
                }
                
        except SQLAlchemyError as e:
            logger.error(f"Error getting product: {e}")
            return None
    
    def delete_product(self, product_id: str) -> bool:
        """Soft delete a product (set status to inactive)"""
        try:
            with self.SessionLocal() as session:
                session.execute(
                    text("""
                        UPDATE products 
                        SET status = 'inactive', updated_at = CURRENT_TIMESTAMP
                        WHERE product_id = :product_id
                    """),
                    {"product_id": product_id}
                )
                session.commit()
                logger.info(f"Product {product_id} soft deleted successfully")
                return True
                
        except SQLAlchemyError as e:
            logger.error(f"Error deleting product: {e}")
            return False

# Global database manager instance
db_manager = DatabaseManager()
