"""
Frequently Bought Together (FBT) Service
Implements association rules using Apriori algorithm
"""

import logging
import time
from typing import List, Dict, Any, Set, Tuple
from itertools import combinations
from collections import defaultdict, Counter
import json
from database import db_manager

logger = logging.getLogger(__name__)

class FBTService:
    """Frequently Bought Together service using Association Rules"""
    
    def __init__(self):
        self.db_manager = db_manager
        self.min_support = 0.01  # 1% minimum support
        self.min_confidence = 0.3  # 30% minimum confidence
        self.min_lift = 1.0  # Minimum lift threshold
    
    def generate_association_rules(self, min_support: float = None, min_confidence: float = None) -> Dict[str, Any]:
        """
        Generate association rules from purchase transactions
        """
        try:
            start_time = time.time()
            
            # Override defaults if provided
            if min_support is not None:
                self.min_support = min_support
            if min_confidence is not None:
                self.min_confidence = min_confidence
            
            logger.info(f"Starting FBT rule generation with min_support={self.min_support}, min_confidence={self.min_confidence}")
            
            # Get purchase transactions
            transactions = self.db_manager.get_purchase_transactions(limit=50000, days=365)
            
            if not transactions:
                logger.warning("No purchase transactions found for FBT analysis")
                return {
                    "status": "error",
                    "message": "No purchase transactions found",
                    "rules_generated": 0,
                    "execution_time": time.time() - start_time
                }
            
            # Convert to transaction format for Apriori
            transaction_lists = []
            for txn in transactions:
                if txn.get("items"):
                    products = [item["product_id"] for item in txn["items"]]
                    if len(products) > 1:  # Only transactions with multiple products
                        transaction_lists.append(products)
            
            if not transaction_lists:
                logger.warning("No multi-product transactions found")
                return {
                    "status": "error",
                    "message": "No multi-product transactions found",
                    "rules_generated": 0,
                    "execution_time": time.time() - start_time
                }
            
            logger.info(f"Processing {len(transaction_lists)} multi-product transactions")
            
            # Generate frequent itemsets
            frequent_itemsets = self.apriori_algorithm(transaction_lists)
            
            # Generate association rules
            rules = self.generate_rules(frequent_itemsets, transaction_lists)
            
            # Save to database
            if rules:
                self.db_manager.save_association_rules(rules)
                logger.info(f"Saved {len(rules)} association rules to database")
            
            execution_time = time.time() - start_time
            
            return {
                "status": "success",
                "rules_generated": len(rules),
                "transactions_processed": len(transaction_lists),
                "frequent_itemsets": len(frequent_itemsets),
                "min_support": self.min_support,
                "min_confidence": self.min_confidence,
                "execution_time": execution_time
            }
            
        except Exception as e:
            logger.error(f"Error generating association rules: {e}")
            return {
                "status": "error",
                "message": f"Error generating rules: {str(e)}",
                "rules_generated": 0,
                "execution_time": time.time() - start_time
            }
    
    def apriori_algorithm(self, transactions: List[List[str]]) -> Dict[Tuple, int]:
        """
        Apriori algorithm for finding frequent itemsets
        """
        # Count single items
        item_counts = Counter()
        for transaction in transactions:
            for item in transaction:
                item_counts[item] += 1
        
        total_transactions = len(transactions)
        min_support_count = int(self.min_support * total_transactions)
        
        # Find frequent 1-itemsets
        frequent_1_itemsets = {frozenset([item]) for item, count in item_counts.items() 
                              if count >= min_support_count}
        
        frequent_itemsets = {}
        k = 1
        
        while frequent_1_itemsets:
            # Count k-itemsets
            k_itemset_counts = Counter()
            
            for transaction in transactions:
                transaction_set = frozenset(transaction)
                for itemset in frequent_1_itemsets:
                    if itemset.issubset(transaction_set):
                        k_itemset_counts[itemset] += 1
            
            # Filter by minimum support
            frequent_k_itemsets = {itemset for itemset, count in k_itemset_counts.items() 
                                 if count >= min_support_count}
            
            # Store frequent itemsets
            for itemset in frequent_k_itemsets:
                frequent_itemsets[itemset] = k_itemset_counts[itemset]
            
            # Generate candidate (k+1)-itemsets
            if frequent_k_itemsets:
                candidate_itemsets = self.generate_candidates(frequent_k_itemsets)
                frequent_1_itemsets = candidate_itemsets
                k += 1
            else:
                break
        
        return frequent_itemsets
    
    def generate_candidates(self, frequent_itemsets: Set[frozenset]) -> Set[frozenset]:
        """
        Generate candidate itemsets for next iteration
        """
        candidates = set()
        
        for itemset1 in frequent_itemsets:
            for itemset2 in frequent_itemsets:
                if itemset1 != itemset2:
                    # Union of two itemsets
                    union = itemset1.union(itemset2)
                    
                    if len(union) == len(itemset1) + 1:
                        # Check if all subsets are frequent
                        all_subsets_frequent = True
                        for item in union:
                            subset = union - {item}
                            if subset not in frequent_itemsets:
                                all_subsets_frequent = False
                                break
                        
                        if all_subsets_frequent:
                            candidates.add(union)
        
        return candidates
    
    def generate_rules(self, frequent_itemsets: Dict[Tuple, int], 
                      transactions: List[List[str]]) -> List[Dict[str, Any]]:
        """
        Generate association rules from frequent itemsets
        """
        rules = []
        total_transactions = len(transactions)
        
        # Calculate support for all items
        item_counts = Counter()
        for transaction in transactions:
            for item in transaction:
                item_counts[item] += 1
        
        for itemset, support_count in frequent_itemsets.items():
            if len(itemset) >= 2:
                support = support_count / total_transactions
                
                # Generate all possible rules from this itemset
                for i in range(1, len(itemset)):
                    for antecedent in combinations(itemset, i):
                        antecedent_set = frozenset(antecedent)
                        consequent = itemset - antecedent_set
                        
                        # Calculate confidence
                        antecedent_count = item_counts.get(list(antecedent)[0], 0)
                        if antecedent_count > 0:
                            confidence = support_count / antecedent_count
                            
                            # Calculate lift
                            consequent_count = item_counts.get(list(consequent)[0], 0)
                            if consequent_count > 0:
                                lift = (support_count * total_transactions) / (antecedent_count * consequent_count)
                            else:
                                lift = 0
                            
                            if confidence >= self.min_confidence and lift >= self.min_lift:
                                rule = {
                                    "antecedent": list(antecedent),
                                    "consequent": list(consequent),
                                    "support": support,
                                    "confidence": confidence,
                                    "lift": lift
                                }
                                rules.append(rule)
        
        return rules
    
    def get_frequently_bought_together(self, product_id: str, limit: int = 10, 
                                     min_confidence: float = 0.3) -> Dict[str, Any]:
        """
        Get frequently bought together products for a given product
        """
        try:
            start_time = time.time()
            
            associations = self.db_manager.get_product_associations(
                product_id, limit=limit, min_confidence=min_confidence
            )
            
            execution_time = time.time() - start_time
            
            return {
                "product_id": product_id,
                "associations": associations,
                "count": len(associations),
                "min_confidence": min_confidence,
                "execution_time": execution_time
            }
            
        except Exception as e:
            logger.error(f"Error getting FBT for product {product_id}: {e}")
            return {
                "product_id": product_id,
                "associations": [],
                "count": 0,
                "error": str(e),
                "execution_time": time.time() - start_time
            }
    
    def get_all_association_rules(self, min_confidence: float = 0.3, limit: int = 1000) -> Dict[str, Any]:
        """
        Get all association rules for analysis
        """
        try:
            start_time = time.time()
            
            rules = self.db_manager.get_all_association_rules(min_confidence, limit)
            
            execution_time = time.time() - start_time
            
            return {
                "rules": rules,
                "count": len(rules),
                "min_confidence": min_confidence,
                "execution_time": execution_time
            }
            
        except Exception as e:
            logger.error(f"Error getting all association rules: {e}")
            return {
                "rules": [],
                "count": 0,
                "error": str(e),
                "execution_time": time.time() - start_time
            }
    
    def clear_association_rules(self) -> Dict[str, Any]:
        """
        Clear all association rules (useful for regeneration)
        """
        try:
            success = self.db_manager.clear_association_rules()
            
            return {
                "status": "success" if success else "error",
                "message": "Association rules cleared" if success else "Failed to clear rules"
            }
            
        except Exception as e:
            logger.error(f"Error clearing association rules: {e}")
            return {
                "status": "error",
                "message": f"Error clearing rules: {str(e)}"
            }
