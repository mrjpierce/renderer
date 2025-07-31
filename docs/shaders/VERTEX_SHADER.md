# Vertex Shader Documentation

## File: `src/shaders/textured.vert`

## Overview
The vertex shader is responsible for processing each vertex of the 3D models in the scene. It transforms vertex positions from local object space to clip space and prepares data for the fragment shader.

## Inputs

### Vertex Attributes
- `aPos` (vec3): Vertex position in local space (x, y, z)
- `aColor` (vec3): Vertex color (r, g, b)
- `aNormal` (vec3): Vertex normal vector (nx, ny, nz)
- `aTexCoord` (vec2): Texture coordinates (u, v)

### Uniform Variables
- `model` (mat4): Model matrix (local to world space transformation)
- `view` (mat4): View matrix (world to camera space transformation)
- `projection` (mat4): Projection matrix (camera to clip space transformation)

## Outputs
- `FragPos` (vec3): Fragment position in world space
- `Normal` (vec3): Transformed normal vector in world space
- `ourColor` (vec3): Vertex color passed to fragment shader
- `TexCoord` (vec2): Texture coordinates passed to fragment shader
- `gl_Position` (vec4): Final vertex position in clip space (built-in output)

## Processing Steps
1. **World Space Transformation**:
   - Multiplies the vertex position by the model matrix to transform it to world space
   - Stores the world space position in `FragPos` for lighting calculations

2. **Normal Transformation**:
   - Applies the inverse transpose of the model matrix to the normal vector
   - Ensures correct lighting when non-uniform scaling is applied
   - Normalizes the result to maintain unit length

3. **Color Passing**:
   - Simply passes the vertex color to the fragment shader

4. **Clip Space Transformation**:
   - Applies the full model-view-projection transformation
   - Stores the result in `gl_Position` for rasterization

## Usage Notes
- The shader is designed to work with 3D models containing position, color, normal, and texture coordinate data.
- It passes both color and texture coordinates to the fragment shader for flexible material and texture support.
- The normal matrix calculation handles non-uniform scaling correctly.
- This vertex shader is paired with a fragment shader that uses Material and Light structs for physically-based lighting and supports both textured and untextured models.

## Dependencies
- Requires OpenGL 3.3 or higher
- Expects the model to have proper normal vectors and texture coordinates for correct lighting and texturing
