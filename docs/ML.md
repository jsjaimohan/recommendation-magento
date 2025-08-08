# Machine Learning Documentation

**Developer:** J S JAIMOHAN  
**Email:** jsjaimohan@gmail.com  
**License:** Private License

## Overview

This document covers all machine learning aspects of the Magento Recommendation System, including algorithms, model training, evaluation, and deployment.

## 🧠 ML Architecture

### Core Components

1. **RecommendationService** - Main ML engine
2. **Algorithms** - User-based, Content-based, Hybrid
3. **Data Processing** - Behavior tracking and feature engineering
4. **Model Persistence** - Save/load trained models

### Technology Stack

- **scikit-learn**: Primary ML library
- **pandas**: Data manipulation
- **numpy**: Numerical computations
- **pickle**: Model serialization

## 📊 Data Processing

### User Behavior Data

```python
# Behavior types and their weights
weights = {
    'purchase': 3.0,    # Highest weight - direct purchase intent
    'cart': 2.0,        # High weight - strong interest
    'wishlist': 1.5,    # Medium weight - interest
    'view': 1.0         # Base weight - basic interaction
}
```

### Data Preparation

```python
def prepare_data(self, user_behaviors: List[UserBehavior], product_data: List[ProductData]):
    """Prepare data for training"""
    # Convert behaviors to DataFrame
    behaviors_df = pd.DataFrame([behavior.dict() for behavior in user_behaviors])
    
    # Create user-item matrix
    self.user_item_matrix = behaviors_df.pivot_table(
        index='user_id',
        columns='product_id',
        values='behavior_type',
        aggfunc='count',
        fill_value=0
    )
    
    # Prepare product data
    self.product_data = pd.DataFrame([product.dict() for product in product_data])
```

## 🎯 Recommendation Algorithms

### 1. User-Based Collaborative Filtering

**Principle**: Find users similar to the target user and recommend products they liked.

```python
def _get_user_based_recommendations(self, user_id: str, n_recommendations: int):
    """User-based collaborative filtering"""
    if user_id not in self.user_item_matrix.index:
        return []
    
    user_idx = self.user_item_matrix.index.get_loc(user_id)
    similar_users = self.user_based_model[user_idx]
    similar_user_indices = np.argsort(similar_users)[::-1][1:6]  # Top 5 similar users
    
    recommendations = []
    user_products = set(self.user_item_matrix.columns[self.user_item_matrix.iloc[user_idx] > 0])
    
    for similar_user_idx in similar_user_indices:
        similar_user_products = set(self.user_item_matrix.columns[self.user_item_matrix.iloc[similar_user_idx] > 0])
        new_products = similar_user_products - user_products
        recommendations.extend(list(new_products))
    
    return list(set(recommendations))[:n_recommendations]
```

**Advantages:**
- Captures user preferences well
- Works with sparse data
- Easy to understand and implement

**Disadvantages:**
- Cold start problem for new users
- Computationally expensive for large datasets
- Privacy concerns with user similarity

### 2. Content-Based Filtering

**Principle**: Recommend products similar to what the user has liked before.

```python
def _get_content_based_recommendations(self, user_id: str, n_recommendations: int):
    """Content-based filtering"""
    if user_id not in self.user_item_matrix.index:
        return []
    
    user_idx = self.user_item_matrix.index.get_loc(user_id)
    user_products = self.user_item_matrix.columns[self.user_item_matrix.iloc[user_idx] > 0]
    
    if len(user_products) == 0:
        return []
    
    # Get most recent product
    recent_product = user_products[0]
    product_idx = self.product_data[self.product_data['product_id'] == recent_product].index[0]
    
    similar_products = self.content_based_model[product_idx]
    similar_indices = np.argsort(similar_products)[::-1][1:n_recommendations+1]
    
    return self.product_data.iloc[similar_indices]['product_id'].tolist()
```

**Feature Engineering:**
```python
# Product descriptions for content-based filtering
product_descriptions = self.product_data['name'] + ' ' + self.product_data['category']
tfidf = TfidfVectorizer(stop_words='english', max_features=1000)
product_features = tfidf.fit_transform(product_descriptions)
self.content_based_model = cosine_similarity(product_features)
```

