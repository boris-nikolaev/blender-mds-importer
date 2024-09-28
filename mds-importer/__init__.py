bl_info = {
    "name": "DQ8 MDS Importer",
    "author": "Boris Nikolaev",
    "version": (1, 0),
    "blender": (3, 6, 0),
    "location": "File > Import-Export",
    "description": "Import MDS Meshes and UV's from Dragon Quest 8",
    "warning": "",
    "doc_url": "",
    "category": "Import-Export",
}

import bpy
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty
from bpy.types import Operator
from . import mds_import

class ImportDQ8MDS(Operator, ImportHelper):
    bl_idname = "mds_format.import"
    bl_label = "Import MDS"

    filename_ext = ".mds"

    filter_glob: StringProperty(
        default="*.mds",
        options={'HIDDEN'},
        maxlen=255,
    )

    def execute(self, context):
        mds_import.import_model(self.filepath)
        return {'FINISHED'}


def menu_func_import(self, context):
    self.layout.operator(ImportDQ8MDS.bl_idname, text="Import DQ8 Mesh (.mds)")


def register():
    bpy.utils.register_class(ImportDQ8MDS)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)


def unregister():
    bpy.utils.unregister_class(ImportDQ8MDS)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)


if __name__ == "__main__":
    register()
