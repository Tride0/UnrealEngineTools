"""
still needs testing and features
"""

import unreal
import csv
import os

enum_asset_path_column = 'enum_asset_path'
enum_name_column = 'enum_name'
enum_options_column = 'enum_options'
enum_options_column_delimiter = '\n'

def create_enums_from_csv(csv_filepath):
    try:
        with open(csv_filepath, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            if not all(header in reader.fieldnames for header in [enum_asset_path_column, enum_name_column, enum_options_column]):
                unreal.log_error(f"Error: CSV file must contain columns: {enum_asset_path_column}, {enum_name_column}, {enum_options_column}.")
                return

            for row in reader:
                enum_asset_path = row[enum_asset_path_column].strip()
                enum_name = row[enum_name_column].strip()
                enum_options_str = row[enum_options_column].strip()
                enum_options = [option.strip() for option in enum_options_str.split(enum_options_column_delimiter)]

                full_asset_path = f"{enum_asset_path}/{enum_name}"

                if not unreal.EditorAssetLibrary.does_directory_exist(enum_asset_path):
                    unreal.EditorAssetLibrary.make_directory(enum_asset_path)
                    unreal.log(f"Created directory: {enum_asset_path}")

                if unreal.EditorAssetLibrary.does_asset_exist(full_asset_path):
                    unreal.log_warning(f"UEnum asset already exists at: {full_asset_path}. Skipping creation.")
                    continue

                if not enum_options:
                    unreal.log_warning(f"No enum options provided for '{enum_name}'. Skipping creation.")
                    continue

                new_enum = unreal.EditorAssetLibrary.create_asset(enum_name, enum_asset_path, unreal.UEnum)

                if new_enum:
                    enum_data = []
                    for index, option in enumerate(enum_options):
                        name = unreal.Name(option)
                        enum_data.append((name, index))

                    new_enum.set_enums(enum_data)
                    unreal.EditorAssetLibrary.save_loaded_asset(new_enum)
                    unreal.log(f"Successfully created UEnum asset at: {full_asset_path} with options: {enum_options}")
                else:
                    unreal.log_error(f"Failed to create UEnum asset at: {full_asset_path}.")

    except FileNotFoundError:
        unreal.log_error(f"Error: CSV file not found.")
    except Exception as e:
        unreal.log_error(f"An error occurred: {e}")

csv_file = "enums_to_create.csv"

with open(csv_file, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['enum_asset_path', 'enum_name', 'enum_options'])
    writer.writerow(['/Game/CharacterEnums', 'ECharacterClass', 'Warrior,Mage,Rogue,Healer'])
    writer.writerow(['/Game/Gameplay', 'EGameStates', 'MainMenu,Loading,Playing,Paused'])
    writer.writerow(['/Game/UI/Enums', 'EWidgetVisibility', 'Visible,Hidden,Collapsed'])

create_enums_from_csv(csv_file)