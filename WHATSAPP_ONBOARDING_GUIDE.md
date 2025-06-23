# WhatsApp Business API Onboarding Guide

## Overview

This application provides two different onboarding flows for WhatsApp Business API integration:

1. **Test/Development Flow** - Public endpoints for testing and development
2. **Production Flow** - Authenticated endpoints for real business use

## 🧪 Test/Development Endpoints (Public)

### Purpose
- Testing the integration flow
- Development and debugging
- Demo purposes
- No authentication required

### Key Endpoints
- `GET /api/whatsapp/onboarding-test` - Test onboarding page
- `POST /api/whatsapp/complete-onboarding-public` - Public onboarding completion
- `GET /api/whatsapp/status-public?business_email=email` - Public status check
- `POST /api/whatsapp/configure-webhook` - Public webhook configuration
- `POST /api/whatsapp/test-messaging` - Public test messaging

### Security Considerations
- ⚠️ **NOT suitable for production use**
- Requires business email parameter for identification
- No authentication or authorization
- Anyone with the email can access the business data

### Usage Example
```bash
# Check status (public)
curl "https://your-domain.com/api/whatsapp/status-public?business_email=test@business.com"

# Complete onboarding (public)
curl -X POST "https://your-domain.com/api/whatsapp/complete-onboarding-public" \
  -H "Content-Type: application/json" \
  -d '{
    "auth_code": "authorization_code_from_facebook",
    "signup_data": {
      "business_id": "business_id",
      "phone_number_id": "phone_number_id",
      "waba_id": "waba_id"
    },
    "business_email": "test@business.com"
  }'
```

## 🔐 Production Endpoints (Authenticated)

### Purpose
- Real business use
- Secure access control
- User-specific data isolation
- Production-ready security

### Key Endpoints
- `GET /api/whatsapp/onboarding-production` - Production onboarding page
- `POST /api/whatsapp/complete-onboarding-auth` - Authenticated onboarding completion
- `GET /api/whatsapp/status-auth` - Authenticated status check
- `POST /api/whatsapp/configure-webhook-auth` - Authenticated webhook configuration
- `POST /api/whatsapp/test-messaging-auth` - Authenticated test messaging

### Security Features
- ✅ **JWT Token Authentication Required**
- User-specific data access
- Automatic business identification from token
- Secure API access control
- Session management

### Authentication Flow
1. User logs in via `/api/auth/login`
2. Receives JWT access token
3. Includes token in `Authorization: Bearer <token>` header
4. Backend validates token and identifies business
5. Operations are performed for the authenticated business only

### Usage Example
```bash
# Step 1: Login to get token
curl -X POST "https://your-domain.com/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@business.com&password=secure_password"

# Response: {"access_token": "jwt_token_here", "token_type": "bearer"}

# Step 2: Use authenticated endpoints
curl -X GET "https://your-domain.com/api/whatsapp/status-auth" \
  -H "Authorization: Bearer jwt_token_here"

# Step 3: Complete onboarding (authenticated)
curl -X POST "https://your-domain.com/api/whatsapp/complete-onboarding-auth" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer jwt_token_here" \
  -d '{
    "auth_code": "authorization_code_from_facebook",
    "signup_data": {
      "business_id": "business_id",
      "phone_number_id": "phone_number_id",
      "waba_id": "waba_id"
    }
  }'
```

## 📊 Comparison Table

| Feature | Test/Development | Production |
|---------|------------------|------------|
| **Authentication** | None | JWT Token Required |
| **Business Identification** | Email Parameter | From JWT Token |
| **Security** | Low | High |
| **Data Isolation** | None | User-specific |
| **Use Case** | Testing/Demo | Real Business |
| **Frontend Access** | `/api/whatsapp/onboarding-test` | `/api/whatsapp/onboarding-production` |

## 🚀 Migration from Test to Production

When moving from development to production:

1. **Update Frontend Code**
   - Change from public endpoints to authenticated endpoints
   - Implement login functionality
   - Add JWT token management
   - Remove business email parameters

2. **Update API Calls**
   ```javascript
   // Before (Test)
   fetch('/api/whatsapp/status-public?business_email=test@business.com')
   
   // After (Production)
   fetch('/api/whatsapp/status-auth', {
     headers: {
       'Authorization': `Bearer ${authToken}`
     }
   })
   ```

3. **Security Considerations**
   - Ensure HTTPS in production
   - Implement proper token storage (secure cookies/localStorage)
   - Add token refresh logic
   - Implement logout functionality

## 🔧 Implementation Details

### Backend Dependencies
- `get_current_business` dependency for authentication
- JWT token validation
- Business repository for data access
- Proper error handling for unauthorized access

### Frontend Requirements
- Login form for user authentication
- Token storage and management
- Automatic token validation
- Redirect to login if unauthorized

### Database Security
- User data is automatically isolated by business ID
- No cross-business data access
- Audit trails for authenticated operations

## 📝 Best Practices

### For Development
- Use test endpoints for initial integration
- Test with multiple business emails
- Validate all error scenarios

### For Production
- Always use authenticated endpoints
- Implement proper session management
- Add comprehensive error handling
- Monitor authentication failures
- Use HTTPS only
- Implement rate limiting
- Add logging for security events

## 🔗 Quick Links

- **Test Onboarding Page**: `https://your-domain.com/api/whatsapp/onboarding-test`
- **Production Onboarding Page**: `https://your-domain.com/api/whatsapp/onboarding-production`
- **API Documentation**: Available via FastAPI docs at `/docs`
- **Authentication Endpoint**: `/api/auth/login`

## 🆘 Troubleshooting

### Common Issues

1. **"Authentication Required" Error**
   - Ensure you're using authenticated endpoints in production
   - Check JWT token is valid and not expired
   - Verify Authorization header format: `Bearer <token>`

2. **"Business Not Found" Error**
   - User must be registered and logged in
   - Check business exists in database
   - Verify JWT token contains correct business information

3. **Token Expired**
   - Implement token refresh logic
   - Redirect user to login page
   - Clear invalid tokens from storage

### Support
For technical support, check the application logs and ensure all environment variables are properly configured. 