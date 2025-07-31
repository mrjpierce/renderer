"""
Simple OBJ model loader for the ModernGL renderer.
Supports vertex positions, texture coordinates, and normals.
"""
import numpy as np
from collections import namedtuple
import os

# Simple data structure to hold mesh data
MeshData = namedtuple('MeshData', ['vertices', 'indices', 'has_texcoords', 'material'])

class Material:
    """Simple material class to hold material properties."""
    def __init__(self, name):
        self.name = name
        self.diffuse_texture = None
        self.ambient = [0.2, 0.2, 0.2]
        self.diffuse = [0.8, 0.8, 0.8]
        self.specular = [1.0, 1.0, 1.0]
        self.shininess = 100.0

def load_mtl(mtl_path):
    """
    Load materials from an MTL file.
    
    Args:
        mtl_path (str): Path to the .mtl file
        
    Returns:
        dict: Dictionary of Material objects keyed by material name
    """
    materials = {}
    current_material = None
    
    with open(mtl_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            parts = line.split()
            if not parts:
                continue
                
            if parts[0] == 'newmtl':
                current_material = Material(parts[1])
                materials[parts[1]] = current_material
            elif current_material:
                if parts[0] == 'Kd':
                    current_material.diffuse = [float(x) for x in parts[1:4]]
                elif parts[0] == 'Ka':
                    current_material.ambient = [float(x) for x in parts[1:4]]
                elif parts[0] == 'Ks':
                    current_material.specular = [float(x) for x in parts[1:4]]
                elif parts[0] == 'Ns':
                    current_material.shininess = float(parts[1])
                elif parts[0] == 'map_Kd':
                    # Handle texture paths (relative to MTL file)
                    tex_path = ' '.join(parts[1:])
                    mtl_dir = os.path.dirname(mtl_path)
                    current_material.diffuse_texture = os.path.join(mtl_dir, tex_path)
    
    return materials

def load_obj(file_path):
    """
    Load an OBJ file and return vertex and index data.
    
    Args:
        file_path (str): Path to the .obj file
        
    Returns:
        MeshData: A named tuple containing vertices, indices, and material info
    """
    vertices = []  # Will contain interleaved vertex data: [x,y,z, r,g,b, nx,ny,nz, u,v]
    indices = []   # Will contain face indices
    
    # Temporary storage for OBJ data
    temp_vertices = []
    temp_normals = []
    temp_texcoords = []
    
    # Vertex data storage
    vertices = []
    indices = []
    vertices_dict = {}  # Maps (v_idx, vt_idx, vn_idx) to vertex index
    
    # Material data
    materials = {}
    current_material = None
    has_texcoords = False
    
    # Check for MTL file
    mtl_path = os.path.splitext(file_path)[0] + '.mtl'
    if os.path.exists(mtl_path):
        materials = load_mtl(mtl_path)
    
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            parts = line.split()
            if not parts:
                continue
                
            # Parse vertex data
            if parts[0] == 'v':  # Vertex position
                temp_vertices.append([float(parts[1]), float(parts[2]), float(parts[3])])
            elif parts[0] == 'vt':  # Texture coordinate
                has_texcoords = True
                if len(parts) >= 3:  # Some models might have 3D texture coordinates
                    temp_texcoords.append([float(parts[1]), float(parts[2])])
            elif parts[0] == 'vn':  # Vertex normal
                temp_normals.append([float(parts[1]), float(parts[2]), float(parts[3])])
            elif parts[0] == 'usemtl':  # Material definition
                current_material = materials.get(parts[1])
            elif parts[0] == 'f':  # Face
                # For now, just handle simple triangulated faces
                # This will need to be expanded for more complex models
                face_vertex_indices = []
                for part in parts[1:]:
                    vertex_parts = part.split('/')
                    v_idx = int(vertex_parts[0]) - 1
                    vt_idx = int(vertex_parts[1]) - 1 if len(vertex_parts) > 1 and vertex_parts[1] else None
                    vn_idx = int(vertex_parts[2]) - 1 if len(vertex_parts) > 2 and vertex_parts[2] else None

                    vertex = temp_vertices[v_idx]
                    color = [1.0, 1.0, 1.0]
                    if current_material and hasattr(current_material, 'diffuse') and current_material.diffuse:
                        color = current_material.diffuse
                    normal = [0.0, 0.0, 1.0]
                    if vn_idx is not None and vn_idx < len(temp_normals):
                        normal = temp_normals[vn_idx]
                    texcoord = [0.0, 0.0]
                    if vt_idx is not None and vt_idx < len(temp_texcoords):
                        texcoord = temp_texcoords[vt_idx]
                    vertex_key = (v_idx, vt_idx if vt_idx is not None else -1, vn_idx if vn_idx is not None else -1)
                    if vertex_key in vertices_dict:
                        idx = vertices_dict[vertex_key]
                    else:
                        vertices.append(vertex + color + normal + texcoord)
                        idx = len(vertices) - 1
                        vertices_dict[vertex_key] = idx
                    face_vertex_indices.append(idx)
                # Triangulate face if needed
                if len(face_vertex_indices) == 3:
                    indices.extend(face_vertex_indices)
                elif len(face_vertex_indices) > 3:
                    for i in range(1, len(face_vertex_indices) - 1):
                        indices.extend([face_vertex_indices[0], face_vertex_indices[i + 1], face_vertex_indices[i]])
    
    # Convert to numpy arrays
    vertices_np = np.array(vertices, dtype='f4')
    indices_np = np.array(indices, dtype='i4')


    return MeshData(vertices=vertices_np, indices=indices_np, 
                   has_texcoords=has_texcoords, material=current_material)
