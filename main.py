# Merging two textures' image
def merge(img_modified, img_main, modified_side, main_side):
    from PIL import Image
    import numpy as np

    # Ensure both images are in 'P' mode (palettized)
    _chg = img_modified.convert('P')
    _main = img_main.convert('P')

    # Get the color palettes
    chg_palette = _chg.getpalette()
    main_palette = _main.getpalette()

    # Convert palettes to numpy arrays for easier manipulation
    chg_palette_array = np.array(chg_palette).reshape(-1, 3)
    main_palette_array = np.array(main_palette).reshape(-1, 3)

    # Convert images to numpy arrays
    chg_array = np.array(_chg)
    main_array = np.array(_main)

    # Checking the merging side of main texture
    # Get the color indices of the needed line
    if main_side == 'up':
        main_line_indices = main_array[0, :]
    elif main_side == 'down':
        main_line_indices = main_array[-1, :]
    elif main_side == 'left':
        main_line_indices = main_array[:, 0]
    elif main_side == 'right':
        main_line_indices = main_array[:, -1]
    else:
        raise ValueError("Main side: Not an actual side")

    # Checking the merging side of modified texture
    # Get the color indices of the needed line
    if modified_side == 'up':
        modified_line_indices = chg_array[0, :]
    elif modified_side == 'down':
        modified_line_indices = chg_array[-1, :]
    elif modified_side == 'left':
        modified_line_indices = chg_array[:, 0]
    elif modified_side == 'right':
        modified_line_indices = chg_array[:, -1]
    else:
        raise ValueError("Modified side: Not an actual side")

    # Map the indices to RGB values using the main image's palette
    main_bottom_line_colors = main_palette_array[main_line_indices]

    # Add missing colors to the chg image's palette
    new_palette = chg_palette_array.tolist()
    new_indices = []

    for color in main_bottom_line_colors:
        if list(color) not in new_palette:
            new_palette.append(list(color))
        new_indices.append(new_palette.index(list(color)))

    # Ensure the new palette does not exceed 256 colors
    if len(new_palette) > 256:
        raise ValueError("The combined palette exceeds 256 colors.")

    # Update the modified image's palette
    new_palette_flat = [item for sublist in new_palette for item in sublist]
    _chg.putpalette(new_palette_flat)

    # Copy the new indices to the top line of the chg image
    modified_line_indices[:] = new_indices

    # Create a new image with the modified pixel values
    img_modified = Image.fromarray(chg_array.astype(np.uint8), mode='P')
    img_modified.putpalette(new_palette_flat)

    return img_modified


def to_block_path(path):
    return str(path).replace('minecraft:block/', '') + '.png'

