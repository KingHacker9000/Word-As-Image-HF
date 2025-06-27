import os
import subprocess
import uuid
from pathlib import Path
import gradio as gr

DEFAULT_FONT = "KaushanScript-Regular"


def generate(concept: str, letter: str, font: str = DEFAULT_FONT, seed: int = 0):
    out_root = Path("space_outputs")
    out_dir = out_root / str(uuid.uuid4())
    out_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        "python", "code/main.py",
        "--semantic_concept", concept,
        "--optimized_letter", letter,
        "--font", font,
        "--seed", str(seed),
        "--log_dir", str(out_dir)
    ]
    subprocess.run(cmd, check=True)

    # find the resulting image
    pattern = list(out_dir.rglob("output-png/output.png"))
    if not pattern:
        raise RuntimeError("No output image found")
    return pattern[0]


demo = gr.Interface(
    fn=generate,
    inputs=[
        gr.Textbox(label="Semantic Concept"),
        gr.Textbox(label="Optimized Letter"),
        gr.Textbox(label="Font Name", value=DEFAULT_FONT)
    ],
    outputs=gr.Image(type="filepath"),
    title="Word-As-Image"
)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=port)
