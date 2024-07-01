#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 15 14:30:21 2024

#Maybe there is a problem with x and y. Make sure that n_patches_x and n_patches_y matches in all lines

@author: Kaian Shahateet
"""
# %% i/o Import required libraries
import numpy as np
import cv2 as cv
from matplotlib import pyplot as plt
import tifffile as tif
import sys
import os
from patchify import patchify
from PIL import Image
import rasterio
from osgeo import gdal, osr
from rasterio.enums import Resampling

# %% i/o definition
image_path= sys.argv[1] # /home/fernanka/Desktop/IGE-CryoDyn/IceDaM/Projects/Full_chain/Edge_detection/Input_image/RGB_image.tif"
folder_out= sys.argv[2] # "/home/fernanka/Desktop/IGE-CryoDyn/IceDaM/Projects/Full_chain/Edge_detection/Temp_patchified_images/"

# %% i/o definition trouble-shooting
image_path= "/home/fernanka/Desktop/IGE-CryoDyn/IceDaM/Projects/Full_chain/Edge_detection/Input_image/RGB_image.tif"
folder_out= "/home/fernanka/Desktop/IGE-CryoDyn/IceDaM/Projects/Full_chain/Edge_detection/Temp_patchified_images/"

# %% i/o String manipulation to get file name. It will be used to export the images
file_name_with_extension = os.path.basename(image_path) # Extract the file name without the path
file_name = os.path.splitext(file_name_with_extension)[0] # Remove the extension to get just the file name
inc_out_file_name = "%s/%s_index_"%(folder_out,file_name) # create a almost ready output name. It is missing the ixj patch and the extension, which will be added on the saving procedure
multi_tiff_name = "%s/patched_%s" %(folder_out,file_name_with_extension) # name of the multi-tiff file

# %% Parameters definition
patchsize_x= int(sys.argv[3]) # 2048 
patchsize_y= int(sys.argv[4]) # 2048
stepsize= int(sys.argv[5]) # 2048
stepsize= 2048
patchsize_x= 2048 
patchsize_y= 2048


new_size=(8192,8192)

n_patches_x=int(new_size[0]/patchsize_x)
n_patches_y=int(new_size[1]/patchsize_y)
 
# %% Convert input
# large_image = tif.imread(image_path) # load tifffile
# Resampling using rasterio
with rasterio.open(image_path) as dataset: # load the tif file with rasterio
    bounds = dataset.bounds # Get the bounding box of the image
    left, bottom, right, top = bounds.left, bounds.bottom, bounds.right, bounds.top # The bounds contain the extent of the image in the form of (left, bottom, right, top)
    crs = dataset.crs # Get the coordinate reference system (CRS)
    data = dataset.read(     # resample data to target shape
        out_shape=(
            dataset.count,
            int(new_size[0]),
            int(new_size[1])
        ),
        resampling=Resampling.bilinear
    )
    transform = dataset.transform * dataset.transform.scale( # scale image transform
        (dataset.width / data.shape[-1]),
        (dataset.height / data.shape[-2])
    )
    pixel_x = transform[0] # Extract pixel size (resolution)
    pixel_y = -transform[4]  # Pixel sizes can be negative, hence the negative sign)
    
large_image=np.transpose(data,(1,2,0)) # transpose variable. The rest of the code expects the channels to be the last dimension
print(f"Bounds: {bounds}")
print(f"Pixel size (resolution): X = {pixel_x}, Y = {pixel_y}")
print(f"CRS: {crs}")

# %% Core of patchify

# Initialize a list to hold patches for all bands
all_img_patches = np.zeros([n_patches_x,n_patches_y,patchsize_x,patchsize_y,3])
sing_patch_bbox=np.zeros((n_patches_y,n_patches_x,4)) # the last dimension are the left, bottom, right, and top margins
# Create patches for each band and collect them in the list
for i in range(large_image.shape[2]): # iterate through the RGB bands
    patches_img = patchify(large_image[:,:,i], (patchsize_x, patchsize_y), step=stepsize)  # create new patches of this image #Step=256 for 256 patches means no overlap
    for j in range(patches_img.shape[0]): # iterate through the individual patches with next line
        for k in range(patches_img.shape[1]):
            single_patch_img = patches_img[j, k, :, :]  # correct the indices
            #single_patch_img = (single_patch_img / 255.).astype(np.uint8)  # transform it
            all_img_patches[j,k,:,:,i]=single_patch_img  # stack patches
            # getting the bbox of each patch
            sing_patch_bbox[j,k,0], sing_patch_bbox[j,k,1], sing_patch_bbox[j,k,2], sing_patch_bbox[j,k,3] = (left+((pixel_x*(patchsize_x))*k)), (top-((pixel_y*patchsize_y)*(j+1))), (left+((pixel_x*patchsize_x)*(k+1))), (top-((pixel_y*patchsize_y)*(j)))
# Verify the shape of the combined patches array
print("Number of patches in x and y; pixels in x and y; and bands:") 
print(all_img_patches.shape)  # Expected output shape: (number_of_patches_x, number_of_patches_y, patchsize_x, patchsize_y, number_of_bands)

# %% Functions to save geotiff
for j in range(patches_img.shape[0]): # iterate through the individual patches with next line
    for k in range(patches_img.shape[1]):
        no_of_bands = all_img_patches[i,j].shape[2] # number of bands
        height = all_img_patches[i,j].shape[1]
        width = all_img_patches[i,j].shape[0]
        x1 = sing_patch_bbox[i,j,0]
        y1 = sing_patch_bbox[i,j,3]
        x2 = sing_patch_bbox[i,j,2]
        y2 = sing_patch_bbox[i,j,1]
        x_res = (x1 - x2)/width
        y_res = (y1 - y2)/width
        print(no_of_bands, x1, y1, x2, y2, x_res, y_res, width, height)

# %% Getting only figures with non-zero information
non_zero_slices = np.any(all_img_patches != 0, axis=(2, 3, 4)) # what are the patches (e.g. total number of 32x32) with information? 
all_img_patches_non_zero=all_img_patches[non_zero_slices,:,:,:] # Get this patches into the variable

# %% Back into RGB pillow tiff file
images_32x32 = [] # Create a list to hold the 32x32 images
# Iterate over the first two dimensions (patches)
for i in range(n_patches_y):
    row_images = [] # this variable will hold 32 pillow images to be appended into the 32x32
    for j in range(n_patches_x):
        # Extract the 256x256x3 slice
        img_array_all = all_img_patches[i, j] # single RGB patch
        patched_pil_RGB_single=Image.fromarray(np.array(img_array_all).astype(np.uint8),"RGB") # Convert to a Pillow Image
        row_images.append(patched_pil_RGB_single) # Append to the row list
    images_32x32.append(row_images) # Append the row to the main list. It is a list that contains a list of images. It is native list, not a numpy list. To access individual images, do images_32x32[i][j]

print("All patches saved into the python variable")
# %% Saving patched images
all_images = [img for row in images_32x32 for img in row] # images_32x32 is essentially row of images inside a row 
all_images[0].save(multi_tiff_name, save_all=True, append_images=all_images[1:], compression="tiff_deflate") # Save the images as a multi-page TIFF
print(f"Multi-page TIFF saved at {multi_tiff_name}")

# following is the old procedure to export each image into a file
# To enable that, just uncomment
# =============================================================================
# print("Proceeding to export the images")
# # Iterate over the first two dimensions (patches)
# for i in range(n_patches_x):
#     for j in range(n_patches_y):
#         img=images_32x32[i][j]
#         name_out="%s%ix%i.tif" %(inc_out_file_name,i,j)
#         t=tif.imread(img) 
#         
#         # Plot and save the image
#         plt.figure()
#         plt.imshow(img)
#         plt.xticks([])
#         plt.yticks([])
#         plt.savefig(name_out, bbox_inches='tight', dpi=300)
#         plt.close()  # Close the figure to avoid memory issues
#         print("%ix%i exported" % (i, j))
#         
#         all_images[0].save(multi_tiff_path, save_all=True, append_images=images_32x32[1:], compression="tiff_deflate")
# =============================================================================

# %% Plotting
# =============================================================================
# # Create a new figure with a single axes
# fig, axes = plt.subplots(figsize=(10, 10))
# axes.imshow(images_32x32[9][3])
# # Set title and labels
# axes.set_title("Single patch")
# # Show the plot
# plt.show()
# =============================================================================

