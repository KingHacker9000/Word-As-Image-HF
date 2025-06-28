import os
import subprocess
import uuid
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import torch
import pydiffvg

DEFAULT_FONT = "KaushanScript-Regular"


def ensure_diffvg_cuda():
    """Raise RuntimeError if diffvg is not built with CUDA support."""
    pydiffvg.set_use_gpu(torch.cuda.is_available())
    try:
        device = pydiffvg.get_device()
    except RuntimeError as exc:
        # get_device raises when diffvg lacks CUDA bindings
        raise RuntimeError(
            "diffvg not compiled with CUDA. Please rebuild diffvg with GPU support."
        ) from exc
    if device.type != "cuda":
        raise RuntimeError(
            "diffvg not compiled with CUDA. Please rebuild diffvg with GPU support."
        )

class GenerationRequest(BaseModel):
    concept: str
    letter: str
    font: str = DEFAULT_FONT
    seed: int = 0
    token: str

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Use POST /generate"}

@app.post("/generate")
def generate(req: GenerationRequest):
    out_root = Path("space_outputs")
    out_dir = out_root / str(uuid.uuid4())
    out_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        "python", "code/main.py",
        "--semantic_concept", req.concept,
        "--optimized_letter", req.letter,
        "--font", req.font,
        "--seed", str(req.seed),
        "--log_dir", str(out_dir),
        "--token", req.token,
    ]
    subprocess.run(cmd, check=True)

    pattern = list(out_dir.rglob("output-png/output.png"))
    if not pattern:
        raise HTTPException(status_code=500, detail="No output image found")
    return FileResponse(pattern[0], media_type="image/png")

if __name__ == "__main__":
    ensure_diffvg_cuda()
    import uvicorn
    port = int(os.environ.get("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port)
