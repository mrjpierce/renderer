# Render Model Test

This test demonstrates the complete workflow for loading and rendering a textured 3D model using the ModernGL renderer, now with modular scene management.

## What it does
- Loads a sample OBJ model (`textured_cube.obj`) and its material (`textured_cube.mtl`)
- Loads the associated texture (`test_texture.png`)
- Initializes the renderer, adds the model to the scene, and displays it with interactive camera controls (WASD + mouse look)
- Demonstrates the new `Scene` class for managing renderable objects
- Verifies that the renderer's texture/material pipeline, shaders, and model loader are working as expected

## How to run
```bash
python test_render_model.py
```

## Expected result
A window opens displaying a textured cube. You can move the camera with WASD and look around with the mouse. The cube should appear correctly textured and lit, with no spiky artifacts or geometry issues.
