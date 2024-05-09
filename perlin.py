from perlin_noise import PerlinNoise
import json, random, os, h5py
import numpy as np
import pickle

def generate_world():
    superflat = False
    # superflat_composition = {"grass_block": 1, "dirt_block": 3, "stone": 2, "bedrock": 1, "air": 2, "diamond_ore": 2}
    superflat_composition = {
        "grass_block": 1,
        "dirt_block": 1,
        "stone": 1,
        "bedrock": 1,
    }
    if superflat:
        world = generate_superflat_world(superflat_composition, 6, 6)
    else:
        # seed = random.randint(0, 100000000000000000000000000000)
        seed = 2
        print("Generating world with seed: " + str(seed))
        world = generate_perlin_noise_2d(16, 16, seed)
        # world = generate_random(8, 8)
    # with open("world.json", "w") as f:
        # json.dump(world, f)
    # save as pickle
    with open("world.pkl", "wb") as f:
        pickle.dump(world, f)
    return world

def generate_superflat_world(composition: dict, width: int, height: int) -> list:
    world = []
    y = 0
    for block in composition:
        for count in range(composition[block]):
            for x in range(width):
                for z in range(height):
                    if block == "air":
                        pass
                    else:
                        world.append({"block": block, "coords": (x * 2, y, z * 2)})
            y += 2
    return world


def generate_perlin_noise_2d(width: int, height: int, seed: int) -> list:
    random.seed(seed)
    noise = PerlinNoise(octaves=10, seed=seed)
    world = {}
    scale = 10
    for x in range(width):
        for y in range(height):
            wow = 8
            if random.randint(0, 100) < 5:
                world[(x * 2, wow, y * 2)] = "poppy"
            elif random.randint(0, 100) < 5:
                world[(x * 2, wow, y * 2)] = "dandelion"
            wow += 2
            world[(x * 2, wow, y * 2)] = "grass_block"
            wow += 2
            for i in range(0, 2):
                world[(x * 2, wow, y * 2)] = "dirt_block"
                wow += 2
            for i in range(0, 64):
                deeper_block = "stone"
                stone_deepness = 0
                if random.randint(0, 100) < 10 and stone_deepness <= 2:
                    deeper_block = "dirt_block"
                else:
                    deeper_block = "stone"
                world[(x * 2, wow, y * 2)] = deeper_block
                stone_deepness += 1
                wow += 2
            world[(x * 2, wow, y * 2)] = "bedrock"
    with open("assets/treasure.json", "r") as f:
        treasure = json.load(f)
    for block in world:
        for ore in treasure:
            if (
                block[1] >= treasure[ore]["yLower"]
                and block[1] <= treasure[ore]["yUpper"]
                and world[block] == "stone"
            ):
                if random.randint(0, 100) < treasure[ore]["rarity"]:
                    world[block] = ore
    # add ores between wow 12 and 24
    # for block in world:
    #     with open("assets/treasure.json", "r") as f:
    #         treasure = json.load(f)
    #     for ore in treasure:
    #         if (
    #             block["coords"][1] >= treasure[ore]["yLower"]
    #             and block["coords"][1] <= treasure[ore]["yUpper"]
    #         ):
    #             if random.randint(0, 100) < treasure[ore]["rarity"]:
    #                 block["block"] = ore
    return world


def generate_random(width: int, height: int) -> list:
    world = []
    for x in range(width):
        for y in range(height):
            block = random.choice(
                [
                    "grass_block",
                    "dirt_block",
                    "stone",
                    "bedrock",
                    "air",
                    "diamond_ore",
                    "iron_ore",
                    "coal_ore",
                    "gold_ore",
                ]
            )
            if block != "air":
                wow = random.randint(0, 5) * 2
                world.append({"block": block, "coords": (x * 2, wow, y * 2)})
            if block == "grass_block":
                if random.randint(0, 100) > 25:
                    world.append({"block": "poppy", "coords": (x * 2, wow - 2, y * 2)})
    return world
