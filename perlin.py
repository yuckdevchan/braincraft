from perlin_noise import PerlinNoise
import json, random, os
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
        world = generate_perlin_noise_2d(16, 16, seed, 0, 0)
        # world = generate_skyblock_world()
        # world = generate_random(8, 8)
    # with open("world.json", "w") as f:
        # json.dump(world, f)
    # save as pickle
    print("World generated")
    with open("world.pkl", "wb") as f:
        pickle.dump(world, f)
    print("World pickled")
    return world

def get_chunk(seed, chunkx, chunkz):
    chunk = generate_perlin_noise_2d(16, 16, seed, chunkx, chunkz)
    return chunk

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


def get_flowers():
    flowers = {}
    for blockmeta in os.listdir("assets/meta/block"):
        with open(f"assets/meta/block/{blockmeta}", "r") as f:
            block = json.load(f)
        try:
            if block["props"]["flower"]["spawns"]:
                flowers[block["id"]] = block["props"]["flower"]
        except KeyError:
            pass
    return flowers

def get_structures():
    structures = {}
    for structure in os.listdir("assets/meta/structures"):
        with open(f"assets/meta/structures/{structure}", "r") as f:
            structures[structure] = json.load(f)
    return structures

def generate_skyblock_world(width=6, height=6):
    world = {}
    for n in range(0, 2):
        for i in range(0, 3):
            for j in range(0, 3):
                world[(i*2, 0, j*2)] = "grass_block"
                world[(i*2, 2, j*2)] = "dirt_block"
    for n in range(0, 2):
        for i in range(0, 3):
            for j in range(0, 3):
                world[(i*2, 0, j*2-6)] = "grass_block"
                world[(i*2, 2, j*2-6)] = "dirt_block"
    for n in range(0, 2):
        for i in range(0, 3):
            for j in range(0, 3):
                world[(i*2 + 6, 0, j*2-6)] = "grass_block"
                world[(i*2 + 6, 2, j*2-6)] = "dirt_block"
    # generate structure
    tree = "oak_tree.json"
    with open(f"assets/meta/structures/{tree}", "r") as f:
        tree = json.load(f)
    for block in tree["blocks"]:
        world[(block[0][0] + 2, block[0][1], block[0][2]+2)] = block[1]
    print(world)
    return world

def generate_perlin_noise_2d(width: int, height: int, seed: int, chunkx: int, chunkz: int) -> list:
    random.seed(seed)
    noise = PerlinNoise(octaves=10, seed=seed)
    world = {}
    scale = 300
    flowers = get_flowers()
    structures = get_structures()
    for x in range(chunkx, width):
        for z in range(chunkz, height):
            wow = int((noise([x/scale, z/scale]) + 2) * 5)
            if wow % 2 != 0:
                wow += 1
            wow2 = 0
            for flower in flowers:
                if random.randint(0, 100) <= flowers[flower]["rarity"]:
                    world[(x * 2, wow, z * 2)] = flower
            for structure in structures:
                if random.randint(0, 100) < structures[structure]["rarity"]:
                    for block in structures[structure]["blocks"]:
                        world[(x * 2 + block[0][0], wow + block[0][1], z * 2 + block[0][2])] = block[1]
            wow += 2
            world[(x * 2, wow, z * 2)] = "grass_block"
            wow += 2
            for i in range(0, 2):
                world[(x * 2, wow, z * 2)] = "dirt_block"
                wow += 2
            for i in range(0, 64):
                deeper_block = "stone"
                stone_deepness = 0
                if random.randint(0, 100) < 10 and stone_deepness <= 2:
                    deeper_block = "dirt_block"
                else:
                    deeper_block = "stone"
                world[(x * 2, wow, z * 2)] = deeper_block
                stone_deepness += 1
                wow += 2
            world[(x * 2, 144, z * 2)] = "bedrock"
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
