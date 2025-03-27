
# TimeGlobeWhatsappAssistant

This Project aims to automate appointment booking through whatsapp


## Installation

Clone the repository:
```bash
https://github.com/Xsolai/TimeGlobeWhatsappAssistant
```
Navigate to the app directory:

```
cd app
 ```

Install Python dependencies

```
pip install -r requirements.txt
```

Configure environment variables:

``` 
create .env file in project folder and add following 

FROM_WHATSAPP_NUMBER Twilio sandbox number 
ACCOUNT_SID Twilio account sid
AUTH_TOKEN Twilio auth token
TWILIO_API_URL
TWILIO_MESSAGING_SERVICE_SID
WABA_ID WhatsApp bussiness id
TIME_GLOBE_LOGIN_USERNAME
TIME_GLOBE_LOGIN_PASSWORD
TIME_GLOBE_BASE_URL
TIME_GLOBE_API_KEY
OPENAI_ASSISTANT_ID
OPENAI_API_KEY
SECRETE_KEY default  ""
 ```
 Start the server:
```
uvicorn app.main:app --host 0.0.0.0 --port 80
```
API Documentation

```
http://127.0.0.1/docs
```
