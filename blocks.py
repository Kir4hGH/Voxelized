import json
import os
# from abc import ABC, abstractmethod


# Not used
class Face:
    def __init__(self, texture, uv):
        self.texture = texture
        self.uv = uv


# Not used
class CubeElement:
    def __init__(self, coords_from, coords_to, faces):
        self._from = coords_from
        self._to = coords_to
        self.faces = faces


class Block:
    """Base class for all block types."""
    def __init__(self, block_model_path):
        self.name = os.path.basename(block_model_path).replace('.json', '')

        self.block_model_path = block_model_path
        with open(block_model_path) as file:
            self.block_data = json.load(file)
        self.textures = self.block_data.get('textures', {})
        self.block_type = self.block_data.get('parent')

    def print_sides(self):
        sides = ['up', 'down', 'north', 'south', 'east', 'west']
        for side in sides:
            texture_path = self.textures.get(side)
            if texture_path:
                print(f"  - Side '{side}': {texture_path}")
            else:
                print(f"  - Side '{side}': No texture found.")
        print(self.textures)
        print(self.block_type)
        print(self.block_data)


class BlockProcessor:
    """Factory class to create the appropriate block type."""
    @staticmethod
    def to_block(block_model_path):
        """Create a new block object based on the model."""

        if BlockProcessor.is_model_supported(block_model_path):
            return Block(block_model_path)
        return NotImplementedError

    @staticmethod
    def is_model_supported(block_model_path):
        with open(block_model_path) as file:
            block_data = json.load(file)

        parent = block_data.get('parent')

        return parent in ['minecraft:block/cube', 'minecraft:block/cube_all', 'minecraft:block/cube_column']


# Example usage
if __name__ == '__main__':
    # Paths to block JSON files
    cube_block_path = ('K:/Kir4h/Programming/Voxelized/test folder/'
                       "resourcepack/assets/minecraft/models/block/crafting_table.json")
    cube_all_block_path = 'path_to_cube_all_block.json'
    cube_column_block_path = 'path_to_cube_column_block.json'
    stairs_block_path = 'path_to_stairs_block.json'

    # Create and process blocks
    cube_block = BlockProcessor.to_block(cube_block_path)
    cube_block.print_sides()
