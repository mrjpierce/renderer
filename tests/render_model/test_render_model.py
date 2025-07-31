"""
Render Model Test

Loads and displays a textured cube using the ModernGL renderer.
"""
import sys
import os
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))
from renderer import Renderer
from PIL import Image, ImageDraw

# Optionally: set up test-specific paths if running from project root
if __name__ == "__main__":
    # Create renderer and load the test model
    renderer = Renderer()
    model_path = os.path.join(os.path.dirname(__file__), "textured_cube.obj")
        # Load the model and print mesh data size
    mesh_data = None
    try:
        from model_loader import load_obj
        mesh_data = load_obj(model_path)
        pass  # No debug prints, keep syntax valid
    except Exception as e:
        pass  # Optionally handle error or log
    renderer.load_model("test_cube", model_path)
    assert "test_cube" in renderer.scene.objects
    renderer.render()
