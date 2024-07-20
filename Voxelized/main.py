def main():
    from tkinter.filedialog import askdirectory
    from PIL import Image
    import numpy as np

    # Open the file dialog to select a folder
    folder_path = askdirectory()

    # Check if a folder was selected
    if folder_path:
        pass

    # Create a folder to save the modified images
    import os
    output_folder = os.path.join(folder_path, "modified_images")
    os.makedirs(output_folder, exist_ok=True)

    front = Image.open(os.path.join(folder_path, "crafting_table_side.png"))
    top = Image.open(os.path.join(folder_path, "crafting_table_top.png"))

    # Ensure both images are in 'P' mode (palettized)
    front = front.convert('P')
    top = top.convert('P')

    # Get the color palettes
    front_palette = front.getpalette()
    top_palette = top.getpalette()

    # Convert palettes to numpy arrays for easier manipulation
    front_palette_array = np.array(front_palette).reshape(-1, 3)
    top_palette_array = np.array(top_palette).reshape(-1, 3)

    # Convert images to numpy arrays
    front_array = np.array(front)
    top_array = np.array(top)

    # Get the color indices of the bottom line of the top image
    top_bottom_line_indices = top_array[-1, :]

    # Map the indices to RGB values using the top image's palette
    top_bottom_line_colors = top_palette_array[top_bottom_line_indices]

    # Add missing colors to the front image's palette
    new_palette = front_palette_array.tolist()
    new_indices = []

    for color in top_bottom_line_colors:
        if list(color) not in new_palette:
            new_palette.append(list(color))
        new_indices.append(new_palette.index(list(color)))

    # Ensure the new palette does not exceed 256 colors
    if len(new_palette) > 256:
        raise ValueError("The combined palette exceeds 256 colors.")

    # Update the front image's palette
    new_palette_flat = [item for sublist in new_palette for item in sublist]
    front.putpalette(new_palette_flat)

    # Copy the new indices to the top line of the front image
    front_array[0, :] = new_indices

    # Create a new image with the modified pixel values
    modified_front = Image.fromarray(front_array.astype(np.uint8), mode='P')
    modified_front.putpalette(new_palette_flat)

    # Save the modified image in the output folder
    filename = os.path.basename("crafting_table_side.png")
    modified_front.save(os.path.join(output_folder, filename))

    """
    # Get a list of image files in the selected folder
    import glob
    image_files = glob.glob(os.path.join(folder_path, "*.png"))
    
        for image_file in image_files:
            
            # Open the image and convert to np array
            image = Image.open(image_file)
            image_array = np.array(image)

            # Get the color palette
            palette = image.getpalette()

            # Create a color lookup table
            lookup_table = np.array(palette).reshape(-1, 3)

            # Map the values of the image to RGB triples using the lookup table
            rgb_image = lookup_table[image_array]

            # Modify half of the image
            #image_array[:, :image.width // 2, 0] = 0

            # Convert the modified array back to an image
            modified_image = Image.fromarray(rgb_image.astype(np.uint8))

            # Save the modified image in the output folder
            filename = os.path.basename(image_file)
            modified_image.save(os.path.join(output_folder, filename))

        print("Images have been successfully modified and saved in a separate folder.")
    else:
        print("No folder selected.")
    """

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