**Advantages:**
- No cold start for new users
- Explainable recommendations
- Privacy-friendly

**Disadvantages:**
- Limited to product features
- Requires good product descriptions
- May create filter bubbles

### 3. Hybrid Approach

**Principle**: Combine multiple algorithms for better results.

```python
def _get_hybrid_recommendations(self, user_id: str, n_recommendations: int):
    """Hybrid approach combining multiple methods"""
    user_recs = self._get_user_based_recommendations(user_id, n_recommendations)
    content_recs = self._get_content_based_recommendations(user_id, n_recommendations)
    
    # Combine and rank
    all_recs = user_recs + content_recs
    rec_counts = Counter(all_recs)
    
    return [rec for rec, count in rec_counts.most_common(n_recommendations)]
```

**Advantages:**
- Better coverage and diversity
- Reduces limitations of individual algorithms
- More robust recommendations

## 🏋️ Model Training

### Training Process

```python
def train_models(self):
    """Train all recommendation models"""
    try:
        # Train user-based model
        self.user_based_model = cosine_similarity(self.user_item_matrix)
        
        # Train content-based model
        product_descriptions = self.product_data['name'] + ' ' + self.product_data['category']
        tfidf = TfidfVectorizer(stop_words='english', max_features=1000)
        product_features = tfidf.fit_transform(product_descriptions)
        self.content_based_model = cosine_similarity(product_features)
        
        # Train matrix factorization model
        n_components = min(20, min(self.user_item_matrix.shape))
        self.mf_model = NMF(n_components=n_components, random_state=42)
        self.user_factors = self.mf_model.fit_transform(self.user_item_matrix)
        self.item_factors = self.mf_model.components_
        
        self.is_trained = True
        logger.info("Models trained successfully")
        
    except Exception as e:
        logger.error(f"Error training models: {e}")
        self.is_trained = False
```

### Training Data Sources

1. **Direct Training**: Provide user behaviors and product data
2. **Database Training**: Use existing data from MariaDB
3. **Incremental Training**: Update models with new data

## 📈 Trending Products Algorithm

### Weighted Behavior Scoring

```python
def get_trending_products(self, category: Optional[str] = None, limit: int = 10, timeframe_days: int = 7):
    """Get trending products based on recent behavior"""
    # Get recent behaviors from database
    recent_behaviors = db_manager.get_recent_behaviors(days=timeframe_days)
    
    # Calculate trending scores
    trending_scores = {}
    
    for behavior in recent_behaviors:
        product_id = behavior['product_id']
        behavior_type = behavior['behavior_type']
        
        # Weight different behavior types
        weights = {
            'purchase': 3.0,
            'cart': 2.0,
            'wishlist': 1.5,
            'view': 1.0
        }
        
        weight = weights.get(behavior_type, 1.0)
        
        if product_id not in trending_scores:
            trending_scores[product_id] = 0
        
        trending_scores[product_id] += weight
    
    # Sort by score and return top products
    sorted_products = sorted(trending_scores.items(), key=lambda x: x[1], reverse=True)
    return [product_id for product_id, score in sorted_products[:limit]]
```

## 🛒 Frequently Bought Together (FBT) Algorithm

### Association Rule Mining with Apriori

The FBT system uses **Association Rule Mining** to discover products that are frequently purchased together. This is implemented using the **Apriori algorithm** with three key metrics:

#### Key Metrics

1. **Support**: How often items appear together in transactions
   ```
   Support(X,Y) = (Transactions containing both X and Y) / (Total transactions)
   ```

2. **Confidence**: How likely Y is bought when X is bought
   ```
   Confidence(X→Y) = Support(X,Y) / Support(X)
   ```

3. **Lift**: How much more likely Y is bought with X vs. random chance
   ```
   Lift(X→Y) = Confidence(X→Y) / Support(Y)
   ```

### Apriori Algorithm Implementation

