import fastapi
from fastapi import File, HTTPException
from fastapi import status
import os
from fastapi import UploadFile
import uuid
from dotenv import load_dotenv

load_dotenv()

app = fastapi.FastAPI()

token = os.getenv("TOKEN")

@app.get("/clear")
def clear():
    if token != token:
        raise HTTPException(status_code=401, detail="Invalid token")
    os.remove("uploads/*")
    return {"message": "DB cleared"}

@app.post("/upload")
async def upload_file(token: str, file: UploadFile = File(...)):
    if token != token:
        raise HTTPException(status_code=401, detail="Invalid token")
    file_path = os.path.join("uploads", file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())
    return {"message": "File uploaded"}

@app.get("/clips")
def get_clips():
    return {"message": "Clips retrieved"}

@app.get('/clip/{clip_id}')
def get_clip(clip_id: str):
    return {"message": "Clip retrieved"}

