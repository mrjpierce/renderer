# Fragment Shader Documentation

## File: `src/shaders/textured.frag`

## Overview
The fragment shader calculates the final color of each pixel by applying lighting calculations to the interpolated vertex data. It implements a physically-based lighting model with ambient, diffuse, and specular components, supporting both textured and untextured rendering.

## Inputs (from Vertex Shader)
- `FragPos` (vec3): Fragment position in world space
- `Normal` (vec3): Interpolated normal vector in world space
- `ourColor` (vec3): Interpolated vertex color
- `TexCoord` (vec2): Interpolated texture coordinates

## Uniform Variables
- `light` (Light struct): Light properties (position, color, etc.)
- `material` (Material struct): Material properties (ambient, diffuse, specular, etc.)
- `viewPos` (vec3): Position of the camera in world space (must be set by the application)

## Outputs
- `FragColor` (vec4): Final RGBA color of the fragment

## Lighting and Material System

Lighting is computed using a physically-based model with ambient, diffuse, and specular components. The shader uses Material and Light structs for flexibility and clarity.

- **Material struct**: Controls ambient, diffuse, specular reflectivity, shininess, and whether to use a texture.
- **Light struct**: Controls light position and color properties.

### Texture Support
- If `material.useTexture` is true, the fragment color is sampled from the diffuse texture using `TexCoord`.
- Otherwise, the vertex color is used as the base color.

### Lighting Calculation
- Ambient: `light.ambient * material.ambient * objectColor`
- Diffuse: `light.diffuse * (diff * material.diffuse) * objectColor`
- Specular: `light.specular * (spec * material.specular)`

The final color is the sum of these components, output as `FragColor`.

```glsl
vec3 objectColor = material.useTexture ? texture(texture_diffuse1, TexCoord).rgb : ourColor;
vec3 ambient = light.ambient * material.ambient * objectColor;
vec3 diffuse = light.diffuse * (diff * material.diffuse) * objectColor;
vec3 specular = light.specular * (spec * material.specular);
vec3 result = ambient + diffuse + specular;
FragColor = vec4(result, 1.0);
```

## Performance Considerations
- The specular calculation includes a `pow()` operation which can be expensive
- The normal is re-normalized to account for interpolation artifacts
- The shader performs all calculations in world space for clarity

## Customization
To modify the lighting:
1. Adjust `material.ambient`, `material.diffuse`, and `material.specular` for material properties
2. Change `light.ambient`, `light.diffuse`, and `light.specular` for light properties
1. Adjust `ambientStrength` for ambient light intensity
2. Change `specularStrength` for highlight intensity
3. Modify the exponent in the specular calculation for highlight size
4. Update `lightPos` and `lightColor` for different lighting setups

## Dependencies
- Requires OpenGL 3.3 or higher
- Expects normalized normal vectors from the vertex shader
- Assumes light and view positions are in world space
