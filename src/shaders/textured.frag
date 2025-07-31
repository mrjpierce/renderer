#version 330

// Inputs from vertex shader (interpolated)
in vec3 FragPos;     // Fragment position in world space
in vec3 Normal;      // Normal vector
in vec3 ourColor;    // Vertex color
in vec2 TexCoord;    // Texture coordinates

// Output color of the pixel
out vec4 FragColor;

// Material properties
struct Material {
    vec3 ambient;
    vec3 diffuse;
    vec3 specular;
    float shininess;
    bool useTexture;
};

// Light properties
struct Light {
    vec3 position;
    vec3 ambient;
    vec3 diffuse;
    vec3 specular;
};

// Uniforms
uniform Material material;
uniform Light light;
uniform vec3 viewPos;
uniform sampler2D texture_diffuse1;

void main()
{
    // Sample the texture if enabled, otherwise use vertex color
    vec3 objectColor = material.useTexture ? texture(texture_diffuse1, TexCoord).rgb : ourColor;
    
    // Ambient
    vec3 ambient = light.ambient * material.ambient * objectColor;
    
    // Diffuse
    vec3 norm = normalize(Normal);
    vec3 lightDir = normalize(light.position - FragPos);
    float diff = max(dot(norm, lightDir), 0.0);
    vec3 diffuse = light.diffuse * (diff * material.diffuse) * objectColor;
    
    // Specular
    vec3 viewDir = normalize(viewPos - FragPos);
    vec3 reflectDir = reflect(-lightDir, norm);
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), material.shininess);
    vec3 specular = light.specular * (spec * material.specular);
    
    // Combine results
    vec3 result = ambient + diffuse + specular;
    FragColor = vec4(result, 1.0);
}
