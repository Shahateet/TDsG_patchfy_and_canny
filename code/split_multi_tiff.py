#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  3 12:38:14 2024

@author: fernanka
"""
# %% i/o Import required libraries
import tifffile as tiff
import numpy as np
import glob
import rasterio
import multipagetiff as mtif
import os
from PIL import Image
from matplotlib import pyplot as plt

# %% i/o definition
image_path="/home/fernanka/Desktop/IGE-CryoDyn/IceDaM/Projects/Full_chain/Edge_detection/Output_images/"
image_name="patched_RGB_image.tif"
image_full_name="%s/%s" %(image_path,image_name)
folder_out="%s/splitted/" %(image_path)
image_set=tiff.imread(image_full_name)

# %% i/o String manipulation to get file name. It will be used to export the images
os.makedirs(folder_out,exist_ok=True) # create the output folder
file_name_with_extension = os.path.basename(image_full_name) # Extract the file name without the path
file_name = os.path.splitext(file_name_with_extension)[0] # Remove the extension to get just the file name
inc_out_file_name = "%s/%s_index_"%(folder_out,file_name) # create a almost ready output name. It is missing the ixj patch and the extension, which will be added on the saving procedure
multi_tiff_name = "%s/patched_%s" %(folder_out,file_name_with_extension) # name of the multi-tiff file

# %% Splitting
print("Proceeding to export the images")
# Iterate over the first two dimensions (patches)
for i in range(image_set.shape[0]):
    img = Image.fromarray(image_set[i]).convert("L")  # Convert each numpy array to a grayscale PIL Image
    name_out="%s_%i.tif" %(inc_out_file_name,i) # create output name
    img.save(name_out, format='TIFF', compression="tiff_deflate")  # Save the image as a TIFF
    print("%i exported out of %i" % (i+1,image_set.shape[0]))
