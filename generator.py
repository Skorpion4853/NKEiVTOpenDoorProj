import torch
from diffusers import Flux2KleinPipeline
from PIL import Image
import os
import time

MODEL_PATH = "models/flux2-klein-4b"

if not os.path.exists(MODEL_PATH):
    snapshot_download(
        repo_id="black-forest-labs/FLUX.2-klein-4B",
        local_dir="./models/flux2-klein-4b",
        local_dir_use_symlinks=False
    )

device = "cuda"
pipe = None


def load_model(mode=3):
    global pipe
    if pipe is None:
        pipe = Flux2KleinPipeline.from_pretrained(
            "./models/flux2-klein-4b",
            torch_dtype=torch.bfloat16,
            local_files_only=True
        )
        if mode == 1:
            pipe.to("cuda")
        elif mode == 2:
            pipe.enable_model_cpu_offload()
            pipe.enable_vae_slicing()
            pipe.enable_attention_slicing()
        else:
            pipe.enable_model_cpu_offload()
    return pipe


def generate_image(init_image_path, prompt):
    pipe = load_model()
    init_image = Image.open(init_image_path).convert("RGB")

    result = pipe(
        prompt=prompt,
        image=init_image,
        height=1024,
        width=1024,
        guidance_scale=1.0,
        num_inference_steps=4,
        generator=torch.Generator(device=device).manual_seed(0)
    ).images[0]

    os.makedirs("source/generated", exist_ok=True)
    out_path = f"source/generated/gen_{int(time.time())}.png"
    result.save(out_path)

    return out_path