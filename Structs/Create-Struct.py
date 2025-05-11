import unreal

STRUCT_PATH = ""
STRUCT_NAME = ""
# View DEFAULT_PROPERTY_TYPES and CUSTOM_PROPERTY_TYPES for type
MEMBER_DEFINITIONS = [
    {"name": "ExampleString", "type": "FString"}
]

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

def create_single_struct(struct_path, struct_name, member_definitions):
    full_asset_path = f"{struct_path}/{struct_name}"

    struct_editor_subsystem = unreal.get_editor_subsystem(unreal.StructEditorSubsystem)
    if not struct_editor_subsystem:
        unreal.log_error("Error: Struct Editor Subsystem not available.")
        return None
    
    if not unreal.EditorAssetLibrary.does_directory_exist(struct_path):
        unreal.EditorAssetLibrary.make_directory(struct_path)
    if unreal.EditorAssetLibrary.does_asset_exist(full_asset_path):
        unreal.log_warning(f"UStruct asset already exists at: {full_asset_path}. Skipping creation.")
        return unreal.load_object(None, full_asset_path)
    
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

create_single_struct(STRUCT_PATH, STRUCT_NAME, MEMBER_DEFINITIONS)