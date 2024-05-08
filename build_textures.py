import json, os
from pathlib import Path

def build_textures() -> dict:
    textures = {}
    for texture_group in os.listdir(Path("assets", "meta")):
        for texture in os.listdir(Path("assets", "meta", texture_group)):
            with open(Path("assets", "meta", texture_group, texture), "r") as f:
                texture_meta = json.load(f)
            textures[texture] = texture_meta
    return textures

if __name__ == "__main__":
    print(build_textures())