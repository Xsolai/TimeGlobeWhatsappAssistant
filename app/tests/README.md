# Authentication Tests

This directory contains tests for the authentication endpoints in the TimeGlobe WhatsApp Assistant API.

## Available Tests

### 1. Unit Tests (`test_auth.py`)

These are automated pytest tests that verify each endpoint's functionality in isolation using a mock database.

Features:
- Uses in-memory SQLite database for testing
- Mocks email and OTP components
- Tests all authentication endpoints
- Verifies correct behaviors and error cases

### 2. Verification Script (`verify_auth_endpoints.py`)

An interactive script that makes real API calls to test the authentication endpoints against a running server.

Features:
- Sends real HTTP requests
- Provides visual feedback of responses
- Interactive prompts for OTP and reset tokens
- Comprehensive verification flow

## How to Run Tests

### Option 1: Using the Runner Script

The easiest way to run tests is using the `run_auth_tests.py` script:

```bash
# Run both unit tests and verification script
python -m app.tests.run_auth_tests

# Run only unit tests
python -m app.tests.run_auth_tests --unit

# Run only verification script
python -m app.tests.run_auth_tests --verify

# Show help
python -m app.tests.run_auth_tests --help
```

### Option 2: Running Tests Directly

You can also run each test file directly:

```bash
# Run unit tests
python -m app.tests.test_auth

# Run verification script
python -m app.tests.verify_auth_endpoints
```

## Requirements for Verification Tests

To run the verification script:

1. The API server must be running
2. Set the `API_BASE_URL` environment variable or create a `.env` file with:
   ```
   API_BASE_URL=http://your-api-server:port/api
   ```
3. If not specified, it defaults to `http://localhost:8000/api`

## Troubleshooting

- If you encounter import errors, make sure you're running the tests using the module syntax (`python -m app.tests.file_name`) rather than directly.
- For verification tests, ensure the API server is running and accessible at the specified URL.
- If OTP verification fails, check that email sending is properly configured in the development environment. 