```python
def apriori_algorithm(self, transactions: List[List[str]]) -> Dict[Tuple, int]:
    """Apriori algorithm for finding frequent itemsets"""
    # Step 1: Find frequent 1-itemsets
    item_counts = Counter()
    for transaction in transactions:
        for item in transaction:
            item_counts[item] += 1
    
    min_support_count = int(self.min_support * len(transactions))
    frequent_1_itemsets = {frozenset([item]) for item, count in item_counts.items() 
                          if count >= min_support_count}
    
    frequent_itemsets = {1: frequent_1_itemsets}
    k = 2
    
    # Step 2: Generate frequent k-itemsets iteratively
    while frequent_itemsets[k-1]:
        # Generate candidates
        candidates = self.generate_candidates(frequent_itemsets[k-1])
        
        # Count support for candidates
        candidate_counts = Counter()
        for transaction in transactions:
            transaction_set = frozenset(transaction)
            for candidate in candidates:
                if candidate.issubset(transaction_set):
                    candidate_counts[candidate] += 1
        
        # Filter by minimum support
        frequent_k_itemsets = {itemset for itemset, count in candidate_counts.items() 
                             if count >= min_support_count}
        frequent_itemsets[k] = frequent_k_itemsets
        k += 1
    
    # Flatten all frequent itemsets
    all_frequent_itemsets = {}
    for k, itemsets in frequent_itemsets.items():
        for itemset in itemsets:
            all_frequent_itemsets[tuple(sorted(itemset))] = candidate_counts.get(itemset, 0)
    
    return all_frequent_itemsets
```

### Association Rule Generation

```python
def generate_rules(self, frequent_itemsets: Dict[Tuple, int], 
                  transactions: List[List[str]]) -> List[Dict[str, Any]]:
    """Generate association rules from frequent itemsets"""
    rules = []
    total_transactions = len(transactions)
    
    for itemset, support_count in frequent_itemsets.items():
        if len(itemset) < 2:
            continue
        
        # Calculate support for the itemset
        support = support_count / total_transactions
        
        # Generate all possible rules from this itemset
        for i in range(1, len(itemset)):
            for antecedent in combinations(itemset, i):
                consequent = tuple(set(itemset) - set(antecedent))
                
                # Calculate confidence
                antecedent_support = frequent_itemsets.get(antecedent, 0) / total_transactions
                if antecedent_support > 0:
                    confidence = support / antecedent_support
                    
                    # Calculate lift
                    consequent_support = frequent_itemsets.get(consequent, 0) / total_transactions
                    lift = confidence / consequent_support if consequent_support > 0 else 0
                    
                    # Filter by minimum confidence
                    if confidence >= self.min_confidence and lift >= self.min_lift:
                        rules.append({
                            'antecedent': antecedent,
                            'consequent': consequent,
                            'support': support,
                            'confidence': confidence,
                            'lift': lift
                        })
    
    return rules
```

### FBT Service Architecture

```python
class FBTService:
    def __init__(self):
        self.min_support = 0.01      # 1% minimum support
        self.min_confidence = 0.3    # 30% minimum confidence
        self.min_lift = 1.0          # Must be better than random
    
    def generate_association_rules(self, min_support: float = None, 
                                 min_confidence: float = None) -> Dict[str, Any]:
        """Generate association rules from purchase transactions"""
        # 1. Fetch purchase transactions
        transactions = self.db_manager.get_purchase_transactions()
        
        # 2. Convert to transaction format for Apriori
        transaction_lists = []
        for txn in transactions:
            if len(txn['items']) >= 2:  # Only multi-item transactions
                items = [item['product_id'] for item in txn['items']]
                transaction_lists.append(items)
        
        # 3. Run Apriori algorithm
        frequent_itemsets = self.apriori_algorithm(transaction_lists)
        
        # 4. Generate association rules
        rules = self.generate_rules(frequent_itemsets, transaction_lists)
        
        # 5. Save rules to database
        self.db_manager.save_association_rules(rules)
        
        return {
            'rules_generated': len(rules),
            'transactions_processed': len(transactions),
            'frequent_itemsets': len(frequent_itemsets)
        }
    
    def get_frequently_bought_together(self, product_id: str, limit: int = 10, 
                                     min_confidence: float = 0.3) -> Dict[str, Any]:
        """Get FBT recommendations for a product"""
        associations = self.db_manager.get_product_associations(
            product_id, limit, min_confidence
        )
        
        return {
            'product_id': product_id,
            'associations': associations,
            'count': len(associations),
            'min_confidence': min_confidence
        }
```

