# ModernGL 3D Renderer

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://www.python.org/)

A bare-bones, cross-platform 3D renderer built with Python, ModernGL, and GLFW.

---

## Quickstart

1. **Install dependencies** (see below).
2. **Run the renderer:**
   ```bash
   python renderer.py
   ```
3. **Try the included test:**
   ```bash
   cd tests/render_model
   python test_render_model.py
   ```
   This will open a window with a textured cube you can move around.

---

## Concepts Overview (How it Works)

This renderer is designed to be easy to learn and extend. Here’s a high-level view of how it works:

1. **Renderer Initialization**: Sets up a window, OpenGL context, and loads shaders.
2. **Model Loading**: Loads 3D models (OBJ format) and their materials/textures.
3. **Rendering Loop**: Handles user input, updates the camera, and draws all loaded models each frame.
4. **Shaders**: GPU programs (GLSL) that control how models are drawn and lit.
5. **Controls**: Move the camera with WASD, look around with the mouse.

**Typical Flow:**
- You create a `Renderer`.
- Load models with `renderer.load_model()`.
- Call `renderer.render()` to start the interactive window.

For a deeper dive, see [`docs/RENDERER_DETAILS.md`](docs/RENDERER_DETAILS.md).

---

## Features

- Cross-platform (Windows, macOS, Linux)
- Modern OpenGL (3.3 Core Profile)
- Simple and clean codebase
- Basic window management with GLFW
- Textured 3D model loading (OBJ+MTL)
- Physically-based lighting (Phong/Blinn-Phong)
- Texture/material support (diffuse maps)
- Camera controls (WASD + mouse look)

---

## Requirements

- Python 3.7+
- pip (Python package manager)

---

## Installation

1. Clone this repository
2. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

---

## Controls

- `WASD`: Move camera
- Mouse: Look around
- `ESC`: Close the window

---

## Project Structure

- `src/`: Main source code
  - `renderer.py`: Main renderer implementation
  - `scene.py`: Manages 3D objects and their transforms
  - `model_loader.py`: OBJ/MTL model and material loader
  - `model.py`: Model abstraction
  - `shaders/`: Vertex and fragment shaders (GLSL)
- `docs/`: Technical and shader documentation
- `tests/`: Example tests and assets
- `models/`: Example 3D model assets
- `requirements.txt`: Python dependencies

---

## Example Usage

Load and render a textured OBJ model (managed by the Scene class):
```python
from renderer import Renderer
renderer = Renderer()
renderer.load_model('my_cube', 'models/textured_cube.obj')  # Adds model to renderer.scene
# The model is now managed by renderer.scene
renderer.render()
```

---

## Learning & Documentation

- **Technical docs:** See [`docs/RENDERER_DETAILS.md`](docs/RENDERER_DETAILS.md) for architecture, pipeline, and extension guides.
- **Shader docs:** See [`docs/shaders/`](docs/shaders/) for details on GLSL shaders and how the pipeline works.
- **Test walkthrough:** [`tests/render_model/README.md`](tests/render_model/README.md) explains the sample test and assets.

---

## Glossary

- **Scene:** A container for all renderable objects, managing models and their transforms (position, rotation, scale).
- **Shader:** Program that runs on the GPU to process vertices or pixels.
- **Material:** Set of parameters (e.g., textures, colors) and a reference to a shader, describing how a surface appears.
- **Model:** 3D geometry (mesh) that can be rendered.
- **VBO/IBO/VAO:** GPU buffer objects for storing vertex/index data and attribute layouts.
- **Uniform:** Parameter sent to the shader (e.g., transformation matrix, color).

---

## Controls

- `WASD`: Move camera
- Mouse: Look around
- `ESC`: Close the window



## License

This project is open source and available under the MIT License.
