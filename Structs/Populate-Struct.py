import unreal
import os

STRUCT_PATH_ROOT = "/Game/GeneratedStructs"
STRUCT_NAME_TO_UPDATE = "MyExistingStruct"
MEMBER_DEFINITIONS_TO_ADD = [
    {"name": "NewString", "type": "FString"},
    {"name": "NewInteger", "type": "int32"}
]
MEMBERS_TO_REMOVE = ["OldBool"]

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

def update_existing_struct(struct_path_root, struct_name_to_update, members_to_add, members_to_remove):
    
    struct_editor_subsystem = unreal.get_editor_subsystem(unreal.StructEditorSubsystem)
    if not struct_editor_subsystem:
        unreal.log_error("Error: Struct Editor Subsystem not available.")
        return None

    full_asset_path = f"{struct_path_root}/{struct_name_to_update}"
    existing_struct = unreal.load_object(None, full_asset_path)
    if not existing_struct:
        unreal.log_error(f"Error: UStruct asset not found at '{full_asset_path}'.")
        return None
    if unreal.UStruct.is_blueprint_generated_class(existing_struct):
        unreal.log_warning(f"Warning: Skipping blueprint generated struct '{full_asset_path}'.")
        return existing_struct
    
    modified = False
    
    existing_member_names = {prop.get_fname(): prop for prop in unreal.EditorPropertyLibrary.get_struct_properties(existing_struct)}
    for member_name_to_remove in members_to_remove:
        name_to_remove = unreal.Name(member_name_to_remove)
        if name_to_remove in existing_member_names:
            struct_editor_subsystem.remove_property(existing_struct, name_to_remove)
            modified = True
            unreal.log(f"Removed member '{member_name_to_remove}' from '{struct_name_to_update}'.")
        else:
            unreal.log_warning(f"Warning: Member '{member_name_to_remove}' not found in '{struct_name_to_update}'.")
    
    for member_info in members_to_add:
        member_name = member_info["name"].strip()
        member_type_str = member_info["type"].strip().lower()
        name_to_add = unreal.Name(member_name)
        if name_to_add not in existing_member_names:
            property_type = DEFAULT_PROPERTY_TYPES.get(member_type_str)
            custom_struct_class = CUSTOM_PROPERTY_TYPES.get(member_type_str)
            if property_type:
                struct_editor_subsystem.add_property(existing_struct, name_to_add, property_type)
                modified = True
                unreal.log(f"Added member '{member_name}' of type '{member_type_str}' to '{struct_name_to_update}'.")
            elif custom_struct_class:
                found_class = unreal.find_class(custom_struct_class)
                if found_class:
                    struct_editor_subsystem.add_struct_property(existing_struct, name_to_add, found_class)
                    modified = True
                    unreal.log(f"Added member '{member_name}' of custom type '{member_type_str}' to '{struct_name_to_update}'.")
                else:
                    unreal.log_warning(f"Warning: Custom struct '{custom_struct_class}' not found for new member '{member_name}' in '{struct_name_to_update}'.")
            else:
                unreal.log_warning(f"Warning: Unsupported type '{member_type_str}' for new member '{member_name}' in '{struct_name_to_update}'.")
        else:
            unreal.log_warning(f"Warning: Member '{member_name}' already exists in '{struct_name_to_update}'.")
    if modified:
        unreal.EditorAssetLibrary.save_loaded_asset(existing_struct)
        unreal.log(f"Successfully updated UStruct asset at: {full_asset_path}.")
    else:
        unreal.log(f"UStruct asset at: {full_asset_path} was not modified.")
    return existing_struct

update_existing_struct(STRUCT_PATH_ROOT, STRUCT_NAME_TO_UPDATE, MEMBER_DEFINITIONS_TO_ADD, MEMBERS_TO_REMOVE)