def main():
    from tkinter.filedialog import askdirectory

    # Open the file dialog to select a folder
    print('Select resource pack folder')
    input_folder = askdirectory()

    # Check if a folder was selected
    if not input_folder:
        raise Exception("No input folder selected.")
    else:
        print('Selected path: ' + input_folder)

    import os
    # import shutil - will be in the future, as well as shutil.copytree(source_folder, destination_folder)

    # Paths for block models and textures
    input_folder_textures = os.path.join(input_folder, 'assets/minecraft/textures/block')
    input_folder_models = os.path.join(input_folder, 'assets/minecraft/models/block')

    # Create folders to save the modified resource pack
    parent_directory = os.path.dirname(input_folder)
    output_folder = os.path.join(parent_directory, os.path.basename(input_folder) + '_voxelized')

    os.makedirs(output_folder, exist_ok=True)
    os.makedirs(os.path.join(output_folder, 'assets'), exist_ok=True)
    os.makedirs(os.path.join(output_folder, 'assets/minecraft'), exist_ok=True)
    os.makedirs(os.path.join(output_folder, 'assets/minecraft/textures'), exist_ok=True)

    output_folder_textures = os.path.join(output_folder, 'assets/minecraft/textures/block')
    os.makedirs(output_folder_textures, exist_ok=True)
    output_folder_models = os.path.join(output_folder, 'assets/minecraft/models')
    is_models_folder_created = False
    # os.makedirs(output_folder_models, exist_ok=True)    # Only if it requires to change one texture more than once

    import glob
    import json
    from PIL import Image

    # Get a list of block models
    block_models_path = os.path.join(input_folder_models, "*.json")
    block_models = glob.glob(block_models_path)

    block_count = 0
    for block_model in block_models:
        block_count += 1
        with open(block_model) as file:
            block_data = json.load(file)

        # If all the sides are different
        if block_data['parent'] == 'minecraft:block/cube':
            # Check texture for copying [NOT YET IMPLEMENTED]

            # Process a block
            block_textures = block_data['textures']
            up = to_block_path(block_textures['up'])
            north = to_block_path(block_textures['north'])
            west = to_block_path(block_textures['west'])
            east = to_block_path(block_textures['east'])
            south = to_block_path(block_textures['south'])
            down = to_block_path(block_textures['down'])

            up_img = Image.open(os.path.join(input_folder_textures, up))
            north_img = Image.open(os.path.join(input_folder_textures, north))
            west_img = Image.open(os.path.join(input_folder_textures, west))
            east_img = Image.open(os.path.join(input_folder_textures, east))
            south_img = Image.open(os.path.join(input_folder_textures, south))
            down_img = Image.open(os.path.join(input_folder_textures, down))

            # ###Merging: need to fix up with north and east && down with north and west
            # Top to sides
            north_img = merge(north_img, up_img, 'up', 'up')
            west_img = merge(west_img, up_img, 'up', 'left')
            east_img = merge(east_img, up_img, 'up', 'right')
            south_img = merge(south_img, up_img, 'up', 'down')

            # Sides between each other
            west_img = merge(west_img, north_img, 'left', 'right')
            east_img = merge(east_img, north_img, 'right', 'left')
            south_img = merge(south_img, west_img, 'left', 'right')
            south_img = merge(south_img, east_img, 'right', 'left')

            # Sides to bottom
            down_img = merge(down_img, north_img, 'down', 'down')
            down_img = merge(down_img, west_img, 'right', 'down')
            down_img = merge(down_img, east_img, 'left', 'down')
            down_img = merge(down_img, south_img, 'up', 'down')
            # ###

            north_img.save(os.path.join(output_folder_textures,
                                        str(os.path.basename(block_model)).replace('.json', '') + '_north.png'))
            west_img.save(os.path.join(output_folder_textures,
                                       str(os.path.basename(block_model)).replace('.json', '') + '_west.png'))
            east_img.save(os.path.join(output_folder_textures,
                                       str(os.path.basename(block_model)).replace('.json', '') + '_east.png'))
            south_img.save(os.path.join(output_folder_textures,
                                        str(os.path.basename(block_model)).replace('.json', '') + '_south.png'))
            down_img.save(os.path.join(output_folder_textures,
                                       str(os.path.basename(block_model)).replace('.json', '') + '_down.png'))

    print("Blocks found: " + str(block_count))

    """
    from PIL import Image
    import numpy as np
    
    # Opening images in folder
    # Should change file paths based on block json
    _chg = Image.open(os.path.join(folder_path, "crafting_table_front.png"))
    _main = Image.open(os.path.join(folder_path, "crafting_table_top.png"))

    img_modified = merge(_chg, _main, 'up')

    # Save the modified image in the output folder
    filename = os.path.basename("crafting_table_front.png")
    img_modified.save(os.path.join(output_folder, filename))
    """
    """
    # Get a list of image files in the selected folder
    import glob
    image_files = glob.glob(os.path.join(folder_path, "*.png"))

        for image_file in image_files:

            # Open the image and convert to np array
            image = Image.open(image_file)
            ...
            ...
            ...
            modified_image.save(os.path.join(output_folder, filename))

        print("Images have been successfully modified and saved in a separate folder.")
    """


if __name__ == '__main__':
    main()
