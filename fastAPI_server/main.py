import fastapi
from fastapi import File, HTTPException, Form
import os
from fastapi import UploadFile
import uuid
from dotenv import load_dotenv
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = fastapi.FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Create uploads directory if it doesn't exist
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


# Mount the uploads directory as static files
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

token = os.getenv("TOKEN")
server_url = os.getenv("SERVER_URL")

@app.get("/clear")
def clear(token: str):
    if token != os.getenv("TOKEN"):
        raise HTTPException(status_code=401, detail="Invalid token")
    for file in os.listdir(UPLOAD_DIR):
        os.remove(os.path.join(UPLOAD_DIR, file))
    return {"message": "DB cleared"}

@app.post("/upload")
async def upload_file(
    token: str = Form(...),
    file: UploadFile = File(...)
):
    print(f"Received token: {token}")
    print(f"Expected token: {os.getenv('TOKEN')}")
    if token != os.getenv("TOKEN"):
        raise HTTPException(status_code=401, detail="Invalid token")
    
    try:
        generated_id = str(uuid.uuid4())
        file_path = os.path.join(UPLOAD_DIR, generated_id)
        print(f"Saving file to: {file_path}")
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        print(f"File saved successfully. Size: {len(content)} bytes")
        
        # Return the updated clip list HTML
        clips = os.listdir(UPLOAD_DIR)
        html_content = """
        <div class="clip-list">
            <h2>Your Clips</h2>
        """
        
        for clip in clips:
            html_content += f"""
            <div class="clip-item">
                <div>
                    <a href="{server_url}/clip/{clip}" target="_blank">View Video {clip[:8]}...</a>
                </div>
                <div class="button-group">
                    <button class="delete-btn" 
                            hx-delete="{server_url}/clip/{clip}"
                            hx-target="#clip-list"
                            hx-swap="innerHTML"
                            hx-confirm="Are you sure you want to delete this clip?">
                        Delete
                    </button>
                </div>
            </div>
            """
        
        html_content += "</div>"
        return HTMLResponse(content=html_content)
    except Exception as e:
        print(f"Error uploading file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/clips")
def get_clips():
    if not os.path.exists(UPLOAD_DIR):
        return "No clips found"
    
    clips = os.listdir(UPLOAD_DIR)
    if not clips:
        return "No clips found"
    
    html_content = """
    <div class="clip-list">
        <h2>Your Clips</h2>
    """
    
    for clip in clips:
        html_content += f"""
        <div class="clip-item">
            <div>
                <a href="{server_url}/clip/{clip}" target="_blank">View Video {clip[:8]}...</a>
            </div>
            <div class="button-group">
                <button class="delete-btn" 
                        hx-delete="{server_url}/clip/{clip}"
                        hx-target="#clip-list"
                        hx-swap="innerHTML"
                        hx-confirm="Are you sure you want to delete this clip?">
                    Delete
                </button>
            </div>
        </div>
        """
    
    html_content += "</div>"
    return HTMLResponse(content=html_content)

@app.get('/clip/{clip_id}')
def get_clip(clip_id: str):
    file = os.path.join(UPLOAD_DIR, clip_id)
    if not os.path.exists(file):
        raise HTTPException(status_code=404, detail="Clip not found")
    return FileResponse(file, media_type="video/mp4")

@app.delete('/clip/{clip_id}')
def delete_clip(clip_id: str):
    file = os.path.join(UPLOAD_DIR, clip_id)
    if not os.path.exists(file):
        raise HTTPException(status_code=404, detail="Clip not found")
    os.remove(file)
    
    # Return the updated clip list HTML
    clips = os.listdir(UPLOAD_DIR)
    if not clips:
        return HTMLResponse(content="<div class='clip-list'><h2>Your Clips</h2><p>No clips found</p></div>")
    
    html_content = """
    <div class="clip-list">
        <h2>Your Clips</h2>
    """
    
    for clip in clips:
        html_content += f"""
        <div class="clip-item">
            <div>
                <a href="{server_url}/clip/{clip}" target="_blank">View Video {clip[:8]}...</a>
            </div>
            <div class="button-group">
                <button class="delete-btn" 
                        hx-delete="{server_url}/clip/{clip}"
                        hx-target="#clip-list"
                        hx-swap="innerHTML"
                        hx-confirm="Are you sure you want to delete this clip?">
                    Delete
                </button>
            </div>
        </div>
        """
    
    html_content += "</div>"
    return HTMLResponse(content=html_content)
