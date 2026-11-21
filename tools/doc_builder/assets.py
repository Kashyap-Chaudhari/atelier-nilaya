import os
import base64
import json

def get_base64_image(rel_path):
    # Try local workspace first, then brain directory
    candidates = [
        rel_path,
        os.path.join("browser_snapshots", os.path.basename(rel_path)),
        os.path.join(r"C:\Users\hi\.gemini\antigravity\brain\f6fd8ec0-0b1d-46c1-8a61-9162ce04f9f5\browser_snapshots", os.path.basename(rel_path))
    ]
    for p in candidates:
        if os.path.exists(p):
            try:
                with open(p, "rb") as f:
                    encoded = base64.b64encode(f.read()).decode("utf-8")
                    ext = os.path.splitext(p)[1].lower()
                    mime = "image/png" if ext == ".png" else "image/webp" if ext == ".webp" else "image/jpeg"
                    return f"data:{mime};base64,{encoded}"
            except Exception as e:
                print(f"Error reading image {p}: {e}")
    return ""

def load_qa_results():
    path = "scratch/qa_results.json"
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []
