from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import JSONResponse
import os
from pathlib import Path
import json
import base64

router = APIRouter()

# Counter file to persist the download count
COUNTER_FILE = Path("app/static/downloads/counter.json")

def get_next_counter():
    """Get the next counter value and increment it for future use"""
    try:
        if COUNTER_FILE.exists():
            with open(COUNTER_FILE, "r") as f:
                data = json.load(f)
                counter = data.get("counter", 00000)
        else:
            # Initialize with starting value if file doesn't exist
            counter = 00000
            
        # Increment counter for next use
        with open(COUNTER_FILE, "w") as f:
            json.dump({"counter": counter + 1}, f)
            
        return counter
    except Exception as e:
        # In case of any error, default to a timestamp-based value
        import time
        return int(time.time())

@router.get("/pdf", summary="Download PDF file with incrementing filename")
async def download_sample_pdf():
    """
    Endpoint to download a PDF file with an incrementing number in the filename.
    
    Returns:
        JSONResponse: Contains the filename and base64-encoded file content
    """
    # Define the path to the PDF file
    pdf_path = Path("app/static/downloads/LS-Mandat.pdf")
    
    # Check if the file exists
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="PDF file not found")
    
    # Get the next counter value
    counter = get_next_counter()
    
    # Create the filename with the counter
    filename = f"SEPA-Lastschriftmandat_{counter}.pdf"
    
    # Open and read the file content, then encode as base64
    with open(pdf_path, 'rb') as file:
        content = file.read()
        encoded_content = base64.b64encode(content).decode('utf-8')
    
    # Create a JSON response with filename and content
    json_content = {
        "filename": filename,
        "file_content": encoded_content,
        "content_type": "application/pdf"
    }
    
    # Create a manual Response object with explicit JSON content type
    response = Response(
        content=json.dumps(json_content),
        media_type="application/json"
    )
    
    # Explicitly set headers to prevent any middleware from overriding them
    response.headers["Content-Type"] = "application/json"
    
    return response
