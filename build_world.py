import json, os

def build_world() -> list:
    world = "world.json"
    with open(world, "r") as f:
        world_data = json.load(f)
    return world_data
