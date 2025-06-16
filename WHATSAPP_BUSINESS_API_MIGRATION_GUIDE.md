# WhatsApp Business API Migration Guide
## From Dialog360 to Meta WhatsApp Business API

This guide will help you migrate from Dialog360 to Meta's official WhatsApp Business API.

## Overview

This project has been updated to support both Dialog360 (for backward compatibility) and Meta's WhatsApp Business API. The migration allows for a gradual transition while maintaining existing functionality.

## Key Changes

### 1. New WhatsApp Business Service
- **File**: `app/services/whatsapp_business_service.py`
- **Purpose**: Direct integration with Meta's WhatsApp Business API
- **Key Features**:
  - Send messages directly to Meta's API
  - Webhook verification
  - Business profile management
  - Phone number management

### 2. Updated Webhook Handling
- **New Endpoint**: `/api/whatsapp/webhook` (GET & POST)
- **Legacy Endpoint**: `/api/whatsapp/incoming-whatsapp` (deprecated)
- **Verification**: Automatic webhook verification for Meta's API

### 3. Dual Service Support
- Both Dialog360 and WhatsApp Business API services are supported
- Automatic service detection based on webhook format
- Gradual migration support

## Prerequisites

### 1. Facebook App Setup
1. Create a Facebook App at https://developers.facebook.com/
2. Add WhatsApp Business API product to your app
3. Configure webhook endpoints
4. Generate access tokens

### 2. WhatsApp Business Account
1. Create or link your WhatsApp Business Account
2. Add phone numbers to your WABA
3. Configure business profile

## Environment Variables

Add these new environment variables to your `.env` file:

```env
# WhatsApp Business API Settings
WHATSAPP_ACCESS_TOKEN=your_permanent_access_token_here
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id_here
WHATSAPP_WEBHOOK_VERIFY_TOKEN=your_webhook_verify_token_here
WHATSAPP_BUSINESS_ACCOUNT_ID=your_waba_id_here
WHATSAPP_APP_ID=your_facebook_app_id_here
WHATSAPP_APP_SECRET=your_facebook_app_secret_here
WHATSAPP_API_VERSION=v18.0

# Deprecated Dialog360 Settings (keep during migration)
DIALOG360_API_KEY=your_dialog360_api_key
DIALOG360_API_URL=https://waba-v2.360dialog.io
DIALOG360_PHONE_NUMBER=your_dialog360_phone
```

## Database Changes

The existing database schema supports both services. Key fields in the `businesses` table:

- `api_key`: Now stores WhatsApp Access Token (instead of Dialog360 API key)
- `channel_id`: Now stores Phone Number ID (instead of Dialog360 channel ID)
- `api_endpoint`: Not used for WhatsApp Business API (Meta handles routing)
- `whatsapp_number`: The display phone number
- `app_id`: Facebook App ID

## Migration Steps

### Step 1: Setup Facebook App and WhatsApp Business API
1. Follow Facebook's WhatsApp Business API setup guide
2. Configure your webhook URL: `https://yourdomain.com/api/whatsapp/webhook`
3. Set your webhook verify token in environment variables

### Step 2: Update Database Records
Update your business records with new WhatsApp Business API credentials:

```sql
UPDATE businesses 
SET 
    api_key = 'your_whatsapp_access_token',
    channel_id = 'your_phone_number_id',
    app_id = 'your_facebook_app_id'
WHERE whatsapp_number = 'your_business_phone_number';
```

### Step 3: Configure Webhooks
1. **Facebook Webhook**: Point to `/api/whatsapp/webhook`
2. **Legacy Dialog360**: Keep pointing to `/api/whatsapp/incoming-whatsapp` during transition

### Step 4: Test Integration
1. Send a test message to your WhatsApp Business number
2. Check logs for successful webhook processing
3. Verify responses are sent correctly

### Step 5: Monitor and Migrate
1. Monitor both services during transition period
2. Gradually move all numbers to WhatsApp Business API
3. Deprecate Dialog360 integration once migration is complete

## Webhook Differences

### Dialog360 Webhook Format
```json
{
  "entry": [{
    "changes": [{
      "value": {
        "metadata": {
          "display_phone_number": "+1234567890"
        },
        "messages": [{
          "from": "1234567890",
          "text": {"body": "Hello"},
          "type": "text"
        }]
      }
    }]
  }]
}
```

### WhatsApp Business API Webhook Format
```json
{
  "object": "whatsapp_business_account",
  "entry": [{
    "changes": [{
      "value": {
        "metadata": {
          "display_phone_number": "+1234567890",
          "phone_number_id": "123456789012345"
        },
        "messages": [{
          "from": "1234567890",
          "text": {"body": "Hello"},
          "type": "text"
        }],
        "contacts": [{
          "profile": {"name": "John Doe"},
          "wa_id": "1234567890"
        }]
      }
    }]
  }]
}
```

## API Endpoint Changes

### Sending Messages

#### Dialog360 (Old)
```python
# URL: https://waba-v2.360dialog.io/messages
headers = {"D360-API-KEY": "your_api_key"}
```

#### WhatsApp Business API (New)
```python
# URL: https://graph.facebook.com/v18.0/{phone_number_id}/messages
headers = {"Authorization": "Bearer your_access_token"}
```

## Testing

### Test WhatsApp Business API Integration
```bash
# Test webhook verification
curl -X GET "https://yourdomain.com/api/whatsapp/webhook?hub.mode=subscribe&hub.challenge=test&hub.verify_token=your_token"

# Should return: test
```

### Test Message Sending
Use the new WhatsApp Business service in your code:

```python
from app.services.whatsapp_business_service import WhatsAppBusinessService

# Initialize service
service = WhatsAppBusinessService(db)

# Send message
response = service.send_message(
    to="+1234567890",
    message="Hello from WhatsApp Business API!",
    business_phone="+0987654321"
)
```

## Troubleshooting

### Common Issues

1. **Webhook Verification Fails**
   - Ensure `WHATSAPP_WEBHOOK_VERIFY_TOKEN` matches Facebook app settings
   - Check that webhook URL is publicly accessible

2. **Messages Not Sending**
   - Verify `WHATSAPP_ACCESS_TOKEN` is valid and has necessary permissions
   - Check `WHATSAPP_PHONE_NUMBER_ID` is correct
   - Ensure recipient number is in correct format (+country_code_number)

3. **Database Errors**
   - Update business records with correct API credentials
   - Ensure `api_key` contains WhatsApp access token, not Dialog360 key

### Logs to Monitor
- Webhook processing: Look for "WhatsApp Business API webhook received"
- Service selection: Look for "using whatsapp_business service"
- Message sending: Look for "WhatsApp message sent successfully"

## Rollback Plan

If you need to rollback to Dialog360:

1. Update webhook URLs back to Dialog360
2. Revert database `api_key` fields to Dialog360 keys
3. Use the legacy `/api/whatsapp/incoming-whatsapp` endpoint

The code maintains backward compatibility, so no code changes are needed for rollback.

## Support

For issues with this migration:
1. Check application logs for detailed error messages
2. Verify all environment variables are set correctly
3. Test webhook connectivity using Facebook's webhook tester
4. Ensure database records are updated with new credentials

## Next Steps

After successful migration:
1. Remove Dialog360 environment variables
2. Clean up deprecated Dialog360 code
3. Update documentation to reflect WhatsApp Business API integration
4. Monitor API usage and costs through Facebook Business Manager 