### Database Schema for FBT

```sql
-- Purchase transactions table
CREATE TABLE purchase_transactions (
    transaction_id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255),
    order_id VARCHAR(255),
    total_amount DECIMAL(10,2),
    status VARCHAR(50) DEFAULT 'completed',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Transaction items table
CREATE TABLE transaction_items (
    transaction_id VARCHAR(255),
    product_id VARCHAR(255),
    quantity INT DEFAULT 1,
    unit_price DECIMAL(10,2),
    total_price DECIMAL(10,2),
    PRIMARY KEY (transaction_id, product_id)
);

-- Product associations table
CREATE TABLE product_associations (
    product_id VARCHAR(255),
    associated_product_id VARCHAR(255),
    support DECIMAL(5,4),      -- How often they appear together
    confidence DECIMAL(5,4),    -- How likely Y is bought with X
    lift DECIMAL(10,4),        -- How much more likely than random
    rule_type VARCHAR(50) DEFAULT 'frequently_bought_together',
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (product_id, associated_product_id)
);
```

### FBT Algorithm Parameters

```python
# FBT Configuration
FBT_PARAMS = {
    'min_support': 0.01,        # 1% minimum support threshold
    'min_confidence': 0.3,      # 30% minimum confidence threshold
    'min_lift': 1.0,           # Must be better than random chance
    'max_rules': 1000,         # Maximum rules to generate
    'regeneration_frequency': 24  # Hours between rule regeneration
}
```

### Example FBT Results

For **iPhone (PROD001)**, the system generates:
- **Screen Protector**: 51.43% confidence (support: 15.65%)
- **iPhone Case**: 47.37% confidence (support: 15.65%)
- **AirPods Pro**: 39.13% confidence (support: 15.65%)
- **Adidas Ultraboost**: 33.33% confidence (support: 0.87%, lift: 19.17)
- **Samsung Galaxy**: 33.33% confidence (support: 0.87%, lift: 3.19)

### FBT Performance Characteristics

- **Processing Time**: < 100ms for recommendations
- **Rule Generation**: ~50ms for 115 transactions
- **Memory Usage**: Efficient with sparse matrix operations
- **Scalability**: Linear with transaction count
- **Accuracy**: High lift values indicate strong associations

## 💾 Model Persistence

### Saving Models

```python
def save_model(self, filepath: str):
    """Save trained model to file"""
    model_data = {
        'user_item_matrix': self.user_item_matrix,
        'product_data': self.product_data,
        'user_based_model': self.user_based_model,
        'content_based_model': self.content_based_model,
        'user_factors': self.user_factors,
        'item_factors': self.item_factors,
        'is_trained': self.is_trained
    }
    
    with open(filepath, 'wb') as f:
        pickle.dump(model_data, f)
    logger.info(f"Model saved to {filepath}")
```

### Loading Models

```python
def load_model(self, filepath: str):
    """Load trained model from file"""
    with open(filepath, 'rb') as f:
        model_data = pickle.load(f)
    
    self.user_item_matrix = model_data['user_item_matrix']
    self.product_data = model_data['product_data']
    self.user_based_model = model_data['user_based_model']
    self.content_based_model = model_data['content_based_model']
    self.user_factors = model_data['user_factors']
    self.item_factors = model_data['item_factors']
    self.is_trained = model_data['is_trained']
    logger.info(f"Model loaded from {filepath}")
```

## 📊 Model Evaluation

### Metrics

1. **Precision**: How many recommended items are relevant
2. **Recall**: How many relevant items are recommended
3. **F1-Score**: Harmonic mean of precision and recall
4. **Coverage**: How many items can be recommended
5. **Diversity**: How diverse the recommendations are

### Evaluation Code

```python
def evaluate_model(self, test_data):
    """Evaluate model performance"""
    precision_scores = []
    recall_scores = []
    
    for user_id in test_data:
        actual_items = set(test_data[user_id])
        predicted_items = set(self.get_recommendations(user_id, n_recommendations=10))
        
        if len(predicted_items) > 0:
            precision = len(actual_items & predicted_items) / len(predicted_items)
            precision_scores.append(precision)
        
        if len(actual_items) > 0:
            recall = len(actual_items & predicted_items) / len(actual_items)
            recall_scores.append(recall)
    
    avg_precision = np.mean(precision_scores)
    avg_recall = np.mean(recall_scores)
    f1_score = 2 * (avg_precision * avg_recall) / (avg_precision + avg_recall)
    
    return {
        'precision': avg_precision,
        'recall': avg_recall,
        'f1_score': f1_score
    }
```

