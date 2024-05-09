import json, os
from perlin import generate_world

def build_world():
    # world = "world.json"
    # with open(world, "r") as f:
    #     world_data = json.load(f)
    # return world_data
    return generate_world()
