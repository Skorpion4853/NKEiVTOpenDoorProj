import torch
from diffusers import StableDiffusionImg2ImgPipeline
from PIL import Image
import os
import time

from huggingface_hub import snapshot_download

MODEL_PATH = "models/sd15"

if not os.path.exists(MODEL_PATH):
    snapshot_download(
        repo_id="runwayml/stable-diffusion-v1-5",
        local_dir=MODEL_PATH,
        local_dir_use_symlinks=False
    )


pipe = None

def load_model():
    global pipe
    if pipe is None:
        pipe = StableDiffusionImg2ImgPipeline.from_pretrained(
            MODEL_PATH,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            safety_checker=None
        )
        if torch.cuda.is_available():
            pipe = pipe.to("cuda")
    return pipe


def generate_image(init_image_path, prompt):
    pipe = load_model()

    init_image = Image.open(init_image_path).convert("RGB")
    init_image = init_image.resize((512, 512))

    result = pipe(
        prompt=prompt,
        image=init_image,
        strength=0.75,
        guidance_scale=7.5
    ).images[0]

    os.makedirs("source/generated", exist_ok=True)
    out_path = f"source/generated/gen_{int(time.time())}.png"
    result.save(out_path)

    return out_path
