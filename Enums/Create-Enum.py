import unreal

ENUM_PATH_ROOT = ""
ENUM_NAME_TO_UPDATE = ""
OPTIONS_TO_ADD = []
OPTIONS_TO_REMOVE = []

def update_existing_enum(enum_path_root, enum_name_to_update, options_to_add, options_to_remove):
    full_asset_path = f"{enum_path_root}/{enum_name_to_update}"
    existing_enum = unreal.load_object(None, full_asset_path)
    if not existing_enum:
        unreal.log_error(f"Error: UEnum asset not found at '{full_asset_path}'.")
        return None
    existing_enums = existing_enum.get_enums()
    existing_enum_names = [name for name, _ in existing_enums]
    modified = False
    for option_to_remove in options_to_remove:
        name_to_remove = unreal.Name(option_to_remove)
        found = False
        updated_enums = []
        for name, value in existing_enums:
            if name == name_to_remove:
                found = True
                modified = True
                unreal.log(f"Removed option '{option_to_remove}' from '{enum_name_to_update}'.")
            else:
                updated_enums.append((name, value))
        existing_enums = updated_enums
        if not found:
            unreal.log_warning(f"Warning: Option '{option_to_remove}' not found in '{enum_name_to_update}'.")
    next_value = 0
    if existing_enums:
        next_value = max(value for _, value in existing_enums) + 1
    for option_to_add in options_to_add:
        name_to_add = unreal.Name(option_to_add)
        if name_to_add not in existing_enum_names:
            existing_enums.append((name_to_add, next_value))
            existing_enum_names.append(option_to_add)
            next_value += 1
            modified = True
            unreal.log(f"Added option '{option_to_add}' to '{enum_name_to_update}'.")
        else:
            unreal.log_warning(f"Warning: Option '{option_to_add}' already exists in '{enum_name_to_update}'.")
    if modified:
        existing_enum.set_enums(existing_enums)
        unreal.EditorAssetLibrary.save_loaded_asset(existing_enum)
        unreal.log(f"Successfully updated UEnum asset at: {full_asset_path}.")
    else:
        unreal.log(f"UEnum asset at: {full_asset_path} was not modified.")
    return existing_enum

update_existing_enum(ENUM_PATH_ROOT, ENUM_NAME_TO_UPDATE, OPTIONS_TO_ADD, OPTIONS_TO_REMOVE)