from fastapi import APIRouter, status

import httpx

router = APIRouter(prefix="/gold", tags=["gold"])

@router.get("/health", status_code=status.HTTP_200_OK)
def health_check():
    return {"status": "ok"}

@router.get("/price", status_code=status.HTTP_200_OK)
def get_gold_prices():
    # 1. Configuration
    # Replace with the actual token you obtained from the browser link
    API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3ODQ3NDgwMDksImlhdCI6MTc4MzQ1MjAwOSwic2NvcGUiOiJnb2xkIiwicGVybWlzc2lvbiI6MH0.T4CAJtFfAEJNGBHCVIpnTjtJgLA8SIpBCWbbI-aIjYw" 

    # Choose your target endpoint (sjc, doji, or pnj)
    URL = "https://api.vnappmob.com/api/v2/gold/sjc"

    # 2. Set up headers with your Bearer token
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    try:
        # 3. Execute the GET request
        response = httpx.get(URL, headers=headers)
        return response.json()  # Return the JSON response directly

    except Exception as e:
        return {"error": f"An error occurred: {e}"}