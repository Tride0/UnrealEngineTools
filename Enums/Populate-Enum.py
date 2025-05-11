"""
    Still requires testing and feature adds
    Test if asset path exists
"""
import unreal

enum_asset_path = ""
enum_options = []

def populate_enum(enum_path, enum_options):
    enum_asset = unreal.load_object(None, enum_path)

    if not enum_asset:
        unreal.log_error(f"Could not find UEnum asset at path: {enum_path}")
        return

    current_enums = enum_asset.get_enums()
    current_enum_names = [name for name, _ in current_enums]

    new_enum_data = []
    for index, option_name in enumerate(enum_options):
        name = unreal.Name(option_name)
        if name not in current_enum_names:
            new_enum_data.append((name, index + len(current_enums)))

    if new_enum_data:
        enum_asset.set_enums(current_enums + new_enum_data)

        unreal.EditorAssetLibrary.save_loaded_asset(enum_asset)
        unreal.log(f"Successfully added options to {enum_path}: {enum_options}")
    else:
        unreal.log("No new options to add.")

populate_enum(enum_asset_path, enum_options)