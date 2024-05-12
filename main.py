from direct.showbase.ShowBase import ShowBase
from panda3d.core import CardMaker, TextureStage, loadPrcFileData, WindowProperties, Vec3, TextNode, ClockObject, CollisionNode, CollisionBox, Point3, NodePath
from direct.task import Task
from direct.showbase.DirectObject import DirectObject
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import ClockObject, LVector3, CollisionRay, CollisionNode, CollisionTraverser, CollisionHandlerQueue, CollisionTraverser, CollisionHandlerQueue, BitMask32, CollisionSphere
from direct.interval.LerpInterval import LerpFunc
from direct.showbase.ShowBaseGlobal import globalClock
from direct.filter.CommonFilters import CommonFilters
from panda3d.core import WindowProperties
from pathlib import Path
import math, time, os, json, toml
from panda3d.physics import PhysicsManager, PhysicalNode, ForceNode, LinearVectorForce

from build_textures import build_textures
textures = build_textures()
from build_world import build_world
from perlin import get_chunk

class MainWindow(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        with open("config.toml", "r") as f:
            config = toml.load(f)
        self.config = config
        prog_timer = time.time()

        self.created_cards = []
        
        self.move_forward_task = None
        self.move_backward_task = None
        self.move_left_task = None
        self.move_right_task = None
        self.move_up_task = None
        self.move_down_task = None
        self.sprint_task = None

        self.props = WindowProperties()
        self.props.setTitle("Parablocks")
        self.props.setSize(3840, 2160)
        self.props.setCursorHidden(True)
        # props.setFullscreen(True)
        self.props.setIconFilename("assets/textures/icon.ico")
        self.win.requestProperties(self.props)

        self.speed = 0.15
        self.accept("escape", self.userExit)
        self.accept("w", self.start_moving_forward)
        self.accept("w-up", self.stop_moving_forward)
        self.accept("a", self.start_moving_left)
        self.accept("a-up", self.stop_moving_left)
        self.accept("s", self.start_moving_backward)
        self.accept("s-up", self.stop_moving_backward)
        self.accept("d", self.start_moving_right)
        self.accept("d-up", self.stop_moving_right)
        self.accept("space", self.start_moving_up)
        self.accept("space-up", self.stop_moving_up)
        self.accept("control", self.start_moving_down)
        self.accept("control-up", self.stop_moving_down)
        self.accept("shift", self.sprint)
        self.accept("shift-up", self.stop_sprinting)
        self.accept("f11", self.toggle_fullscreen)
        self.accept("f9", self.toggle_wireframe)
        self.accept("-", self.zoom_out)
        self.accept("=", self.zoom_in)
        self.accept("c", self.zoom_in_smol)
        self.accept("c-up", self.zoom_out_smol)
        self.accept("p", self.floating_block)
        self.accept("mouse1", self.break_block)
        self.accept("e", self.toggle_inventory)
        self.accept("wheel_up", self.item_up)
        self.accept("wheel_down", self.item_down)

        z = 6
        y = 8
        x = 10
        
        self.disableMouse()
        self.mouseLookTask = taskMgr.add(self.mouseLook, "mouseLookTask")
        base.camLens.setNearFar(0.1, 1000)
        base.camLens.setFov(75)
        self.addHUD()
        # base.setFrameRateMeter(True)

        self.cTrav = CollisionTraverser()
        camCollisionNode = CollisionNode('camCollisionNode')
        camCollisionNode.addSolid(CollisionSphere(0, 0, 0, 1))
        camCollisionNode.setFromCollideMask(BitMask32.bit(1))
        camCollisionNode.setIntoCollideMask(BitMask32.allOff())
        camCollisionNP = self.camera.attachNewNode(camCollisionNode)
        self.camCollisionQueue = CollisionHandlerQueue()
        self.cTrav.addCollider(camCollisionNP, self.camCollisionQueue)
        camCollisionNP.show()

        world_timer = time.time()
        self.world = build_world()
        print("World generated in " + str(round(time.time() - world_timer, 2)) + " seconds")
        self.world_creation = taskMgr.add(self.create_world, "world_creation")
        filters = CommonFilters(base.win, base.cam)
        # filters.setMSAA(2)
        base.physicsMgr = PhysicsManager()
        # add gravity
        gravityFN=ForceNode('world-forces')
        gravityFNP=render.attachNewNode(gravityFN)
        self.gravityForce=LinearVectorForce(0,0,-9.81) #gravity acceleration
        gravityFN.addForce(self.gravityForce)
        self.spawn_entity("chicken")
        self.create_inventory()
        self.breaking_inhibitor = False
        self.mouse_camera_inhibitor = False
        self.held_item = 0
        self.item_is_held = False
        print("Program started in " + str(round(time.time() - prog_timer, 2)) + " seconds")

    def toggle_inventory(self):
        if self.inventory_node.isHidden():
            self.open_inventory()
        else:
            self.close_inventory()

    def create_inventory(self):
        inv_timer = time.time()
        print("Creating inventory")
        self.inventory = CardMaker("inventory")
        self.inventory.setFrame(-1, 1, -1, 1)
        self.inventory_node = aspect2d.attachNewNode(self.inventory.generate())
        self.inventory_node.setPos(0, 0, 0)
        self.inventory_node.setScale(0.75)
        self.inventory_node.setTransparency(1)
        texture = self.loader.loadTexture("assets/textures/gui/inventory.png")
        texture.setMagfilter(0)
        self.inventory_node.setTexture(texture, 1)
        self.inventory_node.setTwoSided(True)
        self.inventory_node.setBin("fixed", 0)
        self.inventory_node.setDepthTest(False)
        self.inventory_node.setDepthWrite(False)
        self.inventory_node.hide()
        block_pos = 0.5
        block_pos_y = 5
        for category in os.listdir("assets/meta"):
            if category != "structures":
                for blockmeta in os.listdir(f"assets/meta/{category}"):
                    with open(f"assets/meta/{category}/" + blockmeta, "r") as f:
                        block = json.load(f)
                        try:
                            try:
                                front_texture = block["textures"]["front"]
                            except KeyError:
                                front_texture = block["textures"]["2dcross"]
                            block_card = CardMaker("block_card")
                            block_card.setFrame(-1, 1, -1, 1)
                            block_node = self.inventory_node.attachNewNode(block_card.generate())
                            block_node.setTransparency(1)
                            block_texture = self.loader.loadTexture(Path("assets", "textures", category, front_texture))
                            block_texture.setMagfilter(0)
                            block_node.setTexture(block_texture, 1)
                            block_node.setTwoSided(True)
                            block_node.setBin("fixed", 0)
                            block_node.setDepthTest(False)
                            block_node.setDepthWrite(False)
                            if block_pos >= 9:
                                block_pos = 0
                                block_pos_y += 1
                            block_node.setPos(-0.9 + (block_pos * 0.2), 0, 0.9 - (block_pos_y * 0.2))
                            block_node.setScale(0.085)
                            block_pos += 1
                        except KeyError:
                            pass
        print("Inventory created in " + str(round(time.time() - inv_timer, 2)) + " seconds")

    def item_up(self):
        items = []
        for category in os.listdir("assets/meta"):
            if category != "structures":
                for blockmeta in os.listdir(f"assets/meta/{category}"):
                    with open(f"assets/meta/{category}/" + blockmeta, "r") as f:
                        block = json.load(f)
                        try:
                            if not block["textures"]["model"]:
                                items.append(block)
                        except KeyError:
                            items.append(block)
        if self.held_item < len(items) - 1:
            self.held_item += 1
            self.hold_item(items[self.held_item]["id"])
        else:
            self.held_item = 0
            self.hold_item(items[self.held_item]["id"])

    def item_down(self):
        items = []
        for category in os.listdir("assets/meta"):
            if category != "structures":
                for blockmeta in os.listdir(f"assets/meta/{category}"):
                    with open(f"assets/meta/{category}/" + blockmeta, "r") as f:
                        block = json.load(f)
                        try:
                            if not block["textures"]["model"]:
                                items.append(block)
                        except KeyError:
                            items.append(block)
        if self.held_item > 0:
            self.held_item -= 1
            self.hold_item(items[self.held_item]["id"])
        else:
            self.held_item = len(items) - 1
            self.hold_item(items[self.held_item]["id"])

    def hold_item(self, item: str):
        if self.item_is_held:
            for child in aspect2d.getChildren():
                if child.getName() == "held_item":
                    child.removeNode()
        else:
            self.item_is_held = True
        for category in os.listdir("assets/meta"):
            if category != "structures":
                for blockmeta in os.listdir(f"assets/meta/{category}"):
                    with open(f"assets/meta/{category}/" + blockmeta, "r") as f:
                        block = json.load(f)
                        if block["id"] == item:
                            item = block
        held_item = CardMaker("held_item")
        held_item.setFrame(-1, 1, -1, 1)
        held_item_node = aspect2d.attachNewNode(held_item.generate())
        held_item_node.setPos(0.9, 0, -0.9)
        held_item_node.setTransparency(1)
        print(item)
        try:
            held_item_texture = self.loader.loadTexture(Path("assets", "textures", "block", item["textures"]["front"]))
        except KeyError:
            held_item_texture = self.loader.loadTexture(Path("assets", "textures", "block", item["textures"]["2dcross"]))
        held_item_texture.setMagfilter(0)
        held_item_node.setTexture(held_item_texture, 1)
        held_item_node.setTwoSided(False)
        held_item_node.setBin("fixed", 0)
        held_item_node.setDepthTest(False)
        held_item_node.setDepthWrite(False)
        held_item_node.setScale(0.75)
        held_item_node.setHpr(25, 0, 0)

    def open_inventory(self):
        self.inventory_node.show()
        self.breaking_inhibitor = True
        self.props.setCursorHidden(False)
        base.win.requestProperties(self.props)
        self.mouse_camera_inhibitor = True

    def close_inventory(self):
        self.inventory_node.hide()
        self.breaking_inhibitor = False
        self.props.setCursorHidden(True)
        base.win.requestProperties(self.props)
        self.mouse_camera_inhibitor = False

    def spawn_entity(self, entity: str):
        # create a gltf model
        self.mob = self.loader.loadModel("assets/models/" + entity + ".gltf")
        self.mob.reparentTo(self.render)
        self.mob.setScale(4)

    def break_block(self):
        if not self.breaking_inhibitor:
            # Create a collision ray that starts at the camera's position and goes in the direction the camera is facing.
            camera = base.camNode
            collision_ray = CollisionRay()
            collision_ray.setOrigin(base.camera.getPos())
            look_vec = base.camera.getQuat().getForward()
            collision_ray.setDirection(look_vec)
        
            # Create a collision node for the ray.
            collision_node = CollisionNode('collision_ray')
            collision_node.addSolid(collision_ray)
            collision_node.setFromCollideMask(BitMask32.allOn())
            collision_node.setIntoCollideMask(BitMask32.allOff())
        
            # Attach the collision node to a new node path.
            collision_np = NodePath(collision_node)
            collision_np.reparentTo(base.render)
        
            # Create a collision traverser and a collision queue.
            traverser = CollisionTraverser()
            queue = CollisionHandlerQueue()
        
            # Add the collision node path to the traverser.
            traverser.addCollider(collision_np, queue)
        
            # Traverse the scene.
            traverser.traverse(base.render)
        
            # If the ray hit something, remove the hit object.
            print(queue)
            if queue.getNumEntries() > 0:
                queue.sortEntries()
                hit_obj = queue.getEntry(0).getIntoNodePath()
                print(hit_obj)
                hit_obj.removeNode()
        
            # Clean up.
            collision_np.removeNode()

    def floating_block(self):
        self.physnode = PhysicalNode("physnode")
        self.bignode.attachNewNode(self.physnode)
        self.create_cube("jukebox", (0, 4, 6), parentnode=self.bignode, cull=False)
        base.physicsMgr.attachPhysicalNode(self.physnode)
        base.physicsMgr.addLinearForce(self.gravityForce)

    def next_chunk(self):
        chunkx = 1
        chunkz = 0
        chunk = get_chunk(2, chunkx, chunkz)
        for block in chunk:
            coords = (block[0] + 32, block[1], block[2])
            self.create_cube(chunk[block], coords)
        self.bignode.flattenStrong()

    def create_world(self, task):
        timer = time.time()
        print("Creating World geometry")
        self.bignode = self.render.attachNewNode("bignode")
        self.bignode.node().setIntoCollideMask(BitMask32.bit(0))
        for block in self.world:
            self.create_cube(self.world[block], block, parentnode=self.bignode, cull=True)
        print("Finished creating world geometry in " + str(round(time.time() - timer, 2)) + " seconds")
        print("Flattening world geometry")
        flatten_timer = time.time()
        if self.config["Performance"]["flatten_geometry"]:
            self.bignode.flattenStrong()
        print("Finished flattening world geometry in " + str(round(time.time() - flatten_timer, 2)) + " seconds")
        # self.next_chunk()

    def zoom_out(self):
        self.camera.setY(self.camera, -100)

    def zoom_in(self):
        self.camera.setY(self.camera, 100)

    def zoom_in_smol(self):
        base.camLens.setFov(base.camLens.getFov() - 25)

    def zoom_out_smol(self):
        base.camLens.setFov(base.camLens.getFov() + 25)

    def toggle_fullscreen(self):
        self.props.setFullscreen(not base.win.isFullscreen())
        base.win.requestProperties(self.props)

    def toggle_wireframe(self):
        base.toggleWireframe()
        num_primatives = base.render.analyze()
        print(num_primatives)

    def mouseLook(self, task):
        if not self.mouse_camera_inhibitor:
            """Update the camera view based on mouse movement."""
            if base.mouseWatcherNode.hasMouse():
                # Get the mouse position
                md = base.win.getPointer(0)
                x = md.getX()
                y = md.getY()

                # Calculate the rotation based on mouse position
                # Adjust these factors to change the mouse sensitivity
                # Swap the control of pitch and heading
                base.camera.setP(base.camera.getP() - (y - base.win.getYSize()/2)*0.1)
                base.camera.setH(base.camera.getH() - (x - base.win.getXSize()/2)*0.1)

                # Reset the mouse cursor to the center of the screen
                base.win.movePointer(0, int(base.win.getXSize()/2), int(base.win.getYSize()/2))

        return Task.cont  # Continue the task indefinitely

    def find_neighbours(self, coords):
        neighbours = {"top": False, "bottom": False, "left": False, "right": False, "front": False, "back": False}
        if self.config["Performance"]["cull_neighboured_faces"]:
            if (coords[0], coords[1] - 2, coords[2]) in self.world and not "transparency" in self.thing_id_to_data(self.world[(coords[0], coords[1] - 2, coords[2])])["props"]:
                neighbours["top"] = True
            if (coords[0], coords[1] + 2, coords[2]) in self.world and not "transparency" in self.thing_id_to_data(self.world[(coords[0], coords[1] + 2, coords[2])])["props"]:
                neighbours["bottom"] = True
            if (coords[0] - 2, coords[1], coords[2]) in self.world and not "transparency" in self.thing_id_to_data(self.world[(coords[0] - 2, coords[1], coords[2])])["props"]:
                neighbours["left"] = True
            if (coords[0] + 2, coords[1], coords[2]) in self.world and not "transparency" in self.thing_id_to_data(self.world[(coords[0] + 2, coords[1], coords[2])])["props"]:
                neighbours["right"] = True
            if (coords[0], coords[1], coords[2] - 2) in self.world and not "transparency" in self.thing_id_to_data(self.world[(coords[0], coords[1], coords[2] - 2)])["props"]:
                neighbours["front"] = True
            if (coords[0], coords[1], coords[2] + 2) in self.world and not "transparency" in self.thing_id_to_data(self.world[(coords[0], coords[1], coords[2] + 2)])["props"]:
                neighbours["back"] = True
            if self.thing_id_to_data(self.world[coords])["id"] == "bedrock":
                neighbours["bottom"] = True

        if self.config["Performance"]["cull_faces_neighbouring_void"]:
            if self.world[(coords[0] - 2, 144, coords[2])] != "bedrock":
                neighbours["front"] = True
                neighbours["back"] = True
                neighbours["left"] = True
                neighbours["right"] = True
            elif self.world[(coords[0] + 2, 144, coords[2])] != "bedrock":
                neighbours["front"] = True
                neighbours["back"] = True
                neighbours["left"] = True
                neighbours["right"] = True
            elif self.world[(coords[0], 144, coords[2] - 2)] != "bedrock":
                neighbours["front"] = True
                neighbours["back"] = True
                neighbours["left"] = True
                neighbours["right"] = True
            elif self.world[(coords[0], 144, coords[2] + 2)] != "bedrock":
                neighbours["front"] = True
                neighbours["back"] = True
                neighbours["left"] = True
                neighbours["right"] = True
        return neighbours

    def create_cube(self, block: str, coords: tuple, parentnode, cull: bool):
        block_data = self.thing_id_to_data(block)
        original_coords = coords
        coords = (coords[0], coords[2], -coords[1])

        try:
            image = Path("assets", "textures", "block", block_data["textures"]["2dcross"])
            texture = self.loader.loadTexture(image)
            texture.setMagfilter(0)

            card = CardMaker("card")
            card.setFrame(-1, 1, -1, 1)
            node = self.render.attachNewNode(card.generate())

            node.setTexture(texture, 0)
            node.setTransparency(1)
            node.setHpr(45, 0, 0)
            node.setPos(coords[0], coords[1] + 1, coords[2])
            node.setTwoSided(True)

            card_3 = CardMaker("card_3")
            card_3.setFrame(-1, 1, -1, 1)
            node_3 = self.render.attachNewNode(card_3.generate())
            node_3.setPos(coords[0], coords[1] + 1, coords[2])
            node_3.setHpr(135, 0, 0)

            node_3.setTexture(texture, 0)
            node_3.setTransparency(1)
            node_3.setTwoSided(True)
        except KeyError:
            pass
        
        try:
            top = Path("assets", "textures", "block", block_data["textures"]["top"])
            bottom = Path("assets", "textures", "block", block_data["textures"]["bottom"])
            front = Path("assets", "textures", "block", block_data["textures"]["front"])
            back = Path("assets", "textures", "block", block_data["textures"]["back"])
            left = Path("assets", "textures", "block", block_data["textures"]["left"])
            right = Path("assets", "textures", "block", block_data["textures"]["right"])

            texture_dict = {}
            
            if (top == bottom) and (top == front) and (top == back) and (top == left) and (top == right):
                if top not in texture_dict:
                    texture_dict[top] = self.loader.loadTexture(top)
                    texture_dict[top].setMagfilter(0)
                texture = texture_2 = texture_3 = texture_4 = texture_5 = texture_6 = texture_dict[top]
            else:
                for tex_name in [front, bottom, top, back, left, right]:
                    if tex_name not in texture_dict:
                        texture_dict[tex_name] = self.loader.loadTexture(tex_name)
                texture = texture_dict[front]
                texture_2 = texture_dict[bottom]
                texture_3 = texture_dict[top]
                texture_4 = texture_dict[back]
                texture_5 = texture_dict[left]
                texture_6 = texture_dict[right]

            texture.setMagfilter(0)
            texture_2.setMagfilter(0)
            texture_3.setMagfilter(0)
            texture_4.setMagfilter(0)
            texture_5.setMagfilter(0)
            texture_6.setMagfilter(0)

            if cull:
                neighs = self.find_neighbours(original_coords)
            else:
                neighs = {"top": False, "bottom": False, "left": False, "right": False, "front": False, "back": False}

            try:
                transparency = 1 if block_data["props"]["transparency"] else 0
            except KeyError:
                transparency = 0

            if not neighs["front"]:
                card = CardMaker("card")
                card.setFrame(-1, 1, -1, 1)
                node = self.render.attachNewNode(card.generate())
                node.setPos(*coords)
                node.setTexture(texture, 0)
                node.setTransparency(transparency)
                if parentnode is not None:
                    node.reparentTo(parentnode)
                    node.node().setIntoCollideMask(BitMask32.allOn())
                # collision_node = CollisionNode("collision_node")
                # collision_node.addSolid(CollisionBox(Point3(0, 1, 0), 1, 1, 1))
                # collision_node_path = node.attachNewNode(collision_node)
                # collision_node_path.show()

            if not neighs["bottom"]:
                card_2 = CardMaker("card_2")
                card_2.setFrame(-1, 1, -1, 1)
                node_2 = self.render.attachNewNode(card_2.generate())
                node_2.setPos(coords[0], coords[1] + 1, coords[2] - 1)
                node_2.setHpr(0, 90, 0)
                node_2.setTransparency(transparency)
                if parentnode is not None:
                    node_2.reparentTo(parentnode)
                    node_2.node().setIntoCollideMask(BitMask32.allOn())
                # self.created_cards.append([coords[0], coords[1] + 1, coords[2] - 1])

                node_2.setTexture(texture_2, 0)

            if not neighs["top"]:
                card_3 = CardMaker("card_3")
                card_3.setFrame(-1, 1, -1, 1)
                node_3 = self.render.attachNewNode(card_3.generate())
                node_3.setPos(coords[0], coords[1] + 1, coords[2] + 1)
                node_3.setHpr(0, -90, 180)
                node_3.setTransparency(transparency)
                if parentnode is not None:
                    node_3.reparentTo(parentnode)
                    node_3.node().setIntoCollideMask(BitMask32.allOn())
                # self.created_cards.append([coords[0], coords[1] + 1, coords[2] + 1])

                node_3.setTexture(texture_3, 0)

            if not neighs["left"]:
                card_4 = CardMaker("card_4")
                card_4.setFrame(-1, 1, -1, 1)
                node_4 = self.render.attachNewNode(card_4.generate())
                node_4.setPos(coords[0] - 1, coords[1] + 1, coords[2])
                node_4.setHpr(-90, 0, 0)
                node_4.setTransparency(transparency)
                if parentnode is not None:
                    node_4.reparentTo(parentnode)
                    node_4.node().setIntoCollideMask(BitMask32.allOn())
                # self.created_cards.append([coords[0] - 1, coords[1] + 1, coords[2]])

                node_4.setTexture(texture_4, 0)

            if not neighs["right"]:
                card_5 = CardMaker("card_5")
                card_5.setFrame(-1, 1, -1, 1)
                node_5 = self.render.attachNewNode(card_5.generate())
                node_5.setPos(coords[0] + 1, coords[1] + 1, coords[2])
                node_5.setHpr(90, 0, 0)
                node_5.setTransparency(transparency)
                if parentnode is not None:
                    node_5.reparentTo(parentnode)
                    node_5.node().setIntoCollideMask(BitMask32.allOn())
                # self.created_cards.append([coords[0] + 1, coords[1] + 1, coords[2]])

                node_5.setTexture(texture_5, 0)

            if not neighs["back"]:
                card_6 = CardMaker("card_6")
                card_6.setFrame(-1, 1, -1, 1)
                node_6 = self.render.attachNewNode(card_6.generate())
                node_6.setPos(coords[0], coords[1] + 2, coords[2])
                node_6.setHpr(0, 180, 180)
                node_6.setTransparency(transparency)
                if parentnode is not None:
                    node_6.reparentTo(parentnode)
                    node_6.node().setIntoCollideMask(BitMask32.allOn())
                # self.created_cards.append([coords[0], coords[1] + 2, coords[2]])

                node_6.setTexture(texture_6, 0)
            
        except KeyError:
            pass

    def addHUD(self):
        text = "parablocks Alpha"
        OnscreenText(text=text, parent=base.a2dTopLeft, pos=(0.01, -0.07), fg=(1, 1, 1, 1), align=TextNode.ALeft, scale=.04, font=base.loader.loadFont("assets/fonts/pixel.ttf"))
        self.fps = OnscreenText(text="", parent=base.a2dTopRight, pos=(-0.1, -0.07), fg=(1, 1, 1, 1), align=TextNode.ARight, scale=.04, font=base.loader.loadFont("assets/fonts/pixel.ttf"), mayChange=True)
        self.fps_task = taskMgr.add(self.update_fps, "fps_task")
        # add crosshair
        crosshair = CardMaker("crosshair")
        crosshair.setFrame(-0.05/2, 0.05/2, -0.05/2, 0.05/2)
        crosshair_node = aspect2d.attachNewNode(crosshair.generate())
        crosshair_node.setPos(0, 0, 0)
        crosshair_node.setTransparency(1)
        texture = self.loader.loadTexture("assets/textures/misc/crosshair.png")
        texture.setMagfilter(0)
        crosshair_node.setTexture(texture, 1)
        crosshair_node.setTwoSided(False)
        crosshair_node.setBin("fixed", 0)
        crosshair_node.setDepthTest(False)
        crosshair_node.setDepthWrite(False)

    def update_fps(self, task):
        self.fps.setText("FPS: " + str(int(round(globalClock.getAverageFrameRate(), 0))))
        return Task.cont

    def change_fov(self, fov):
        # base.camLens.setFov(fov)
        pass
    
    def sprint(self):
        self.original_speed = self.speed
        self.speed = 0.45
        LerpFunc(self.change_fov, fromData=base.camLens.getFov(), toData=90, duration=0.5).start()
    
    def stop_sprinting(self):
        self.speed = self.original_speed
        LerpFunc(self.change_fov, fromData=base.camLens.getFov(), toData=75, duration=0.5).start()

    def start_moving_forward(self):
        """Start moving the camera forward in the direction it's currently facing."""
        self.moving_forward = True
        self.move_forward_task = taskMgr.add(self.move_forward, "move_forward_task")
    
    def stop_moving_forward(self):
        """Stop moving the camera forward."""
        self.moving_forward = False
        if self.move_forward_task:
            taskMgr.remove(self.move_forward_task)
            self.move_forward_task = None
    
    def move_forward(self, task):
        """Update the camera's position."""
        if self.moving_forward:
            # Get the camera's current orientation
            hpr = base.camera.getHpr()
        
            # Calculate the direction to move in
            direction = LVector3(math.sin(math.radians(-hpr[0])), math.cos(math.radians(-hpr[0])), 0)
        
            # Normalize the direction vector and scale it by the speed
            direction.normalize()
            direction *= self.speed
    
            # Get the time elapsed since the last frame
            dt = globalClock.getDt()
    
            # Update the camera's position
            base.camera.setPos(base.camera.getPos() + direction * dt * 75)
    
        return Task.cont  # Continue the task indefinitely

    def start_moving_backward(self):
        """Start moving the camera backward in the direction it's currently facing."""
        self.moving_backward = True
        self.move_backward_task = taskMgr.add(self.move_backward, "move_backward_task")

    def stop_moving_backward(self):
        """Stop moving the camera backward."""
        self.moving_backward = False
        if self.move_backward_task:
            taskMgr.remove(self.move_backward_task)
            self.move_backward_task = None

    def move_backward(self, task):
        """Update the camera's position."""
        if self.moving_backward:
            # Get the camera's current orientation
            hpr = base.camera.getHpr()

            # Calculate the direction to move in
            direction = LVector3(math.sin(math.radians(-hpr[0])), math.cos(math.radians(-hpr[0])), 0)

            # Normalize the direction vector and scale it by the speed
            direction.normalize()
            direction *= self.speed

            dt = globalClock.getDt()

            # Update the camera's position
            base.camera.setPos(base.camera.getPos() - direction * dt * 75)

        return Task.cont  # Continue the task indefinitely
    
    def start_moving_left(self):
        """Start moving the camera to the left."""
        self.moving_left = True
        self.move_left_task = taskMgr.add(self.move_left, "move_left_task")
        
    def stop_moving_left(self):
        """Stop moving the camera to the left."""
        self.moving_left = False
        if self.move_left_task:
            taskMgr.remove(self.move_left_task)
            self.move_left_task = None

    def move_left(self, task):
        """Update the camera's position."""
        if self.moving_left:
            # Get the camera's current orientation
            hpr = base.camera.getHpr()

            # Calculate the direction to move in
            direction = LVector3(math.sin(math.radians(-hpr[0] - 90)), math.cos(math.radians(-hpr[0] - 90)), 0)

            # Normalize the direction vector and scale it by the speed
            direction.normalize()
            direction *= self.speed

            dt = globalClock.getDt()

            # Update the camera's position
            base.camera.setPos(base.camera.getPos() + direction * dt * 75)

        return Task.cont
    
    def start_moving_right(self):
        """Start moving the camera to the right."""
        self.moving_right = True
        self.move_right_task = taskMgr.add(self.move_right, "move_right_task")

    def stop_moving_right(self):
        """Stop moving the camera to the right."""
        self.moving_right = False
        if self.move_right_task:
            taskMgr.remove(self.move_right_task)
            self.move_right_task = None

    def move_right(self, task):
        """Update the camera's position."""
        if self.moving_right:
            # Get the camera's current orientation
            hpr = base.camera.getHpr()

            # Calculate the direction to move in
            direction = LVector3(math.sin(math.radians(-hpr[0] + 90)), math.cos(math.radians(-hpr[0] + 90)), 0)

            # Normalize the direction vector and scale it by the speed
            direction.normalize()
            direction *= self.speed

            dt = globalClock.getDt()

            # Update the camera's position
            base.camera.setPos(base.camera.getPos() + direction * dt * 75)

        return Task.cont

    def start_moving_up(self):
        """Start moving the camera upwards."""
        self.moving_up = True
        self.move_up_task = taskMgr.add(self.move_up, "move_up_task")

    def stop_moving_up(self):
        """Stop moving the camera upwards."""
        self.moving_up = False
        if self.move_up_task:
            taskMgr.remove(self.move_up_task)
            self.move_up_task = None

    def move_up(self, task):
        """Update the camera's position."""
        if self.moving_up:
            # Update the camera's position
            base.camera.setZ(base.camera.getZ() + self.speed)
        return Task.cont  # Continue the task indefinitely

    def start_moving_down(self):
        """Start moving the camera downwards."""
        self.moving_down = True
        self.move_down_task = taskMgr.add(self.move_down, "move_down_task")

    def stop_moving_down(self):
        """Stop moving the camera downwards."""
        self.moving_down = False
        if self.move_down_task:
            taskMgr.remove(self.move_down_task)
            self.move_down_task = None

    def move_down(self, task):
        """Update the camera's position."""
        if self.moving_down:
            # Update the camera's position
            base.camera.setZ(base.camera.getZ() - self.speed)
        return Task.cont  # Continue the task indefinitely

    def thing_id_to_data(self, thing_id):
        for texture in textures:
            if textures[texture]["id"] == thing_id:
                return textures[texture]

if __name__ == "__main__":
    app = MainWindow()
    app.run()
