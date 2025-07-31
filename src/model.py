import moderngl

class Model:
    """
    Represents a 3D model with its own VAO, VBO, IBO, material, and texture.
    Handles its own OpenGL resource creation and rendering.
    """
    def __init__(self, ctx: moderngl.Context, mesh_data, program):
        self.ctx = ctx
        self.program = program
        self.material = mesh_data.material
        self.has_texture = False
        self.texture = None

        # Create buffers
        self.vbo = ctx.buffer(mesh_data.vertices.tobytes())
        self.ibo = ctx.buffer(mesh_data.indices.tobytes())
        self.index_count = len(mesh_data.indices)

        # Always use the full 11-float format
        self.vao = ctx.vertex_array(
            program,
            [(self.vbo, '3f 3f 3f 2f', 'aPos', 'aColor', 'aNormal', 'aTexCoord')],
            index_buffer=self.ibo,
            skip_errors=True
        )

        # Handle texture if present
        if self.material and getattr(self.material, 'diffuse_texture', None):
            # Texture loading should be handled by renderer or a texture manager
            pass  # To be set externally for now

    def set_texture(self, texture):
        self.texture = texture
        self.has_texture = texture is not None

    def draw(self, program=None):
        # Optionally bind material/texture uniforms here
        if self.has_texture and self.texture:
            self.texture.use(location=0)
        self.vao.render()

    def cleanup(self):
        self.vbo.release()
        self.ibo.release()
        self.vao.release()
        # Texture cleanup if needed
