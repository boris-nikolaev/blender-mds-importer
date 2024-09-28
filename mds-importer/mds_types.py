import ctypes

class MDSHeader(ctypes.LittleEndianStructure):
    _fields_ = [
        ("magic_code",          ctypes.c_int32),
        ("format_version",      ctypes.c_int32),
        ("header_size",         ctypes.c_int32),
        ("bone_count",          ctypes.c_int32),
        ("_padding_1",          ctypes.c_char * 4),
        ("bone_struct_size",    ctypes.c_int32),
        ("_padding_2",          ctypes.c_char * 8),
        ("object_count",        ctypes.c_int32),
        ("_padding_3",          ctypes.c_char * 8),
        ("unk_struct_count",    ctypes.c_int32),
        ("unk_struct_size",     ctypes.c_int32),
        ("_padding_4",          ctypes.c_char * 8),
        ("material_block_size", ctypes.c_int32),
        ("_padding_5",          ctypes.c_char * 16),
    ]

    @staticmethod
    def size():
        return ctypes.sizeof(MDSHeader)


class MDTHeader(ctypes.LittleEndianStructure):
    _fields_ = [
        ("magic_code",            ctypes.c_int32),
        ("_padding_1",            ctypes.c_int32),
        ("vertex_count_offset",   ctypes.c_int32),
        ("total_size",            ctypes.c_int32),     # 16
        ("_padding_2",            ctypes.c_char * 16), # 32
        ("mesh_scale_x",          ctypes.c_float),
        ("mesh_scale_y",          ctypes.c_float),
        ("mesh_scale_z",          ctypes.c_float),     # 44
        ("_padding_3",            ctypes.c_char * 36), # 80
        ("uv_scale_x",            ctypes.c_float),
        ("uv_scale_y",            ctypes.c_float),     # 88
        ("_padding_4",            ctypes.c_char * 24), # 112
        ("triangle_group_count",  ctypes.c_int32),     # 116
        ("vertex_attribute_size", ctypes.c_int32),     # 120
        ("_padding_5",            ctypes.c_char * 24), # 144
        ("vertex_count",          ctypes.c_int32),
        ("vertex_offset",         ctypes.c_int32),
        ("normals_count",         ctypes.c_int32),
        ("normals_offset",        ctypes.c_int32),
        ("uv_count",              ctypes.c_int32),
        ("uv_offset",             ctypes.c_int32),
        ("_padding_6",            ctypes.c_char * 120),
    ]

    @staticmethod
    def size():
        return ctypes.sizeof(MDTHeader)


class BoneNode(ctypes.LittleEndianStructure):
    _fields_ = [
        ("index",        ctypes.c_int32),
        ("header_size",  ctypes.c_int32),
        ("_padding_1",   ctypes.c_char * 12),
        ("parent_index", ctypes.c_int32),
        ("local_matrix", ctypes.c_float * 16),
        ("bind_pose",    ctypes.c_float * 16),
    ]

    @staticmethod
    def size():
        return ctypes.sizeof(BoneNode)


class TriangleGroupHeader(ctypes.LittleEndianStructure):
    _fields_ = [
        ("next_offset", ctypes.c_int16),
        ("_padding_1",  ctypes.c_char * 2),
        ("read_mode",   ctypes.c_int16),
        ("index_count", ctypes.c_int16),
        ("_padding_2",  ctypes.c_char * 8),
        ("header_size", ctypes.c_int16),
        ("_padding_3",  ctypes.c_char * 14),
    ]

    @staticmethod
    def size():
        return ctypes.sizeof(TriangleGroupHeader)


class ShortVector3(ctypes.LittleEndianStructure):
    _fields_ = [
        ("x", ctypes.c_int16),
        ("y", ctypes.c_int16),
        ("z", ctypes.c_int16),
    ]

    def multiply(self, x: float, y: float, z: float):
        result_x = self.x * x
        result_y = self.y * y
        result_z = self.z * z
        return [float(result_x), float(result_y), float(result_z)]

    @staticmethod
    def size():
        return ctypes.sizeof(ShortVector3)


class ByteVector2(ctypes.LittleEndianStructure):
    _fields_ = [
        ("x", ctypes.c_ubyte),
        ("y", ctypes.c_ubyte),
    ]

    @staticmethod
    def size():
        return ctypes.sizeof(ByteVector2)
