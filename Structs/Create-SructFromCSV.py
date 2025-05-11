"""
Still needs testing and features
"""
import unreal
import csv

CSV_FILE_PATH = "struct_definitions.csv"
STRUCT_PATH_ROOT = "/Game/GeneratedStructs"
COLUMN_STRUCT_PATH = "struct_asset_path"
COLUMN_STRUCT_NAME = "struct_name"
COLUMN_MEMBER_NAME = "member_name"
COLUMN_MEMBER_TYPE = "member_type"

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

def create_or_edit_structs_from_csv(csv_filepath, struct_path_root):
    struct_definitions = {}
    try:
        with open(csv_filepath, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            required_headers = [COLUMN_STRUCT_PATH, COLUMN_STRUCT_NAME, COLUMN_MEMBER_NAME, COLUMN_MEMBER_TYPE]
            if not all(header in reader.fieldnames for header in required_headers):
                unreal.log_error(f"Error: CSV must contain columns: {', '.join(required_headers)}.")
                return
            for row in reader:
                struct_asset_path = row[COLUMN_STRUCT_PATH].strip()
                struct_name = row[COLUMN_STRUCT_NAME].strip()
                member_name = row[COLUMN_MEMBER_NAME].strip()
                member_type = row[COLUMN_MEMBER_TYPE].strip()
                if struct_name not in struct_definitions:
                    struct_definitions[struct_name] = {"path": struct_asset_path, "members": []}
                struct_definitions[struct_name]["members"].append({"name": member_name, "type": member_type})
    except FileNotFoundError:
        unreal.log_error(f"Error: CSV file not found at '{csv_filepath}'.")
        return
    except Exception as e:
        unreal.log_error(f"An error occurred: {e}")
        return

    struct_editor_subsystem = unreal.get_editor_subsystem(unreal.StructEditorSubsystem)
    
    if not struct_editor_subsystem:
        unreal.log_error("Error: Struct Editor Subsystem not available.")
        return
    for struct_name, definition in struct_definitions.items():
        asset_path = definition["path"].strip()
        members = definition["members"]
        full_asset_path = f"{asset_path}/{struct_name}"
        
        if not unreal.EditorAssetLibrary.does_directory_exist(asset_path):
            unreal.EditorAssetLibrary.make_directory(asset_path)
        
        existing_struct = unreal.load_object(None, full_asset_path)
        if existing_struct and unreal.UStruct.is_blueprint_generated_class(existing_struct):
            unreal.log_warning(f"Warning: Skipping blueprint generated struct '{full_asset_path}'.")
            continue
        if existing_struct:
            modified = False
            existing_member_names = {prop.get_fname(): prop for prop in unreal.EditorPropertyLibrary.get_struct_properties(existing_struct)}
            for member_info in members:
                member_name = member_info["name"].strip()
                member_type_str = member_info["type"].strip().lower()
                property_type = DEFAULT_PROPERTY_TYPES.get(member_type_str)
                custom_struct_class = CUSTOM_PROPERTY_TYPES.get(member_type_str)

                if member_name not in existing_member_names:
                    if property_type:
                        struct_editor_subsystem.add_property(existing_struct, unreal.Name(member_name), property_type)
                        modified = True
                    elif custom_struct_class:
                        found_class = unreal.find_class(custom_struct_class)
                        if found_class:
                            struct_editor_subsystem.add_struct_property(existing_struct, unreal.Name(member_name), found_class)
                            modified = True
                        else:
                            unreal.log_warning(f"Warning: Custom struct '{custom_struct_class}' not found for new member '{member_name}' in '{struct_name}'.")
                    else:
                        unreal.log_warning(f"Warning: Unsupported type '{member_type_str}' for new member '{member_name}' in '{struct_name}'.")
            if modified:
                unreal.EditorAssetLibrary.save_loaded_asset(existing_struct)
                unreal.log(f"Successfully edited UStruct asset at: {full_asset_path}.")
            else:
                unreal.log(f"UStruct asset at: {full_asset_path} is up to date.")
        else:
            new_struct = struct_editor_subsystem.create_new_struct_asset(asset_path, struct_name)
            if new_struct:
                for member_info in members:
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
                unreal.log(f"Successfully created UStruct asset at: {full_asset_path} with {len(members)} members.")
            else:
                unreal.log_error(f"Failed to create UStruct asset at: {full_asset_path}.")

create_or_edit_structs_from_csv(CSV_FILE_PATH, STRUCT_PATH_ROOT)