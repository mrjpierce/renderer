"""
ModernGL 3D Renderer
-------------------
A simple 3D renderer built with Python, ModernGL, and GLFW.
This implementation demonstrates basic 3D rendering concepts including:
- Vertex and fragment shaders
- 3D transformations (model, view, projection matrices)
- Camera controls
- Basic lighting (ambient, diffuse, specular)
"""

import glfw                # For window creation and input handling
import moderngl            # Modern OpenGL bindings for Python
import numpy as np         # For numerical operations and array handling
import math               # For mathematical functions and constants
import sys                # For system-specific functions and variables
import time               # For timing and sleep functionality
import os                 # For file path operations
from pathlib import Path  # For cross-platform path handling
from PIL import Image     # For image loading (future texture support)
from pyrr import Matrix44, Vector3  # For 3D math operations

# Local imports
from model_loader import load_obj  # Our custom OBJ loader
from model import Model
from scene import Scene
from camera import Camera  # Our new Camera class

class Renderer:
    """
    Main renderer class that handles the 3D rendering pipeline.
    This class manages the OpenGL context, shaders, and rendering loop.
    """
    
    def __init__(self, width=800, height=600, title="ModernGL 3D Renderer", target_fps=0):
        """
        Initialize the renderer with the specified window dimensions and title.
        
        Args:
            width (int): Width of the window in pixels
            height (int): Height of the window in pixels
            title (str): Window title
            target_fps (int): Target frames per second (0 for unlimited)
        """
        # Window dimensions and title
        self.width = width
        self.height = height
        self.title = title
        
        # OpenGL context and objects (initialized later)
        self.ctx = None      # ModernGL context
        self.window = None   # GLFW window
        self.vao = None      # Vertex Array Object (holds vertex data and attributes)
        self.prog = None     # Shader program
        
        # Initialize the camera
        self.camera = Camera(
            position=Vector3([0.0, 0.0, 3.0]),  # Start slightly back from origin
            up=Vector3([0.0, 1.0, 0.0]),        # Y is up
            yaw=-90.0,                          # Look along -Z axis
            pitch=0.0                           # Level horizon
        )
        self.camera_speed = 2.5  # Base movement speed (will be scaled by delta_time)
        self.first_mouse = True  # Flag for initial mouse movement
        self.last_x = width / 2  # Last X position of the mouse
        self.last_y = height / 2  # Last Y position of the mouse
        
        # Timing variables for smooth movement and frame limiting
        self.delta_time = 0.0  # Time between current and last frame (in seconds)
        self.last_frame = 0.0  # Time of last frame
        self.target_fps = target_fps  # Target frames per second (0 = unlimited)
        self.frame_time = 1.0 / target_fps if target_fps > 0 else 0  # Target time per frame
        
        # Initialize the GLFW library
        if not glfw.init():
            raise Exception("Failed to initialize GLFW")
            
        # Configure GLFW window hints
        # These settings tell GLFW what version of OpenGL we want to use
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)  # OpenGL 3.x
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)  # OpenGL x.3
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)  # Use core profile
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, True)  # Required for macOS compatibility
        
        # Create the GLFW window
        self.window = glfw.create_window(width, height, title, None, None)
        if not self.window:
            glfw.terminate()
            raise Exception("Failed to create GLFW window")
            
        # Make the window's context current (required for OpenGL operations)
        glfw.make_context_current(self.window)
        
        # Create a ModernGL context
        # This gives us access to all OpenGL functions
        self.ctx = moderngl.create_context()
        
        # Print the OpenGL version for debugging
        print(f"OpenGL version: {self.ctx.version_code}")
        
        # Enable depth testing for proper 3D rendering
        self.ctx.enable(moderngl.DEPTH_TEST)
        
        # Enable face culling to improve performance and fix rendering artifacts
        self.ctx.enable(moderngl.CULL_FACE)
        self.ctx.cull_face = 'back'  # Cull back faces
        
        # Set the default front face winding order (counter-clockwise)
        self.ctx.front_face = 'ccw'
        
        # Set up GLFW callbacks
        # These functions will be called when specific events occur
        glfw.set_framebuffer_size_callback(self.window, self._on_resize)  # Window resize
        glfw.set_key_callback(self.window, self._on_key)  # Keyboard input
        
        # Scene management
        self.scene = Scene()

        # Initialize the renderer
        self._init_renderer()

        # Load default models
        self._load_default_models()
    
    def _load_texture(self, file_path):
        """
        Load a texture from an image file.
        
        Args:
            file_path (str): Path to the texture image file
            
        Returns:
            moderngl.Texture: The loaded texture
        """
        try:
            # Load the image using Pillow
            img = Image.open(file_path).convert('RGBA')
            
            # Create a texture
            texture = self.ctx.texture(
                img.size,  # Size
                4,         # Components (RGBA)
                img.tobytes()  # Image data
            )
            
            # Set texture parameters
            texture.build_mipmaps()
            texture.anisotropy = 16.0
            
            return texture
            
        except Exception as e:
            print(f"Error loading texture {file_path}: {e}")
            return None
    
    def load_model(self, name, file_path, position=None, rotation=None, scale=None):
        """
        Load a 3D model from an OBJ file with optional textures and add to the scene.
        """
        mesh_data = load_obj(file_path)
        model = Model(self.ctx, mesh_data, self.prog)
        # Load and set texture if available
        if mesh_data.material and getattr(mesh_data.material, 'diffuse_texture', None):
            texture = self._load_texture(mesh_data.material.diffuse_texture)
            model.set_texture(texture)
        self.scene.add_object(name, model, position, rotation, scale)
        print(f"Model loaded: {name} ({len(mesh_data.vertices)} vertices, {len(mesh_data.indices)} indices)")
        return model

    
    def _load_default_models(self):
        """No-op: removed colored cube and default models for simplified, texture-only renderer."""
        pass
    
    def render_model(self, name, position=None, rotation=None, scale=None):
        """
        Render a model from the scene with optional transform overrides.
        """
        obj = dict(self.scene.objects.get(name, {}))
        if not obj or 'model' not in obj:
            print(f"Model '{name}' not found in scene!")
            return
        model = obj['model']
        # Use overrides if provided, else use scene values
        position = position if position is not None else obj.get('position')
        rotation = rotation if rotation is not None else obj.get('rotation')
        scale = scale if scale is not None else obj.get('scale')

        # Start with an identity matrix
        model_matrix = Matrix44.identity()

        # Apply translation if specified
        if position is not None:
            model_matrix = model_matrix * Matrix44.from_translation(position)

        # Apply rotation if specified (in degrees)
        if rotation is not None:
            if isinstance(rotation, (list, tuple)) and len(rotation) >= 3:
                # Convert degrees to radians for rotation functions
                rot_x = math.radians(rotation[0])
                rot_y = math.radians(rotation[1])
                rot_z = math.radians(rotation[2])
                # Create rotation matrices and combine them
                rot_matrix = (
                    Matrix44.from_x_rotation(rot_x) *
                    Matrix44.from_y_rotation(rot_y) *
                    Matrix44.from_z_rotation(rot_z)
                )
                model_matrix = model_matrix * rot_matrix

        # Apply scaling if specified
        if scale is not None:
            if isinstance(scale, (list, tuple)) and len(scale) >= 3:
                model_matrix = model_matrix * Matrix44.from_scale(scale)
            else:
                scale_val = float(scale)
                model_matrix = model_matrix * Matrix44.from_scale([scale_val, scale_val, scale_val])

        # Update the model matrix in the shader
        self.prog['model'].write(model_matrix.astype('f4').tobytes())
        self.prog['viewPos'].write(np.array(self.camera.position, dtype='f4').tobytes())

        # Set material properties if available
        if hasattr(model, 'material') and model.material:
            mat = model.material
            self.prog['material.ambient'].value = tuple(mat.ambient)
            self.prog['material.diffuse'].value = tuple(mat.diffuse)
            self.prog['material.specular'].value = tuple(mat.specular)
            self.prog['material.shininess'].value = mat.shininess
            self.prog['material.useTexture'].value = getattr(model, 'has_texture', False)

        # Draw the model (handles texture bind and VAO render)
        model.draw(self.prog)

    
    def _load_shader(self, file_path):
        """
        Load shader source code from a file.
        
        Args:
            file_path (str): Path to the shader file
            
        Returns:
            str: Shader source code
            
        Raises:
            FileNotFoundError: If the shader file doesn't exist
        """
        try:
            with open(file_path, 'r') as file:
                return file.read()
        except FileNotFoundError:
            print(f"Error: Shader file not found: {file_path}")
            raise
    
    def _init_renderer(self):
        """
        Initialize the renderer by setting up shaders, vertex data, and OpenGL objects.
        This function is called once during initialization.
        """
        # Load shaders from files
        try:
            # Get the directory of the current script
            script_dir = os.path.dirname(os.path.abspath(__file__))
            
            # Load the textured shader by default
            vertex_shader = self._load_shader(os.path.join(script_dir, 'shaders', 'textured.vert'))
            fragment_shader = self._load_shader(os.path.join(script_dir, 'shaders', 'textured.frag'))
            
            # Create and compile the shader program
            self.prog = self.ctx.program(
                vertex_shader=vertex_shader,    # Vertex shader source code
                fragment_shader=fragment_shader # Fragment shader source code
            )
            
            # Set up texture uniform
            self.prog['texture_diffuse1'] = 0  # Use texture unit 0
            
            # Set up default material
            self.prog['material.ambient'].value = (0.2, 0.2, 0.2)
            self.prog['material.diffuse'].value = (0.8, 0.8, 0.8)
            self.prog['material.specular'].value = (1.0, 1.0, 1.0)
            self.prog['material.shininess'].value = 32.0
            self.prog['material.useTexture'].value = False
            
            # Set up default light
            self.prog['light.position'].value = (1.2, 1.0, 2.0)
            self.prog['light.ambient'].value = (0.2, 0.2, 0.2)
            self.prog['light.diffuse'].value = (0.8, 0.8, 0.8)
            self.prog['light.specular'].value = (1.0, 1.0, 1.0)
            
        except Exception as e:
            print(f"Error loading shaders: {e}")
            raise
        # Note: ModernGL handles shader compilation and linking for us
        # If there are any errors in the shaders, an exception will be raised here
        
        # Define vertex data for a 3D cube
        # Each vertex has a position (x,y,z) and a color (r,g,b)
        # The cube has 8 vertices (corners) and each vertex is shared by 3 faces
        # The format is: [x, y, z, r, g, b] for each vertex
        vertices = np.array([
            # Front face (red)
            -0.5, -0.5, -0.5,  1.0, 0.0, 0.0,  # Bottom-left
             0.5, -0.5, -0.5,  1.0, 0.0, 0.0,  # Bottom-right
             0.5,  0.5, -0.5,  1.0, 0.0, 0.0,  # Top-right
            -0.5,  0.5, -0.5,  1.0, 0.0, 0.0,  # Top-left
            # Back face (green)
            -0.5, -0.5,  0.5,  0.0, 1.0, 0.0,  # Bottom-left
             0.5, -0.5,  0.5,  0.0, 1.0, 0.0,  # Bottom-right
             0.5,  0.5,  0.5,  0.0, 1.0, 0.0,  # Top-right
            -0.5,  0.5,  0.5,  0.0, 1.0, 0.0,  # Top-left
        ], dtype='f4')  # 32-bit floating point format
        
        # Define the indices for the cube's triangles
        # Each face of the cube is made up of 2 triangles (6 vertices)
        # The numbers refer to the index of the vertex in the vertices array above
        # The order of vertices is important for face culling (default is counter-clockwise)
        indices = np.array([
            # Front face (2 triangles)
            0, 1, 2,  # First triangle (bottom-right)
            2, 3, 0,  # Second triangle (top-left)
            # Right face
            1, 5, 6,  # First triangle
            6, 2, 1,  # Second triangle
            # Back face
            5, 4, 7,  # First triangle
            7, 6, 5,  # Second triangle
            # Left face
            4, 0, 3,  # First triangle
            3, 7, 4,  # Second triangle
            # Top face
            3, 2, 6,  # First triangle
            6, 7, 3,  # Second triangle
            # Bottom face
            4, 5, 1,  # First triangle
            1, 0, 4   # Second triangle
        ], dtype='i4')  # 32-bit integer format
        
        # Create a vertex buffer object (VBO) to store vertex data on the GPU
        # This is more efficient than sending the data to the GPU every frame
        vbo = self.ctx.buffer(vertices)
        
        # Create an index buffer object (IBO/EBO) to store vertex indices
        # This allows us to reuse vertices and save memory
        ibo = self.ctx.buffer(indices)
        
        # Create vertex array object (VAO) for the default cube
        # This is kept for backward compatibility but will be replaced by model loading
        self.vao = self.ctx.vertex_array(
            self.prog,
            [
                # Layout (buffer, format, *attributes)
                # 3 floats for position (x, y, z), 3 floats for color (r, g, b), 3 floats for normal (nx, ny, nz)
                (vbo, '3f 3f 3f', 'aPos', 'aColor', 'aNormal')
            ],
            index_buffer=ibo  # Use the index buffer
        )
        
        # Enable depth testing
        # This ensures that objects closer to the camera are drawn on top of
        # objects that are further away
        self.ctx.enable(moderngl.DEPTH_TEST)
    
    def _on_resize(self, window, width, height):
        """
        Handle window resize events.
        
        Args:
            window: The GLFW window that was resized
            width (int): New width of the window
            height (int): New height of the window
        """
        self.width = width
        self.height = height
        self.ctx.viewport = (0, 0, width, height)
        
        # Update camera's aspect ratio
        if hasattr(self, 'camera') and self.camera is not None:
            self.camera.set_aspect_ratio(width, height)
    
    def _on_key(self, window, key, scancode, action, mods):
        if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
            glfw.set_window_should_close(window, True)
    
    def _process_movement(self):
        """
        Process keyboard input for camera movement.
        Handles WASD keys for movement and Shift for speed boost.
        """
        # Check for speed boost (Shift key)
        speed_boost = 1.5 if (glfw.get_key(self.window, glfw.KEY_LEFT_SHIFT) == glfw.PRESS or 
                            glfw.get_key(self.window, glfw.KEY_RIGHT_SHIFT) == glfw.PRESS) else 1.0
        
        # Process movement keys
        if glfw.get_key(self.window, glfw.KEY_W) == glfw.PRESS:
            self.camera.process_keyboard('FORWARD', self.delta_time, self.camera_speed * speed_boost)
        if glfw.get_key(self.window, glfw.KEY_S) == glfw.PRESS:
            self.camera.process_keyboard('BACKWARD', self.delta_time, self.camera_speed * speed_boost)
        if glfw.get_key(self.window, glfw.KEY_A) == glfw.PRESS:
            self.camera.process_keyboard('LEFT', self.delta_time, self.camera_speed * speed_boost)
        if glfw.get_key(self.window, glfw.KEY_D) == glfw.PRESS:
            self.camera.process_keyboard('RIGHT', self.delta_time, self.camera_speed * speed_boost)
            
    def _on_mouse_move(self, window, xpos, ypos):
        """
        Handle mouse movement to control camera orientation.
        
        Args:
            window: The GLFW window that received the event
            xpos (float): Current x-coordinate of the mouse
            ypos (float): Current y-coordinate of the mouse
        """
        if self.first_mouse:
            self.last_x = xpos
            self.last_y = ypos
            self.first_mouse = False
            return
        
        # Calculate offset from last position
        xoffset = xpos - self.last_x
        yoffset = self.last_y - ypos  # Reversed since y-coordinates go from bottom to top
        self.last_x = xpos
        self.last_y = ypos
        
        # Let the Camera class handle the orientation update
        self.camera.process_mouse_movement(xoffset, yoffset)
    
    def render(self):
        # Set up mouse callbacks
        glfw.set_cursor_pos_callback(self.window, self._on_mouse_move)
        glfw.set_input_mode(self.window, glfw.CURSOR, glfw.CURSOR_DISABLED)
        
        # Update camera aspect ratio based on window size
        self.camera.set_aspect_ratio(self.width, self.height)
        
        while not glfw.window_should_close(self.window):
            # Per-frame time logic
            current_frame = glfw.get_time()
            self.delta_time = current_frame - self.last_frame
            self.last_frame = current_frame
            
            # Process input
            self._process_movement()
            
            # Frame rate limiting
            if self.target_fps > 0:
                # Calculate time to sleep to maintain target FPS
                current_time = glfw.get_time()
                elapsed = current_time - self.last_frame
                if elapsed < self.frame_time:
                    # Sleep to maintain consistent frame rate
                    time_to_sleep = self.frame_time - elapsed
                    glfw.wait_events_timeout(time_to_sleep)
            
            # Clear the screen and depth buffer
            self.ctx.clear(0.1, 0.1, 0.1, 1.0)
            self.ctx.clear(depth=1.0)
            
            # Get view and projection matrices from camera
            view = self.camera.get_view_matrix()
            projection = self.camera.get_projection_matrix()
            
            # Set view and projection matrices in shader
            self.prog['view'].write(view.astype('f4').tobytes())
            self.prog['projection'].write(projection.astype('f4').tobytes())
            self.prog['viewPos'].write(np.array(self.camera.position, dtype='f4').tobytes())
            
            # Draw all objects in the scene
            for name, obj in self.scene.get_objects():
                self.render_model(name, obj.get('position'), obj.get('rotation'), obj.get('scale'))
        
            # Swap buffers and poll events
            glfw.swap_buffers(self.window)
            glfw.poll_events()
    
    def cleanup(self):
        if self.window:
            glfw.destroy_window(self.window)
        glfw.terminate()


def load_example_models(renderer):
    """Load example models for the demo."""
    # The colored cube is already loaded by default in _load_default_models()
    # You can add more models here if needed
    pass

def main():
    try:
        # Create the renderer with vsync (60 FPS)
        renderer = Renderer(width=1024, height=768, title="3D Model Viewer", target_fps=60)
        
        # Load example models
        load_example_models(renderer)
        
        # Start the rendering loop
        renderer.render()
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1
    finally:
        if 'renderer' in locals():
            renderer.cleanup()
    return 0

if __name__ == "__main__":
    sys.exit(main())