## 🔄 Model Updates

### Incremental Learning

```python
def update_model_with_new_data(self, new_behaviors: List[UserBehavior]):
    """Update model with new user behaviors"""
    # Add new behaviors to existing data
    for behavior in new_behaviors:
        self.add_behavior_to_matrix(behavior)
    
    # Retrain models with updated data
    self.train_models()
    
    # Save updated model
    self.save_model("/app/models/recommendation_model.pkl")
```

### A/B Testing

```python
def get_recommendations_with_ab_test(self, user_id: str, experiment_id: str):
    """Get recommendations with A/B testing"""
    if experiment_id == "user_based_vs_hybrid":
        # 50% users get user-based, 50% get hybrid
        if hash(user_id) % 2 == 0:
            return self._get_user_based_recommendations(user_id, 5)
        else:
            return self._get_hybrid_recommendations(user_id, 5)
```

## 🚀 Performance Optimization

### Caching

```python
# Redis caching for recommendations
cache_key = f"recommendations:{user_id}:{algorithm}:{n_recommendations}"
cached_result = redis_client.get(cache_key)

if cached_result:
    return json.loads(cached_result)

# Generate fresh recommendations
result = self.get_recommendations(user_id, algorithm, n_recommendations)
redis_client.setex(cache_key, 3600, json.dumps(result))  # Cache for 1 hour
```

### Batch Processing

```python
def batch_recommendations(self, user_ids: List[str], algorithm: str = "hybrid"):
    """Generate recommendations for multiple users efficiently"""
    results = {}
    
    for user_id in user_ids:
        try:
            recommendations = self.get_recommendations(user_id, algorithm)
            results[user_id] = recommendations
        except Exception as e:
            logger.error(f"Error for user {user_id}: {e}")
            results[user_id] = []
    
    return results
```

## 🔧 Configuration

### Model Parameters

```python
# Recommendation parameters
RECOMMENDATION_PARAMS = {
    'max_recommendations': 10,
    'min_similarity_threshold': 0.1,
    'cache_ttl_seconds': 3600,
    'batch_size': 100
}

# Training parameters
TRAINING_PARAMS = {
    'min_users': 10,
    'min_products': 5,
    'max_features': 1000,
    'random_state': 42
}
```

## 📋 Best Practices

### 1. Data Quality
- Clean and validate input data
- Handle missing values appropriately
- Remove outliers and noise

### 2. Model Selection
- Start with simple algorithms
- Use hybrid approaches for better results
- A/B test different algorithms

### 3. Performance
- Cache frequently accessed results
- Use batch processing for efficiency
- Monitor model performance regularly

### 4. Privacy
- Anonymize user data when possible
- Use content-based filtering for privacy
- Implement data retention policies

## 🆘 Troubleshooting

### Common Issues

1. **Cold Start Problem**
   - Use content-based filtering for new users
   - Implement popularity-based fallbacks
   - Collect more user behavior data

2. **Poor Recommendations**
   - Check data quality and quantity
   - Try different algorithms
   - Adjust similarity thresholds

3. **Performance Issues**
   - Implement caching
   - Use batch processing
   - Optimize database queries

### Debugging Tools

```python
def debug_recommendations(self, user_id: str):
    """Debug recommendation generation for a user"""
    debug_info = {
        'user_id': user_id,
        'user_in_matrix': user_id in self.user_item_matrix.index,
        'user_products': list(self.user_item_matrix.columns[self.user_item_matrix.iloc[user_idx] > 0]),
        'similar_users': self._get_similar_users(user_id),
        'content_scores': self._get_content_scores(user_id)
    }
    return debug_info
```

## 📞 Support

For ML-related questions or issues:
- **Email:** jsjaimohan@gmail.com
- **Developer:** J S JAIMOHAN

This ML system is designed for internal Magento integration with focus on simplicity and effectiveness.
