import os
import shutil
import tempfile
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import json
import cv2

from backend.vision_analyzer import analyze_table_crop
from backend.table_state import (
    init_floor, update_table, get_floor_state,
    get_tables_for_party, reset_table, floor_state
)

load_dotenv()

app = FastAPI(title="TableVision AI", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

config = {}

os.makedirs("temp", exist_ok=True)

# Auto-load config on startup
config_path = "config/restaurant_config.json"
if os.path.exists(config_path):
    with open(config_path) as f:
        config = json.load(f)
    init_floor(config)


@app.get("/")
def root():
    return {"status": "TableVision backend running"}


@app.post("/api/config")
async def load_config(file: UploadFile = File(...)):
    global config
    content = await file.read()
    config = json.loads(content)
    init_floor(config)
    return {"loaded": True, "tables": len(config.get("tables", []))}


@app.get("/api/config")
def get_config():
    return config


@app.post("/api/analyze")
async def analyze_frame(file: UploadFile = File(...)):
    if not config:
        return {"error": "No restaurant config loaded"}

    img_path = f"temp/frame_{file.filename}"
    with open(img_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    results = {}
    avg_dining = config.get("avg_dining_minutes", 45)

    for table in config["tables"]:
        img = cv2.imread(img_path)
        if img is None:
            continue
        x1, y1, x2, y2 = table["crop_box"]
        h, w = img.shape[:2]
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(w, x2), min(h, y2)
        crop = img[y1:y2, x1:x2]
        crop_path = f"temp/crop_{table['table_id']}.jpg"
        cv2.imwrite(crop_path, crop)

        result = analyze_table_crop(crop_path, table["capacity"])
        if result:
            update_table(table["table_id"], result, avg_dining)
            results[table["table_id"]] = result
        else:
            results[table["table_id"]] = {"skipped": True}

    return {"analyzed": results, "floor_state": get_floor_state()}


@app.get("/api/floor-state")
def floor_state_endpoint():
    return get_floor_state()


@app.post("/api/reset-table/{table_id}")
def reset_table_endpoint(table_id: int):
    reset_table(table_id)
    return {"reset": True, "table_id": table_id}


@app.get("/api/search-table")
def search_table(party_size: int):
    if not floor_state:
        return {"error": "No floor state available"}
    return get_tables_for_party(party_size)


@app.post("/api/analyze-video")
async def analyze_video(file: UploadFile = File(...)):
    if not config:
        return {"error": "No restaurant config loaded"}

    for table_id in floor_state:
        floor_state[table_id].update({
            "occupied_seats": 0,
            "has_people": False,
            "status": "available",
            "parties": [],
            "occupied_since": None,
            "estimated_minutes_remaining": None
        })

    suffix = os.path.splitext(file.filename)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        video_path = tmp.name

    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 25
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps

    sample_interval = max(1, int(fps * 1))
    frame_results = []
    frame_num = 0
    sample_count = 0
    avg_dining = config.get("avg_dining_minutes", 45)

    while cap.isOpened() and sample_count < 10:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_num % sample_interval == 0:
            frame_data = {
                "frame_index": sample_count,
                "timestamp_sec": round(frame_num / fps, 1),
                "tables": {}
            }

            for table in config["tables"]:
                x1, y1, x2, y2 = table["crop_box"]
                h, w = frame.shape[:2]
                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(w, x2), min(h, y2)
                crop = frame[y1:y2, x1:x2]
                crop_path = f"temp/vcrop_{table['table_id']}_{sample_count}.jpg"
                cv2.imwrite(crop_path, crop)

                result = analyze_table_crop(crop_path, table["capacity"])
                if result:
                    update_table(table["table_id"], result, avg_dining)
                    frame_data["tables"][table["table_id"]] = result

            frame_results.append(frame_data)
            sample_count += 1

        frame_num += 1

    cap.release()
    os.unlink(video_path)

    return {
        "video_duration_sec": round(duration, 1),
        "frames_analyzed": sample_count,
        "frame_results": frame_results,
        "final_floor_state": get_floor_state()
    }
