import os
import shutil
import uvicorn
import tempfile
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Load env vars from the current folder
load_dotenv()

from agent import run_agent
from ingest import ingest_data


# Define FastAPI App
app = FastAPI()

# Add CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define Request Body
class QueryRequest(BaseModel):
    message: str
    sessionId: str = "default"

# Define Endpoints
@app.post("/api/chat")
async def ask(req: QueryRequest):
    if not req.message:
        raise HTTPException(status_code=400, detail="Message required")
    try:
        answer = run_agent(req.sessionId, req.message)
        output = answer.get("output", "")
        if not output or not output.strip():
            return {"answer": "I apologize, but I couldn't generate a proper response. Could you please rephrase your question?"}
        return {"answer": output}
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ingest")
async def ingest(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    try:
        # Save to temp file
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, file.filename)

        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Ingest data
        ingest_data(temp_path)
        
        # Cleanup
        try:
            os.remove(temp_path)
        except:
            pass
        return {"ok": True}
    except Exception as e:
        if 'temp_path' in locals() and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except:
                pass
        raise HTTPException(status_code=500, detail=str(e))

# Run the server
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=3001, reload=True)