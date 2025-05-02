
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

WABA_ID WhatsApp bussiness id
TIMEGLOBE_LOGIN_USERNAME
TIMEGLOBE_LOGIN_PASSWORD
TIMEGLOBE_BASE_URL
TIMEGLOBE_API_KEY
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
