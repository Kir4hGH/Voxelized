import os
import glob

import numpy as np
from PIL import Image, ImageFile
from tkinter.filedialog import askdirectory

from blocks import BlockProcessor


class Voxelizer:
    """
    Class which makes block voxelized
    """
    def __init__(self, directory, full_export='full'):
        self.input_folder = directory

        # Paths for block models and textures
        self.input_folder_textures = os.path.join(self.input_folder, 'assets/minecraft/textures/block')
        self.input_folder_models = os.path.join(self.input_folder, 'assets/minecraft/models/block')

        # Prepare path to save the modified resource pack
        self.parent_directory = os.path.dirname(self.input_folder)
        self.output_folder = os.path.join(self.parent_directory,
                                          os.path.basename(self.input_folder) + '_voxelized')

        self.output_folder_textures = os.path.join(self.output_folder, 'assets/minecraft/textures/block')

        # Variables

        # Figure out when needed
        self.is_models_folder_created = True
        if self.is_models_folder_created:
            self.output_folder_models = os.path.join(self.output_folder, 'assets/minecraft/models')

        # Determine whether to do a new resource pack with old pack as dependency or do a full texture export
        self.full_export = full_export

        self.make_output_folders()

    def make_output_folders(self):
        os.makedirs(self.output_folder, exist_ok=True)
        os.makedirs(os.path.join(self.output_folder, 'assets'), exist_ok=True)
        os.makedirs(os.path.join(self.output_folder, 'assets/minecraft'), exist_ok=True)
        os.makedirs(os.path.join(self.output_folder, 'assets/minecraft/textures'), exist_ok=True)
        os.makedirs(self.output_folder_textures, exist_ok=True)
        if self.is_models_folder_created:
            os.makedirs(self.output_folder_models,
                        exist_ok=True)  # Only if it requires to change one texture more than once

    @staticmethod
    def _merge(img_modified, img_main, modified_side, main_side) -> ImageFile:
        """
        Merging two block sides' images
        :param img_modified:
        :param img_main:
        :param modified_side:
        :param main_side:
        :return: Pillow's ImageFile. Hope this doesn't break anything
        """
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

    def voxelize_all(self):
        # Get a list of block models
        block_models_path_mask = os.path.join(self.input_folder_models, "*.json")
        block_model_files = glob.glob(block_models_path_mask)

        block_count = 0
        for block_model_json in block_model_files:

            if BlockProcessor.is_model_supported(block_model_json):
                block_count += 1  # Only if the block will be voxelized
                self.voxelize_block(block_model_json)
        print("Blocks found: " + str(block_count))

    def voxelize_block(self, block_model_json):
        block = BlockProcessor.to_block(block_model_json)
        self._voxelize(block)

    def _voxelize(self, block):
        # Check texture for repeating (parent) [NOT YET IMPLEMENTED]
        # Process a block
        print("Voxelizing", block.name)

        block_textures = {side: Voxelizer.block_to_texture_path(path)
                          for side, path in block.textures.items() if side not in ['particle']}

        block_textures_img = {side: Image.open(os.path.join(self.input_folder_textures, path))
                              for side, path in block_textures.items()}

        # Define merge operations as (target_side, source_side, modified_side, main_side)
        merge_operations = [
            # Top to sides
            ('north', 'up', 'up', 'up'),  # broken
            ('west', 'up', 'up', 'left'),
            ('east', 'up', 'up', 'right'),  # broken
            ('south', 'up', 'up', 'down'),

            # Sides between each other
            ('west', 'north', 'left', 'right'),
            ('east', 'north', 'right', 'left'),
            ('south', 'west', 'left', 'right'),
            ('south', 'east', 'right', 'left'),

            # Sides to bottom
            ('down', 'north', 'down', 'down'),  # broken
            ('down', 'west', 'right', 'down'),  # broken
            ('down', 'east', 'left', 'down'),
            ('down', 'south', 'up', 'down')
        ]

        # Apply merge operations
        for target_side, source_side, modified_side, main_side in merge_operations:
            block_textures_img[target_side] = Voxelizer._merge(
                block_textures_img[target_side],
                block_textures_img[source_side],
                modified_side,
                main_side
            )

        # Saving modified images
        for face, img in block_textures_img.items():
            if face not in ['north'] or self.full_export == 'full':
                img.save(os.path.join(self.output_folder_textures, str(block.name + f'_{face}.png')))

    @staticmethod
    def block_to_texture_path(path) -> str:
        """
        Converts a path to texture from json to file.

        :param path: path taken from model json
        :return: actual texture.png path
        """
        return str(path).replace('minecraft:block/', '') + '.png'


def main():
    # Open the file dialog to select a folder
    print('Select resource pack folder')
    input_folder = askdirectory()

    # Check if a folder was selected
    if not input_folder:
        raise Exception("No input folder selected.")
    else:
        print('Selected path: ' + input_folder)

    voxelizer = Voxelizer(input_folder)
    voxelizer.voxelize_all()

    # import shutil - will be in the future, as well as shutil.copytree(source_folder, destination_folder)


if __name__ == '__main__':
    main()
