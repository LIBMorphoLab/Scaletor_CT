# HOW TO USE 'SCALETOR':
# ----------------------------------------------------------------------
# First, make sure that all necessary python-packages 
# are installed.

# Requirements:
# pip install Pillow numpy

# A guide on how to install packages can be found here:
# https://packaging.python.org/en/latest/tutorials/installing-packages/
 
# Insert the directory path of the input data set in the quotes behind the equal sign behind "path".

# Example input folder structure for batch processing:
# D:/example/
#   Dataset_1/
#       image001.tif
#       image002.tif
#       ...
#   Dataset_2/
#       image001.tif
#       image002.tif
#       ...
#
# Output will look like this:
# D:/example/Dataset_1/scaled/
# D:/example/Dataset_2/scaled/

# Make sure to use slashes instead of backslashes and 
# that there is a slash at the end of the directory path.
# Folders should not contain any other files except for
# the image files that are part of the data set.
#
# Additionally, you can give a value for "new_x". This value will be used as the number of
# pixel columns (x) for the downscaling of the data set.
# The number of pixel rows (y) will be determined based on
# that, maintaining the aspect ratio. A good default value 
# is 500.
#
# The workflow variable can be set to either 1 or 2 depending on the desired output file format and bit depth.
# 
# Run the script. Depending on the size of the data set the 
# process takes some seconds up to several minutes.
#
# A downscaled version of the data set should be found in a 
# folder called "scaled" inside the directory path put 
# in as the input.
# -----------------------------------------------------------

import os
import numpy as np
from PIL import Image

# --- USER SETTINGS ---
path = "" # Path to the input data
new_x = 500 # Number of pixel on x-axis
workflow = 2 # 1 resizes using LANCZOS and outputs to original filetype/bit depth. 2 resizes using LANCZOS and converts to 8-bit BMP
# ---------------------

path = os.path.normpath(path)

if not os.path.isdir(path):
    raise FileNotFoundError(f"Input directory not found: {path}")

# Image extensions to process
extensions = (".tif", ".tiff", ".png", ".bmp")

subfolders = [
    d for d in os.listdir(path)
    if os.path.isdir(os.path.join(path, d))
    and d.lower() != "scaled"
]

for subfolder in subfolders:
    subpath = os.path.join(path, subfolder)

    stack = sorted([
        os.path.join(subpath, filename)
        for filename in os.listdir(subpath)
        if os.path.isfile(os.path.join(subpath, filename))
        and filename.lower().endswith(extensions)
    ])

    if not stack:
        continue

    with Image.open(stack[0]) as ref_img:
        ref_size = ref_img.size

    new_y = round((ref_size[1] / ref_size[0]) * new_x)

    opath = os.path.join(subpath, "scaled")
    os.makedirs(opath, exist_ok=True)

    zlen = len(str(len(stack)))

    print(f"\nProcessing: {subfolder}")
    print(f"Original dimensions: {ref_size}")
    print(f"New dimensions: {new_x} x {new_y}")
    print(f"Images: {len(stack)}")

    for i, img_path in enumerate(stack):
        try:
            with Image.open(img_path) as img:
                # Capture original properties for workflow 1
                original_ext = os.path.splitext(img_path)[1]
                original_mode = img.mode
                
                raw = np.asarray(img)

                if raw.ndim != 2:
                    print(f"Skipping non-grayscale image: {os.path.basename(img_path)}")
                    continue

                # Convert to signed 32-bit integer mode for resizing to prevent clipping/noise
                img_i = Image.fromarray(raw.astype(np.int32), mode="I")

                resized = img_i.resize(
                    (new_x, new_y),
                    Image.Resampling.LANCZOS
                )

                resized_array = np.asarray(resized, dtype=np.float64)

                if workflow == 2:
                    # Percentile-based normalization for 8-bit BMP
                    p1, p99 = np.percentile(resized_array, [1, 99])

                    if p99 > p1:
                        clipped = np.clip(resized_array, p1, p99)
                        normalized = np.round((clipped - p1) / (p99 - p1) * 255).astype(np.uint8)
                    else:
                        normalized = np.zeros(resized_array.shape, dtype=np.uint8)

                    output = Image.fromarray(normalized, mode="L")
                    save_name = f"scaled_{str(i).zfill(zlen)}.bmp"
                    final_range = (normalized.min(), normalized.max())

                else:
                    # WORKFLOW 1: Maintain original type
                    # Clip to the range of the original data type to prevent Lanczos overshoot
                    dtype_min = np.iinfo(raw.dtype).min if np.issubdtype(raw.dtype, np.integer) else raw.min()
                    dtype_max = np.iinfo(raw.dtype).max if np.issubdtype(raw.dtype, np.integer) else raw.max()
                    
                    output_array = np.clip(np.rint(resized_array), dtype_min, dtype_max).astype(raw.dtype)
                    
                    # Use the original image mode (e.g., 'I;16', 'L', 'I')
                    output = Image.fromarray(output_array, mode=original_mode)
                    save_name = f"scaled_{str(i).zfill(zlen)}{original_ext}"
                    final_range = (output_array.min(), output_array.max())

                output_path = os.path.join(opath, save_name)
                output.save(output_path)

                if i == 0:
                    print(f"First image input mode: {original_mode}")
                    print(f"Input intensity range: {raw.min()} - {raw.max()}")
                    print(f"Resized intensity range: {final_range[0]} - {final_range[1]}")

                if (i + 1) % 25 == 0 or i + 1 == len(stack):
                    print(f"  Processed {i + 1}/{len(stack)} images")

        except Exception as e:
            print(f"ERROR processing {os.path.basename(img_path)}: {e}")

    with open(os.path.join(opath, "_Scaletor_log.txt"), "w", encoding="utf-8") as log:
        log.write(f"Dataset: {subpath}\n")
        log.write(f"Original dimensions: {ref_size[0]} x {ref_size[1]}\n")
        log.write(f"Output dimensions: {new_x} x {new_y}\n")
        log.write(f"Number of input images: {len(stack)}\n")
        log.write(f"Output option: {workflow}\n")

    print(f"Saved outputs to: {opath}")

print(f"\nProcessing complete. Output datasets saved in {path}")