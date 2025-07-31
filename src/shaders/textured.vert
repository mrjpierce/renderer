#version 330

// Input vertex attributes (from vertex buffer)
layout (location = 0) in vec3 aPos;      // Vertex position (x, y, z)
layout (location = 1) in vec3 aColor;    // Vertex color (r, g, b)
layout (location = 2) in vec3 aNormal;   // Vertex normal (nx, ny, nz)
layout (location = 3) in vec2 aTexCoord; // Texture coordinates (u, v)

// Uniform variables (same for all vertices)
uniform mat4 model;       // Model matrix (local to world space)
uniform mat4 view;        // View matrix (world to camera space)
uniform mat4 projection;  // Projection matrix (camera to clip space)
uniform vec3 viewPos;     // Camera position in world space

// Output to fragment shader
out vec3 FragPos;       // Fragment position in world space
out vec3 Normal;        // Normal vector
out vec3 ourColor;      // Vertex color
out vec2 TexCoord;      // Texture coordinates

void main()
{
    // Transform vertex position to world space
    vec4 worldPos = model * vec4(aPos, 1.0);
    FragPos = worldPos.xyz;
    
    // Transform normal to world space (inverse transpose of 3x3 model matrix)
    mat3 normalMatrix = transpose(inverse(mat3(model)));
    Normal = normalize(normalMatrix * aNormal);
    
    // Pass color and texture coordinates to fragment shader
    ourColor = aColor;
    TexCoord = aTexCoord;
    
    // Final position in clip space
    gl_Position = projection * view * worldPos;
}
