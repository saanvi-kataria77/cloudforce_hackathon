from fastapi import FastAPI

app = FastAPI()
@app.get("/")
def home():
    return {"status": "online"} # testing testing!!

@app.post("/analyze")
async def analyze_video(url: str):
    return {"message": f"Processing video at {url}", "agent_status": "idle"}