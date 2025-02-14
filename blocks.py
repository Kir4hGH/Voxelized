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


class BlockFactory:
    """Factory class to create the appropriate block type."""
    @staticmethod
    def new_block(block_model_path: str) -> Block:
        """Create a new block object based on the model."""

        if BlockFactory.is_model_supported(block_model_path):
            return Block(block_model_path)
        return NotImplementedError

    @staticmethod
    def is_model_supported(block_model_path) -> bool:
        with open(block_model_path) as file:
            block_data = json.load(file)

        parent = block_data.get('parent')

        supported_block_types = BlockFactory.supported_block_types().keys()

        return parent in supported_block_types

    @staticmethod
    def supported_block_types() -> dict:
        return {
            'minecraft:block/cube': [
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
                ],
            'minecraft:block/cube_all': [
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
                ],
            'minecraft:block/cube_column': [
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
                ],
        }


if __name__ == '__main__':
    # Paths to block JSON files
    cube_block_path = ('K:/Kir4h/Programming/Voxelized/test folder/'
                       "resourcepack/assets/minecraft/models/block/crafting_table.json")

    # Create and process blocks
    cube_block = BlockFactory.new_block(cube_block_path)
    print(cube_block.textures)
