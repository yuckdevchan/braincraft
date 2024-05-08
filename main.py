from direct.showbase.ShowBase import ShowBase
from panda3d.core import CardMaker, TextureStage, loadPrcFileData, WindowProperties, Vec3
from direct.task import Task
from direct.showbase.DirectObject import DirectObject
from panda3d.core import ClockObject, LVector3, CollisionRay, CollisionNode, CollisionTraverser, CollisionHandlerQueue
from direct.interval.LerpInterval import LerpFunc
from direct.showbase.ShowBaseGlobal import globalClock
from panda3d.core import WindowProperties
from pathlib import Path
import math

from build_textures import build_textures
textures = build_textures()
from build_world import build_world
world = build_world()

class MainWindow(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        
        self.move_forward_task = None
        self.move_backward_task = None
        self.move_left_task = None
        self.move_right_task = None
        self.move_up_task = None
        self.move_down_task = None
        self.sprint_task = None

        props = WindowProperties()
        props.setTitle("Braincraft")
        props.setSize(3840, 2160)
        props.setCursorHidden(True)
        # props.setFullscreen(True)
        props.setIconFilename("assets/textures/icon.ico")
        self.win.requestProperties(props)
        # Enable the frame rate meter
        loadPrcFileData("", "show-frame-rate-meter 1")

        # Unlock the framerate
        loadPrcFileData("", "sync-video 0")

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
        # self.accept("mouse1", self.place_block)

        for block in world:
            self.create_cube(block["block"], block["coords"])
            
        self.disableMouse()
        self.mouseLookTask = taskMgr.add(self.mouseLook, "mouseLookTask")
        base.camLens.setNearFar(0.1, 1000)
        base.camLens.setFov(75)

    def toggle_fullscreen(self):
        props = WindowProperties()
        props.setFullscreen(not base.win.isFullscreen())
        base.win.requestProperties(props)

    def toggle_wireframe(self):
        base.toggleWireframe()

    def mouseLook(self, task):
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

    def create_cube(self, block, coords):
        coords = (coords[0], coords[2], -coords[1])
        block_data = self.thing_id_to_data(block)
        card = CardMaker("card")
        card.setFrame(-1, 1, -1, 1)
        node = self.render.attachNewNode(card.generate())
        node.setPos(*coords)
    
        top = Path("assets", "textures", "block", block_data["textures"]["top"])
        bottom = Path("assets", "textures", "block", block_data["textures"]["bottom"])
        front = Path("assets", "textures", "block", block_data["textures"]["front"])
        back = Path("assets", "textures", "block", block_data["textures"]["back"])
        left = Path("assets", "textures", "block", block_data["textures"]["left"])
        right = Path("assets", "textures", "block", block_data["textures"]["right"])
    
        texture = self.loader.loadTexture(front)
        texture.setMagfilter(0)
        node.setTexture(texture, 0)

        card_2 = CardMaker("card_2")
        card_2.setFrame(-1, 1, -1, 1)
        node_2 = self.render.attachNewNode(card_2.generate())
        node_2.setPos(coords[0], coords[1] + 1, coords[2] - 1)
        node_2.setHpr(0, 90, 0)

        texture_2 = self.loader.loadTexture(bottom)
        texture_2.setMagfilter(0)
        node_2.setTexture(texture_2, 0)

        card_3 = CardMaker("card_3")
        card_3.setFrame(-1, 1, -1, 1)
        node_3 = self.render.attachNewNode(card_3.generate())
        node_3.setPos(coords[0], coords[1] + 1, coords[2] + 1)
        node_3.setHpr(0, -90, 180)

        texture_3 = self.loader.loadTexture(top)
        texture_3.setMagfilter(0)
        node_3.setTexture(texture_3, 0)

        card_4 = CardMaker("card_4")
        card_4.setFrame(-1, 1, -1, 1)
        node_4 = self.render.attachNewNode(card_4.generate())
        node_4.setPos(coords[0] - 1, coords[1] + 1, coords[2])
        node_4.setHpr(-90, 0, 0)

        texture_4 = self.loader.loadTexture(back)
        texture_4.setMagfilter(0)
        node_4.setTexture(texture_4, 0)

        card_5 = CardMaker("card_5")
        card_5.setFrame(-1, 1, -1, 1)
        node_5 = self.render.attachNewNode(card_5.generate())
        node_5.setPos(coords[0] + 1, coords[1] + 1, coords[2])
        node_5.setHpr(90, 0, 0)

        texture_5 = self.loader.loadTexture(left)
        texture_5.setMagfilter(0)
        node_5.setTexture(texture_5, 0)

        card_6 = CardMaker("card_6")
        card_6.setFrame(-1, 1, -1, 1)
        node_6 = self.render.attachNewNode(card_6.generate())
        node_6.setPos(coords[0], coords[1] + 2, coords[2])
        node_6.setHpr(0, 180, 180)

        texture_6 = self.loader.loadTexture(right)
        texture_6.setMagfilter(0)
        node_6.setTexture(texture_6, 0)

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
        
            # Update the camera's position
            base.camera.setPos(base.camera.getPos() + direction)
    
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

            # Update the camera's position
            base.camera.setPos(base.camera.getPos() - direction)

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

            # Update the camera's position
            base.camera.setPos(base.camera.getPos() + direction)

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

            # Update the camera's position
            base.camera.setPos(base.camera.getPos() + direction)

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
