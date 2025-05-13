import unreal

def add_enum_entry(enum_path, new_entry_name):
    """Adds a new entry to the specified enum asset."""

    enum_asset = unreal.load_object(None, enum_path)
    if not enum_asset:
        unreal.log_error(f"Failed to load enum at path: {enum_path}")
        return

    enum_data = enum_asset.get_editor_property("values")
    new_entry_value = len(enum_data)
    new_entry = (new_entry_name, new_entry_value)

    # Check if the new entry already exists
    for key, value in enum_data:
        if key == new_entry_name:
            unreal.log_warning(f"Enum entry '{new_entry_name}' already exists.")
            return
    
    enum_data.append(new_entry)
    enum_asset.set_editor_property("values", enum_data)
    unreal.EditorAssetLibrary.save_loaded_asset(enum_asset)
    unreal.EditorAssetLibrary.refresh_content_browser()
    unreal.log(f"Added '{new_entry_name}' to enum '{enum_path}'")

# Example usage
enum_path = "/Game/MyFolder/MyEnum" # Replace with your enum's path
new_entry_name = "NewEnumValue"
add_enum_entry(enum_path, new_entry_name)
