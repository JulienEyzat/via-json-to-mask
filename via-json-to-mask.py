import os
from PIL import Image, ImageDraw
import json
import numpy as np
import argparse

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-j', "--json", required=True, help='input json file')
    parser.add_argument('-i', "--input", default="input", help='input images directory')
    parser.add_argument('-o', "--output", default="output", help='output masks directory')
    parser.add_argument('-s', "--image_sizes", default=None, help="dict with image sizes")
    args = parser.parse_args()

    return args.json, args.input, args.output, args.image_sizes	

def main(json_path, input_directory, output_directory, image_sizes):
    # Open JSON file
    with open(json_path) as f:
        via_json = json.load(f)
    images_json = via_json["_via_img_metadata"]

    # Extract regions from json
    regions_dict = {}
    for image_id in images_json:
        file_name = images_json[image_id]["filename"]
        regions_dict[file_name] = []

        for region in images_json[image_id]["regions"]:
            x = region["shape_attributes"]["all_points_x"]
            y = region["shape_attributes"]["all_points_y"]
            regions_dict[file_name].append(list(zip(x, y)))
    
    # Create masks
    for image_file_name in os.listdir(input_directory):
        image_path = os.path.join(input_directory, image_file_name)

        # Get original image size
        if image_sizes is None:
            with Image.open(image_path) as im:
                image_size = im.size
        else:
            image_size = image_sizes[image_path]

        # Create numpy array with same size
        mask_array = np.zeros((image_size[1], image_size[0]))
        mask = Image.fromarray(mask_array, "L")

        # Fill mask with region polygons
        draw = ImageDraw.Draw(mask)
        for region_polygon in regions_dict[image_file_name]:
            draw.polygon(region_polygon, fill=255)

        # Save the mask
        if not os.path.isdir(output_directory):
            os.mkdir(output_directory)
        output_mask_path = os.path.join(output_directory, image_file_name)
        mask.save(output_mask_path)

if __name__ == "__main__":
    json_path, input_directory, output_directory, image_sizes = get_args()
    main(json_path, input_directory, output_directory, image_sizes)