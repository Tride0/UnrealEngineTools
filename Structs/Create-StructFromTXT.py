import unreal
import os

STRUCT_PATH = "/Game/GeneratedStructs"
STRUCT_NAME_FROM_FILE = True
STATIC_STRUCT_NAME = "MyTextFileStruct"
MEMBER_DELIMITER = ":"
TYPE_DELIMITER = "|"

CUSTOM_PROPERTY_TYPES = {
    "vector": "Vector",
    "rotator": "Rotator"
}

DEFAULT_PROPERTY_TYPES = {
    "fstring": unreal.TextProperty,
    "int32": unreal.IntProperty,
    "bool": unreal.BoolProperty,
    "float": unreal.FloatProperty,
    "name": unreal.NameProperty,
    "byte": unreal.ByteProperty
}

def create_struct_from_text(file_path, struct_path, use_filename_as_name, static_name, member_delimiter, type_delimiter):
    struct_editor_subsystem = unreal.get_editor_subsystem(unreal.StructEditorSubsystem)
    if not struct_editor_subsystem:
        unreal.log_error("Error: Struct Editor Subsystem not available.")
        return None
    try:
        with open(file_path, 'r') as f:
            lines = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        unreal.log_error(f"Error: Text file not found at '{file_path}'.")
        return None
    
    member_definitions = []
    for line in lines:
        parts = line.split(member_delimiter)
        if len(parts) == 2:
            member_name = parts[0].strip()
            type_part = parts[1].strip().split(type_delimiter)
            member_type = type_part[0].strip()
            member_definitions.append({"name": member_name, "type": member_type})
        else:
            unreal.log_warning(f"Warning: Invalid line format in '{file_path}': '{line}'. Expected 'memberName{member_delimiter}memberType'.")
    if use_filename_as_name:
        struct_name_with_extension = os.path.basename(file_path)
        struct_name = os.path.splitext(struct_name_with_extension)[0]
    else:
        struct_name = static_name
    
    full_asset_path = f"{struct_path}/{struct_name}"
    if not unreal.EditorAssetLibrary.does_directory_exist(struct_path):
        unreal.EditorAssetLibrary.make_directory(struct_path)
    if unreal.EditorAssetLibrary.does_asset_exist(full_asset_path):
        unreal.log_warning(f"UStruct asset already exists at: {full_asset_path}. Skipping creation.")
        return unreal.load_object(None, full_asset_path)
    if not member_definitions:
        unreal.log_warning(f"Warning: No valid member definitions found in '{file_path}'.")
        return None
    
    new_struct = struct_editor_subsystem.create_new_struct_asset(struct_path, struct_name)
    if new_struct:
        for member_info in member_definitions:
            member_name = member_info["name"].strip()
            member_type_str = member_info["type"].strip().lower()
            property_type = DEFAULT_PROPERTY_TYPES.get(member_type_str)
            custom_struct_class = CUSTOM_PROPERTY_TYPES.get(member_type_str)
            if property_type:
                struct_editor_subsystem.add_property(new_struct, unreal.Name(member_name), property_type)
            elif custom_struct_class:
                found_class = unreal.find_class(custom_struct_class)
                if found_class:
                    struct_editor_subsystem.add_struct_property(new_struct, unreal.Name(member_name), found_class)
                else:
                    unreal.log_warning(f"Warning: Custom struct '{custom_struct_class}' not found for member '{member_name}' in '{struct_name}'.")
            else:
                unreal.log_warning(f"Warning: Unsupported type '{member_type_str}' for member '{member_name}' in '{struct_name}'.")
        unreal.EditorAssetLibrary.save_loaded_asset(new_struct)
        unreal.log(f"Successfully created UStruct asset at: {full_asset_path} with {len(member_definitions)} members.")
        return new_struct
    else:
        unreal.log_error(f"Failed to create UStruct asset at: {full_asset_path}.")
        return None

TEXT_FILE_PATH = "my_struct_definition.txt"

create_struct_from_text(TEXT_FILE_PATH, STRUCT_PATH, STRUCT_NAME_FROM_FILE, STATIC_STRUCT_NAME, MEMBER_DELIMITER, TYPE_DELIMITER)