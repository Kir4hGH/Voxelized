# Merging two textures' image
def merge(img_modified, img_main, main_side):

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

    # Get the color indices of the bottom line of the main image
    main_bottom_line_indices = main_array[-1, :]

    # Map the indices to RGB values using the main image's palette
    main_bottom_line_colors = main_palette_array[main_bottom_line_indices]

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
    chg_array[0, :] = new_indices

    # Create a new image with the modified pixel values
    img_modified = Image.fromarray(chg_array.astype(np.uint8), mode='P')
    img_modified.putpalette(new_palette_flat)

    return img_modified


def main():
    from tkinter.filedialog import askdirectory

    # Open the file dialog to select a folder
    folder_path = askdirectory()

    # Check if a folder was selected
    if folder_path:

        # Create a folder to save the modified images
        import os
        output_folder = os.path.join(folder_path, "modified_images")
        os.makedirs(output_folder, exist_ok=True)

        from PIL import Image
        import numpy as np

        # Opening images in folder
        # Should change file paths based on block json
        _chg = Image.open(os.path.join(folder_path, "crafting_table_front.png"))
        _main = Image.open(os.path.join(folder_path, "crafting_table_top.png"))

        img_modified = merge(_chg, _main, 'top')

        # Save the modified image in the output folder
        filename = os.path.basename("crafting_table_front.png")
        img_modified.save(os.path.join(output_folder, filename))

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
    else:
        print("No folder selected.")


if __name__ == '__main__':
    main()
