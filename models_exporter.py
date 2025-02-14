import os
import json
import pandas as pd


def extract_block_data(json_file_path):
    """
    Extracts the texture paths, block name, and parent key value from a Minecraft block model JSON file.
    Each texture is placed in a separate column, and duplicate fields are avoided.
    """
    with open(json_file_path, 'r') as file:
        data = json.load(file)

    block_name = os.path.basename(json_file_path).replace('.json', '')
    parent_value = data.get('parent', 'N/A')

    # Extract texture paths
    textures = data.get('textures', {})
    texture_paths = set()  # Use a set to avoid duplicates

    for key, value in textures.items():
        if isinstance(value, str):
            texture_paths.add(value)
        elif isinstance(value, dict):
            for nested_value in value.values():
                if isinstance(nested_value, str):
                    texture_paths.add(nested_value)

    # Convert the set to a sorted list for consistent column ordering
    texture_paths = sorted(list(texture_paths))

    # Create a dictionary for the block data
    block_data = {
        'Block Name': block_name,
        'Parent': parent_value
    }

    # Add each texture path as a separate column
    for i, texture_path in enumerate(texture_paths, start=1):
        block_data[f'Texture {i}'] = texture_path

    return block_data


def create_excel_from_jsons(json_directory, output_excel_path):
    """
    Reads all JSON files in the specified directory, extracts data, and writes to an Excel sheet.
    """
    all_block_data = []
    all_texture_columns = set()  # Track all unique texture columns across blocks

    # Iterate over all JSON files in the directory
    for filename in os.listdir(json_directory):
        if filename.endswith('.json'):
            json_file_path = os.path.join(json_directory, filename)
            block_info = extract_block_data(json_file_path)
            all_block_data.append(block_info)

            # Update the set of all texture columns
            for key in block_info.keys():
                if key.startswith('Texture '):
                    all_texture_columns.add(key)

    # Ensure consistent columns for all blocks
    all_texture_columns = sorted(list(all_texture_columns))  # Sort for consistent ordering

    # Create a DataFrame from the extracted data
    df = pd.DataFrame(all_block_data)

    # Ensure all texture columns are present in the DataFrame
    for column in all_texture_columns:
        if column not in df.columns:
            df[column] = 'N/A'  # Fill missing texture columns with 'N/A'

    # Reorder columns: Block Name, Parent, then Texture 1, Texture 2, etc.
    columns_order = ['Block Name', 'Parent'] + all_texture_columns
    df = df[columns_order]

    # Write the DataFrame to an Excel file
    df.to_excel(output_excel_path, index=False)
    print(f"Excel file created successfully at {output_excel_path}")


# Example usage
json_directory = 'K:/Kir4h/Programming/Voxelized/minecraft/models/block'
output_excel_path = 'minecraft_textures.xlsx'
create_excel_from_jsons(json_directory, output_excel_path)