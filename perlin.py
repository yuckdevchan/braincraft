from perlin_noise import PerlinNoise
import json, random, os


def generate_world_json():
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
        seed = random.randint(0, 100000000000000000000000000000)
        print("Generating world with seed: " + str(seed))
        world = generate_perlin_noise_2d(16, 16, seed)
        # world = generate_random(8, 8)
    with open("world.json", "w") as f:
        json.dump(world, f)


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
    world = []
    scale = 10
    for x in range(width):
        for y in range(height):
            wow = 8
            if random.randint(0, 100) < 20:
                world.append({"block": "poppy", "coords": (x * 2, wow, y * 2)})
            elif random.randint(0, 100) < 14:
                world.append({"block": "dandelion", "coords": (x * 2, wow, y * 2)})
            wow += 2
            world.append({"block": "grass_block", "coords": (x * 2, wow, y * 2)})
            wow += 2
            for i in range(0, 2):
                world.append({"block": "dirt_block", "coords": (x * 2, wow, y * 2)})
                wow += 2
            for i in range(0, 5):
                deeper_block = "stone"
                stone_deepness = 0
                if random.randint(0, 100) < 20 and stone_deepness <= 2:
                    deeper_block = "dirt_block"
                else:
                    deeper_block = "stone"
                world.append({"block": deeper_block, "coords": (x * 2, wow, y * 2)})
                stone_deepness += 1
                wow += 2
            world.append({"block": "bedrock", "coords": (x * 2, wow, y * 2)})
    # add ores between wow 12 and 24
    for block in world:
        with open("assets/treasure.json", "r") as f:
            treasure = json.load(f)
        for ore in treasure:
            if (
                block["coords"][1] >= treasure[ore]["yLower"]
                and block["coords"][1] <= treasure[ore]["yUpper"]
            ):
                if random.randint(0, 100) < treasure[ore]["rarity"]:
                    block["block"] = ore
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


if __name__ == "__main__":
    generate_world_json()
