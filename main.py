import os
import glob
import numpy as np
from PIL import Image, ImageFile
from enum import Enum

from tkinter.filedialog import askdirectory
from blocks import BlockFactory


class ExportType(Enum):
    """
    Enum of export type

    values:
    DEPENDENT = writes only the textures which is needed to voxelize. Fully dependent from an old pack

    SEMI_DEPENDENT = writes all the textures of every voxelized element. Still dependent from an old pack

    INDEPENDENT = Default option. Writes a new pack with voxelized old pack's elements and rest of its content

    FULL = Writes every single minecraft element into new pack
    """
    DEPENDENT = "dependent"
    SEMI_DEPENDENT = "semi-dependent"
    INDEPENDENT = "independent"  # default
    FULL = "full"


class Voxelizer:
    """
    Class which makes resource pack voxelized.
    """
    def __init__(self, directory, export_type=ExportType.INDEPENDENT, voxel_size=1):
        """
        :param directory: path to resource pack
        :param export_type: how much the new pack will contain in itself
        :param voxel_size: determines scaling [not implemented]
        """
        # Validate the resource pack structure
        if not self.is_resourcepack_structure_valid(directory):
            self._is_process_allowed = self._ask_user_to_continue()
            if not self._is_process_allowed:
                return

        self._input_folder = directory

        # Determine whether to do a new resource pack with old pack as dependency or do a full texture export
        self.export_type = export_type

        # Paths for block models and textures
        self._input_folder_textures = os.path.join(self._input_folder, 'assets/minecraft/textures/block')
        self._input_folder_models = os.path.join(self._input_folder, 'assets/minecraft/models/block')

        # Prepare path to save the modified resource pack
        self._parent_directory = os.path.dirname(self._input_folder)
        self.output_folder = os.path.join(self._parent_directory,
                                          os.path.basename(self._input_folder) + '_voxelized')

        self._output_folder_textures = os.path.join(self.output_folder, 'assets/minecraft/textures/block')

        self._output_folder_models = os.path.join(self.output_folder, 'assets/minecraft/models')

        self._make_output_folders()

    def _make_output_folders(self):
        os.makedirs(self.output_folder, exist_ok=True)
        os.makedirs(os.path.join(self.output_folder, 'assets'), exist_ok=True)
        os.makedirs(os.path.join(self.output_folder, 'assets/minecraft'), exist_ok=True)
        os.makedirs(os.path.join(self.output_folder, 'assets/minecraft/textures'), exist_ok=True)
        os.makedirs(self._output_folder_textures, exist_ok=True)
        os.makedirs(self._output_folder_models,
                    exist_ok=True)  # Only if it requires to change one texture more than once

    @staticmethod
    def _merge(modified_img, main_img, modified_side, main_side, scale=1) -> ImageFile:
        """
        Merging two block sides' images
        :param modified_img: img which will be changed
        :param main_img: img from where colors will be taken
        :param modified_side: side of modified_img
        :param main_side: side of main_img
        :return: PIL.ImageFile
        """
        # Ensure both images are in 'P' mode (palettized)
        _chg = modified_img.convert('P')
        _main = main_img.convert('P')

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
            main_line_indices = main_array[-1, ::-1]
        elif main_side == 'left':
            main_line_indices = main_array[::-1, 0]
        elif main_side == 'right':
            main_line_indices = main_array[:, -1]
        else:
            raise ValueError("Main side: Not an actual side")

        # Checking the merging side of modified texture
        # Get the color indices of the needed line
        if modified_side == 'up':
            modified_line_indices = chg_array[0, ::-1]
        elif modified_side == 'down':
            modified_line_indices = chg_array[-1, :]
        elif modified_side == 'left':
            modified_line_indices = chg_array[:, 0]
        elif modified_side == 'right':
            modified_line_indices = chg_array[::-1, -1]
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
        modified_img = Image.fromarray(chg_array.astype(np.uint8), mode='P')
        modified_img.putpalette(new_palette_flat)

        return modified_img

    def voxelize_all(self):
        # Get a list of block models
        block_models_path_mask = os.path.join(self._input_folder_models, "*.json")
        block_model_files = glob.glob(block_models_path_mask)

        blocks_processed = 0
        blocks_found = 0
        for block_model_json in block_model_files:
            blocks_found += 1
            if BlockFactory.is_model_supported(block_model_json):
                blocks_processed += 1
                self.voxelize_block(block_model_json)
        print(f'Blocks processed: {blocks_processed}/{blocks_found}')

    def voxelize_block(self, block_model_json):
        block = BlockFactory.new_block(block_model_json)
        self._voxelize(block)

    def _voxelize(self, block):
        # Check texture for repeating (parent) [NOT YET IMPLEMENTED]
        # Process a block
        print("Voxelizing", block.name)

        block_textures = {side: Voxelizer.block_to_texture_path(path)
                          for side, path in block.textures.items() if side not in ['particle']}

        block_textures_img = {side: Image.open(os.path.join(self._input_folder_textures, path))
                              for side, path in block_textures.items()}

        # Define merge operations as (target_face, source_face, target_face_side, source_face_side)
        merge_operations = [
            # Top to sides
            ('north', 'up', 'up', 'up'),
            ('west', 'up', 'up', 'left'),
            ('east', 'up', 'up', 'right'),
            ('south', 'up', 'up', 'down'),

            # Sides between each other
            ('west', 'north', 'left', 'right'),
            ('east', 'north', 'right', 'left'),
            ('south', 'west', 'left', 'right'),
            ('south', 'east', 'right', 'left'),

            # Sides to bottom
            ('down', 'north', 'down', 'down'),
            ('down', 'west', 'left', 'down'),
            ('down', 'east', 'right', 'down'),
            ('down', 'south', 'up', 'down')
        ]

        # Apply merge operations
        for target_face, source_face, target_face_side, source_face_side in merge_operations:
            block_textures_img[target_face] = Voxelizer._merge(
                block_textures_img[target_face],
                block_textures_img[source_face],
                target_face_side,
                source_face_side
            )

        # Saving modified images
        for face, img in block_textures_img.items():
            if face not in ['north'] or self.export_type == 'full':
                img.save(os.path.join(self._output_folder_textures, str(block.name + f'_{face}.png')))

    @staticmethod
    def block_to_texture_path(path) -> str:
        """
        Converts a path to texture from json to file.

        :param path: path taken from model json
        :return: actual texture.png path
        """
        return str(path).replace('minecraft:block/', '') + '.png'

    @staticmethod
    def is_resourcepack_structure_valid(resource_pack_path):
        """
        Validate the structure of the resource pack.
        :param resource_pack_path: Path to the resource pack folder.
        :return: True if the structure is valid, False otherwise.
        """
        required_structure = [
            'assets/minecraft/models/block',
            'assets/minecraft/textures/block',
            'pack.mcmeta'
        ]

        missing_items = []
        for item in required_structure:
            item_path = os.path.join(resource_pack_path, item)
            if not os.path.exists(item_path):
                missing_items.append(item)

        if missing_items:
            print("Warning: The resource pack is missing the following required items:")
            for item in missing_items:
                print(f"  - {item}")
            return False
        return True

    @staticmethod
    def _ask_user_to_continue() -> bool:
        """
        Ask the user if they want to continue despite the missing items.
        :return: True if the user chooses to continue, False otherwise.
        """
        while True:
            user_input = input("Do you want to continue? (yes/no): ").strip().lower()
            if user_input in ['yes', 'y']:
                return True
            elif user_input in ['no', 'n']:
                return False
            else:
                print("Invalid input. Please enter 'yes' or 'no'.")


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
