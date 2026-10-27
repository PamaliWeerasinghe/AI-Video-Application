import os
import httpx
from dotenv import load_dotenv

load_dotenv()

PAGE_ID = os.getenv("FB_PAGE_ID")
ACCESS_TOKEN = os.getenv("FB_PAGE_ACCESS_TOKEN")

if not PAGE_ID or not ACCESS_TOKEN:
    print("Error: Missing FB_PAGE_ID or FB_PAGE_ACCESS_TOKEN in .env")
    exit(1)

# Query Facebook Page details
url = f"https://graph.facebook.com/v19.0/{PAGE_ID}"
response = httpx.get(url, params={"fields": "id,name", "access_token": ACCESS_TOKEN})

if response.status_code == 200:
    data = response.json()
    print("Connection Successful!")
    print(f"Page Name: {data.get('name')}")
    print(f"Page ID:   {data.get('id')}")
else:
    print(f"Connection Failed: {response.status_code} - {response.text}")