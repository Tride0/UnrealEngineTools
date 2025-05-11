import unreal
import os

ENUM_PATH_ROOT = "/Game/GeneratedEnums"
ENUM_NAME_FROM_FILE = True
STATIC_ENUM_NAME = "MyTextFileEnum"
OPTIONS_TO_ADD_KEYWORD = "#ADD"
OPTIONS_TO_REMOVE_KEYWORD = "#REMOVE"

def create_or_update_enum_from_text(file_path, enum_path_root, use_filename_as_name, static_name, add_keyword, remove_keyword):
    full_asset_path = ""
    enum_asset = None
    enum_name = ""
    if use_filename_as_name:
        enum_name_with_extension = os.path.basename(file_path)
        enum_name = os.path.splitext(enum_name_with_extension)[0]
    else:
        enum_name = static_name
    full_asset_path = f"{enum_path_root}/{enum_name}"
    if not unreal.EditorAssetLibrary.does_directory_exist(enum_path_root):
        unreal.EditorAssetLibrary.make_directory(enum_path_root)
    enum_asset = unreal.load_object(None, full_asset_path)
    options_to_add = []
    options_to_remove = []
    try:
        with open(file_path, 'r') as f:
            for line in f:
                stripped_line = line.strip()
                if stripped_line.startswith(add_keyword):
                    options_to_add.extend([opt.strip() for opt in stripped_line[len(add_keyword):].splitlines() if opt.strip()])
                elif stripped_line.startswith(remove_keyword):
                    options_to_remove.extend([opt.strip() for opt in stripped_line[len(remove_keyword):].splitlines() if opt.strip()])
                elif stripped_line and not stripped_line.startswith("#"):
                    options_to_add.append(stripped_line)
    except FileNotFoundError:
        unreal.log_error(f"Error: Text file not found at '{file_path}'.")
        return None
    if not enum_asset:
        if not options_to_add:
            unreal.log_warning(f"Warning: No options to add for new enum '{enum_name}'.")
            return None
        new_enum = unreal.EditorAssetLibrary.create_asset(enum_name, enum_path_root, unreal.UEnum)
        if new_enum:
            enum_data = [(unreal.Name(option), index) for index, option in enumerate(options_to_add)]
            new_enum.set_enums(enum_data)
            unreal.EditorAssetLibrary.save_loaded_asset(new_enum)
            unreal.log(f"Successfully created UEnum asset at: {full_asset_path} with {len(options_to_add)} options.")
            return new_enum
        else:
            unreal.log_error(f"Failed to create UEnum asset at: {full_asset_path}.")
            return None
    else:
        existing_enums = enum_asset.get_enums()
        existing_enum_names = [name for name, _ in existing_enums]
        modified = False
        for option_to_remove in options_to_remove:
            name_to_remove = unreal.Name(option_to_remove)
            updated_enums = [(name, value) for name, value in existing_enums if name != name_to_remove]
            if len(updated_enums) < len(existing_enums):
                existing_enums = updated_enums
                modified = True
                unreal.log(f"Removed option '{option_to_remove}' from '{enum_name}'.")
            elif option_to_remove not in existing_enum_names:
                unreal.log_warning(f"Warning: Option '{option_to_remove}' not found in '{enum_name}'.")
        next_value = 0
        if existing_enums:
            next_value = max((value for _, value in existing_enums), default=-1) + 1
        for option_to_add in options_to_add:
            name_to_add = unreal.Name(option_to_add)
            if name_to_add not in existing_enum_names:
                existing_enums.append((name_to_add, next_value))
                existing_enum_names.append(option_to_add)
                next_value += 1
                modified = True
                unreal.log(f"Added option '{option_to_add}' to '{enum_name}'.")
        if modified:
            enum_asset.set_enums(existing_enums)
            unreal.EditorAssetLibrary.save_loaded_asset(enum_asset)
            unreal.log(f"Successfully updated UEnum asset at: {full_asset_path}.")
        else:
            unreal.log(f"UEnum asset at: {full_asset_path} was not modified.")
        return enum_asset

TEXT_FILE_PATH = "my_enum_definition.txt"

create_or_update_enum_from_text(TEXT_FILE_PATH, ENUM_PATH_ROOT, ENUM_NAME_FROM_FILE, STATIC_ENUM_NAME, OPTIONS_TO_ADD_KEYWORD, OPTIONS_TO_REMOVE_KEYWORD)