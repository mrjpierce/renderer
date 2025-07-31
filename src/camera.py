"""
Camera Module
------------
Handles all camera-related functionality including:
- Camera position and orientation
- View matrix calculations
- Camera movement and rotation
- Projection matrix setup
"""

import math
from pyrr import Matrix44, Vector3, Vector4

class Camera:
    """
    A 3D camera that handles view and projection matrices.
    
    This class manages the camera's position, orientation, and projection settings,
    providing methods to update the view matrix as the camera moves or looks around.
    
    Attributes:
        position (Vector3): The camera's position in world space
        front (Vector3): The camera's forward direction vector
        up (Vector3): The camera's up vector
        right (Vector3): The camera's right vector
        world_up (Vector3): The world's up vector (typically [0, 1, 0])
        yaw (float): Rotation around the Y axis (in degrees)
        pitch (float): Rotation around the X axis (in degrees)
        fov (float): Field of view (in degrees)
        aspect_ratio (float): Viewport aspect ratio (width/height)
        near_plane (float): Near clipping plane distance
        far_plane (float): Far clipping plane distance
    """
    
    def __init__(self, position=None, up=None, yaw=-90.0, pitch=0.0):
        """
        Initialize the camera with default or specified values.
        
        Args:
            position (Vector3, optional): Initial camera position. Defaults to (0, 0, 3).
            up (Vector3, optional): World up vector. Defaults to (0, 1, 0).
            yaw (float, optional): Initial yaw angle in degrees. Defaults to -90.0.
            pitch (float, optional): Initial pitch angle in degrees. Defaults to 0.0.
        """
        # Camera attributes with default values
        self.position = position if position is not None else Vector3([0.0, 0.0, 3.0])
        self.world_up = Vector3(up) if up is not None else Vector3([0.0, 1.0, 0.0])
        self.yaw = yaw
        self.pitch = pitch
        
        # Camera orientation vectors
        self.front = Vector3([0.0, 0.0, -1.0])
        self.right = Vector3()
        self.up = Vector3()
        
        # Projection parameters
        self.fov = 45.0
        self.aspect_ratio = 16.0 / 9.0  # Will be updated by window resize
        self.near_plane = 0.1
        self.far_plane = 100.0
        
        # Update the camera vectors
        self._update_vectors()
    
    def get_view_matrix(self):
        """
        Calculate the view matrix using the camera's position and orientation.
        
        Returns:
            Matrix44: The 4x4 view matrix
        """
        target = self.position + self.front
        return Matrix44.look_at(
            self.position.xyz,
            target.xyz,
            self.up.xyz
        )
    
    def get_projection_matrix(self):
        """
        Calculate the projection matrix using the camera's projection parameters.
        
        Returns:
            Matrix44: The 4x4 projection matrix
        """
        return Matrix44.perspective_projection(
            self.fov, 
            self.aspect_ratio, 
            self.near_plane, 
            self.far_plane
        )
    
    def process_keyboard(self, direction, delta_time, camera_speed=2.5):
        """
        Process keyboard input for camera movement.
        
        Args:
            direction (str): Direction to move ('FORWARD', 'BACKWARD', 'LEFT', 'RIGHT')
            delta_time (float): Time since last frame (for framerate-independent movement)
            camera_speed (float, optional): Movement speed multiplier. Defaults to 2.5.
        """
        velocity = camera_speed * delta_time
        
        if direction == 'FORWARD':
            self.position += self.front * velocity
        if direction == 'BACKWARD':
            self.position -= self.front * velocity
        if direction == 'LEFT':
            self.position -= self.right * velocity
        if direction == 'RIGHT':
            self.position += self.right * velocity
    
    def process_mouse_movement(self, xoffset, yoffset, constrain_pitch=True):
        """
        Process mouse movement to rotate the camera.
        
        Args:
            xoffset (float): Mouse x offset from last frame
            yoffset (float): Mouse y offset from last frame
            constrain_pitch (bool, optional): Whether to constrain the pitch. Defaults to True.
        """
        sensitivity = 0.1
        xoffset *= sensitivity
        yoffset *= sensitivity
        
        self.yaw += xoffset
        self.pitch += yoffset
        
        # Constrain pitch to prevent screen flip
        if constrain_pitch:
            self.pitch = max(-89.0, min(89.0, self.pitch))
        
        # Update front, right, and up vectors
        self._update_vectors()
    
    def process_mouse_scroll(self, yoffset):
        """
        Process mouse scroll to zoom in/out (adjust FOV).
        
        Args:
            yoffset (float): Scroll wheel delta
        """
        self.fov = max(1.0, min(45.0, self.fov - yoffset))
    
    def _update_vectors(self):
        """
        Update the camera's front, right, and up vectors based on yaw and pitch.
        This is called internally when the camera's orientation changes.
        """
        # Calculate the new front vector
        front = Vector3([
            math.cos(math.radians(self.yaw)) * math.cos(math.radians(self.pitch)),
            math.sin(math.radians(self.pitch)),
            math.sin(math.radians(self.yaw)) * math.cos(math.radians(self.pitch))
        ])
        self.front = front.normalized
        
        # Re-calculate right and up vectors
        self.right = self.front.cross(self.world_up).normalized
        self.up = self.right.cross(self.front).normalized
    
    def set_aspect_ratio(self, width, height):
        """
        Update the camera's aspect ratio when the window is resized.
        
        Args:
            width (int): New window width in pixels
            height (int): New window height in pixels
        """
        if height == 0:
            height = 1  # Prevent division by zero
        self.aspect_ratio = width / float(height)
