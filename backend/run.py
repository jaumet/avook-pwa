import uvicorn
from main import app

if __name__ == "__main__":
    print("--- Starting Uvicorn server from run.py ---")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
