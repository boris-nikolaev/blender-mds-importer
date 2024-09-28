import bpy
import math
import random
import os
import re
from .mds_types import *

class Submesh():
    def __init__(self):
        vertices = []
        triangles = []
        uv_triangles = []
        uv_vertices = []
        material_index = -1

class MDSMesh():
    def __init__(self):
        vertices  = []
        uv_vertices = []
        submeshes = []

class MDSModel():
    def __init__(self):
        meshes = []
        materials = []


def import_model(file_path):
    with open(file_path, 'rb') as f:
        data = f.read()

        mds_header = MDSHeader.from_buffer_copy(data)
        model = MDSModel()
        model.meshes = []
        model.materials = []

        # read bones
        bone_offset = mds_header.header_size

        # read unk_struct
        unk_struct_offset = bone_offset + (mds_header.bone_struct_size * mds_header.bone_count)

        # read materials
        material_block_offset = unk_struct_offset + (mds_header.unk_struct_size * mds_header.unk_struct_count)
        material_block = data[material_block_offset : material_block_offset + mds_header.material_block_size - 1]
        material_block = material_block.replace(b'\x00', b' ')
        decoded_string = material_block.decode('ascii')
        decoded_string = re.sub(r'\s+', ' ', decoded_string)
        decoded_string = decoded_string.split("Default ")[1]

        mat_split = decoded_string.split(' ')
        for index in range(0, len(mat_split) - 1, 2):
            mat_name = mat_split[index]
            tex_name = mat_split[index + 1]
            model.materials.append([mat_name, tex_name])

        # read mdt
        mdt_offset = material_block_offset + mds_header.material_block_size
        current_mdt_offset = mdt_offset
        for object_index in range(mds_header.object_count):
            mesh = MDSMesh()
            mdt_header = MDTHeader.from_buffer_copy(data, current_mdt_offset)

            # read vertices
            mesh.vertices = []
            vertex_offset = current_mdt_offset + mdt_header.vertex_count_offset + mdt_header.vertex_offset

            for vertex_index in range(mdt_header.vertex_count):
                co = ShortVector3.from_buffer_copy(data, vertex_offset)
                vertex_offset += ShortVector3.size()

                new_co = co.multiply(mdt_header.mesh_scale_x, mdt_header.mesh_scale_y, mdt_header.mesh_scale_z)
                new_co = [i * 0.000001 for i in new_co] # multiplier was chosen empirically
                mesh.vertices.append(new_co)

            # read texcoords
            mesh.uv_vertices = []
            uv_offset = current_mdt_offset + mdt_header.vertex_count_offset + mdt_header.uv_offset
            for uv_index in range(mdt_header.uv_count):
                co = ByteVector2.from_buffer_copy(data, uv_offset)
                uv_offset += ByteVector2.size()

                new_co = [(co.x / 128) * mdt_header.uv_scale_x, (-co.y / 128) * mdt_header.uv_scale_y]
                mesh.uv_vertices.append(new_co)

            # read triangle groups
            mesh.submeshes = []
            triangle_group_offset = current_mdt_offset + mdt_header.vertex_attribute_size
            current_group_offset = triangle_group_offset
            for group_index in range(mdt_header.triangle_group_count):
                submesh = Submesh()

                group_header = TriangleGroupHeader.from_buffer_copy(data, current_group_offset)

                if group_header.header_size == 32:
                    current_group_offset += group_header.next_offset
                    continue

                # read triangles
                triangle_index_map = {}
                submesh.triangles = []
                submesh.vertices = []

                skipped_indices = []

                triangle_index_offset = current_group_offset + group_header.header_size
                if group_header.read_mode == 3:
                    for i in range(int(group_header.index_count / 3)):
                        indices = ShortVector3.from_buffer_copy(data, triangle_index_offset)
                        triangle_index_offset += ShortVector3.size()
                        face = [indices.x, indices.y, indices.z]

                        new_triangle = []
                        for index in face:
                            if index not in triangle_index_map:
                                triangle_index_map[index] = len(submesh.vertices)
                                submesh.vertices.append(mesh.vertices[index])
                            new_triangle.append(triangle_index_map[index])
                        submesh.triangles.append(new_triangle)
                
                elif group_header.read_mode == 4:
                    inverse = False
                    read_count = 0
                    while read_count < group_header.index_count - 2:
                        indices = ShortVector3.from_buffer_copy(data, triangle_index_offset)
                        triangle_index_offset += 6

                        if indices.x == indices.y or indices.y == indices.z or indices.x == indices.z:
                            triangle_index_offset -= 4
                            inverse = not inverse
                            skipped_indices.append(read_count)
                            read_count += 1
                            continue

                        indices_a = indices.x if not inverse else indices.y
                        indices_b = indices.y if not inverse else indices.x

                        face = [int(indices_a), int(indices_b), int(indices.z)]

                        new_triangle = []
                        for index in face:
                            if index not in triangle_index_map:
                                triangle_index_map[index] = len(submesh.vertices)
                                submesh.vertices.append(mesh.vertices[index])
                            new_triangle.append(triangle_index_map[index])
                        submesh.triangles.append(new_triangle)

                        triangle_index_offset -= 4
                        inverse = not inverse
                        read_count += 1

                # read uv_triangles
                texco_index_map = {}
                submesh.uv_triangles = []
                submesh.uv_vertices = []

                submesh.material_index = int.from_bytes(data[current_group_offset + 32 : current_group_offset + 36], byteorder='little') - 1

                uv_offset_shift = 36 if group_header.header_size > 32 else 20
                uv_offset = int.from_bytes(data[current_group_offset + uv_offset_shift : current_group_offset + uv_offset_shift + 4], byteorder='little')
                uv_triangle_index_offset = current_group_offset + int(uv_offset)
                curret_uv_triangle_offset = uv_triangle_index_offset
                if group_header.read_mode == 3:
                    for i in range(int(group_header.index_count / 3)):
                        indices = ShortVector3.from_buffer_copy(data, curret_uv_triangle_offset)
                        curret_uv_triangle_offset += ShortVector3.size()
                        face = [indices.x, indices.y, indices.z]

                        new_triangle = []
                        for index in face:
                            if index not in texco_index_map:
                                texco_index_map[index] = len(submesh.uv_vertices)
                                submesh.uv_vertices.append(mesh.uv_vertices[index])
                            new_triangle.append(texco_index_map[index])
                        submesh.uv_triangles.append(new_triangle)

                elif group_header.read_mode == 4:
                    inverse = False
                    read_count = 0
                    while read_count < group_header.index_count - 2:
                        indices = ShortVector3.from_buffer_copy(data, curret_uv_triangle_offset)
                        curret_uv_triangle_offset += ShortVector3.size()

                        if read_count in skipped_indices:
                            curret_uv_triangle_offset -= 4
                            inverse = not inverse
                            read_count += 1
                            continue

                        indices_a = indices.x if not inverse else indices.y
                        indices_b = indices.y if not inverse else indices.x

                        face = [int(indices_a), int(indices_b), int(indices.z)]

                        new_triangle = []
                        for index in face:
                            if index not in texco_index_map:
                                texco_index_map[index] = len(submesh.uv_vertices)
                                submesh.uv_vertices.append(mesh.uv_vertices[index])
                            new_triangle.append(texco_index_map[index])
                        submesh.uv_triangles.append(new_triangle)

                        curret_uv_triangle_offset -= 4
                        inverse = not inverse
                        read_count += 1

                current_group_offset += group_header.next_offset
                mesh.submeshes.append(submesh)

            model.meshes.append(mesh)
            current_mdt_offset += mdt_header.total_size

        file_name = os.path.splitext(os.path.basename(file_path))[0]
        root = bpy.data.objects.new(file_name, None)
        root.location = (0.0, 0.0, 0.0)
        bpy.context.collection.objects.link(root)

        created_materials = {}
        for mds_mesh in model.meshes:
            for submesh in mds_mesh.submeshes:
                mesh = bpy.data.meshes.new(name="submesh")
                mesh.from_pydata(submesh.vertices, [], submesh.triangles)
                mesh.update()

                mesh.uv_layers.new(name="UVMap")
                uv_layer = mesh.uv_layers.active.data
                for poly in mesh.polygons:
                    for loop_idx in poly.loop_indices:
                        uv_idx = submesh.uv_triangles[poly.index][poly.loop_indices.index(loop_idx)]
                        uv_layer[loop_idx].uv = submesh.uv_vertices[uv_idx]

                mesh.update()

                mesh_obj = bpy.data.objects.new("submesh", mesh)
                mesh_obj.location = (0.0, 0.0, 0.0)
                mesh_obj.parent = root

                if submesh.material_index < len(model.materials):
                    texture = model.materials[submesh.material_index][1]
                    if texture in created_materials:
                        material = created_materials[texture]
                    else:
                        material = bpy.data.materials.new(name=model.materials[submesh.material_index][1])
                        material.use_nodes = True
                        material.diffuse_color = (random.random(), random.random(), random.random(), 1)
                        created_materials[texture] = material

                    mesh_obj.data.materials.append(material)

                bpy.context.collection.objects.link(mesh_obj)
        
        root.rotation_euler[0] = math.radians(90)
