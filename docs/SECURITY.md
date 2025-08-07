# Security Documentation

**Developer:** J S JAIMOHAN  
**Email:** jsjaimohan@gmail.com  
**License:** Private License

## Security Overview

This document outlines the security measures implemented in the Magento Recommendation API, particularly for sensitive endpoints that handle user data.

## 🔒 Secured Endpoints

### User Statistics Endpoint (`GET /users/{user_id}/stats`)

This endpoint was identified as potentially exposing sensitive user data and has been secured with multiple layers of protection.

#### **Security Measures Implemented:**

1. **Input Validation**
   - User ID format validation using regex pattern
   - Prevents SQL injection and malicious input
   - Pattern: `^[a-zA-Z0-9_-]{1,50}$`

2. **Rate Limiting**
   - Maximum 10 requests per minute per user
   - Prevents abuse and DoS attacks
   - Returns HTTP 429 when limit exceeded

3. **API Key Authentication**
   - Required API key header: `X-API-Key`
   - Valid keys: `magento-recommendation-key-2024`, `internal-api-key`
   - Returns HTTP 401 if key is missing or invalid

4. **Data Sanitization**
   - Removes sensitive raw data from response
   - Returns only aggregated, non-sensitive statistics
   - Prevents exposure of detailed user behavior patterns

5. **Access Logging**
   - Logs all access attempts with user ID and IP
   - Enables security monitoring and audit trails

#### **Before vs After Security:**

**Before (Unsecured):**
```json
{
  "user_id": "user_123",
  "behavior_counts": {
    "view": 45,
    "cart": 12,
    "purchase": 8,
    "wishlist": 3
  },
  "unique_products": 23,
  "recent_activity_7_days": 15
}
```

**After (Secured):**
```json
{
  "user_id": "user_123",
  "total_interactions": 68,
  "unique_products": 23,
  "recent_activity_7_days": 15,
  "behavior_summary": {
    "view_count": 45,
    "cart_count": 12,
    "purchase_count": 8,
    "wishlist_count": 3
  }
}
```

## 🛡️ Security Features

### 1. **Input Validation**
```python
def validate_user_id(user_id: str) -> bool:
    """Validate user ID format and prevent injection attacks"""
    if not user_id or len(user_id) > 50:
        return False
    return bool(ALLOWED_USER_ID_PATTERN.match(user_id))
```

### 2. **Rate Limiting**
```python
def check_rate_limit(user_id: str) -> bool:
    """Simple rate limiting for user stats endpoint"""
    # Limits to 10 requests per minute per user
```

### 3. **API Key Authentication**
```python
def validate_api_key(x_api_key: Optional[str] = Header(None)) -> bool:
    """Validate API key for sensitive endpoints"""
    valid_keys = ["magento-recommendation-key-2024", "internal-api-key"]
    return x_api_key in valid_keys
```

### 4. **Data Sanitization**
- Removes raw behavior data
- Returns only aggregated statistics
- Prevents exposure of sensitive patterns

## 🔐 Usage Examples

### **Secured Access (Correct):**
```bash
curl -X GET "http://localhost:8000/users/user_123/stats" \
  -H "X-API-Key: magento-recommendation-key-2024"
```

**Response:**
```json
{
  "user_id": "user_123",
  "total_interactions": 68,
  "unique_products": 23,
  "recent_activity_7_days": 15,
  "behavior_summary": {
    "view_count": 45,
    "cart_count": 12,
    "purchase_count": 8,
    "wishlist_count": 3
  }
}
```

### **Unauthorized Access (Blocked):**
```bash
curl -X GET "http://localhost:8000/users/user_123/stats"
```

**Response:**
```json
{
  "detail": "API key required for accessing user statistics"
}
```

### **Invalid User ID (Blocked):**
```bash
curl -X GET "http://localhost:8000/users/user@123/stats" \
  -H "X-API-Key: magento-recommendation-key-2024"
```

**Response:**
```json
{
  "detail": "Invalid user ID format"
}
```

## 🚨 Security Best Practices

### 1. **API Key Management**
- Store API keys securely (environment variables)
- Rotate keys regularly
- Use different keys for different environments

### 2. **Rate Limiting**
- Monitor rate limit violations
- Adjust limits based on usage patterns
- Implement IP-based rate limiting for production

### 3. **Logging and Monitoring**
- Monitor access logs for suspicious activity
- Set up alerts for security events
- Regular security audits

### 4. **Data Protection**
- Minimize data exposure
- Encrypt sensitive data at rest
- Use HTTPS in production

## 🔧 Configuration

### **Environment Variables (Recommended):**
```bash
# API Keys
MAGENTO_API_KEY=magento-recommendation-key-2024
INTERNAL_API_KEY=internal-api-key

# Rate Limiting
MAX_REQUESTS_PER_MINUTE=10

# Security
ENABLE_ACCESS_LOGGING=true
```

### **Production Recommendations:**
1. **Use HTTPS** for all API communications
2. **Implement JWT tokens** instead of simple API keys
3. **Add IP whitelisting** for internal endpoints
4. **Use Redis** for distributed rate limiting
5. **Implement proper logging** with structured data
6. **Add request tracing** for debugging

## 📋 Security Checklist

- ✅ Input validation implemented
- ✅ Rate limiting enabled
- ✅ API key authentication required
- ✅ Data sanitization applied
- ✅ Access logging configured
- ✅ Error handling secured
- ✅ SQL injection prevention
- ✅ XSS protection (via FastAPI)

## 🆘 Incident Response

If a security incident occurs:

1. **Immediate Actions:**
   - Review access logs
   - Check for unusual patterns
   - Rotate API keys if compromised

2. **Investigation:**
   - Analyze request patterns
   - Check for data exposure
   - Review system logs

3. **Recovery:**
   - Update security measures
   - Notify affected parties
   - Document lessons learned

## 📞 Security Contact

For security issues or questions:
- **Email:** jsjaimohan@gmail.com
- **Developer:** J S JAIMOHAN

**Note:** This is a private application with limited external access. Security measures are designed for internal Magento integration use cases.
