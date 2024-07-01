#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 15 14:30:21 2024

@author: Kaian Shahateet
"""
# %% i/o Import required libraries
import numpy as np
import cv2 as cv
from matplotlib import pyplot as plt
import tifffile as tif
import sys
from PIL import Image
from datasets import Dataset
import rasterio
import os
import glob
from osgeo import gdal, osr

# %% i/o definition
image_path= sys.argv[1]
out_path= sys.argv[2]

multiplier= float(sys.argv[3]) # 1
subtractor= float(sys.argv[4]) # 0
bottom_threshold= float(sys.argv[5]) # 200
upper_threshold= float(sys.argv[6]) # 400

ind_image_paths=glob.glob("%s/*tif" %(image_path))

# %% Canny Edge detection
image_set=tif.imread(ind_image_paths) # read the multi tiff file
print("The maximum value of the raster is: %f" %(np.max(image_set)))
print("The minimum value of the raster is: %f" %(np.min(image_set)))
image_set_normalized_255=(image_set-np.min(image_set))/(np.max(image_set)-np.min(image_set))*255
image_set=image_set_normalized_255
    
    # Section to load the multiple tiff file into a list of pillow images
    # =============================================================================
    # image_set_pillow = [] # this variable will hold the pillow images
    # for i in range(16): # Loop to load the individual tiffs (from the multi tiff file) images into the variable
    #     img = Image.fromarray(image_set[i].astype(np.uint8), 'RGB') # load the individual tiffs into the variable img variable
    #     image_set_pillow.append(img) # create a list (builtin array) with those images
    # =============================================================================
edges_pillow=[] # It will be a list of pillow images
qual="n"
while (qual=="n"): # for the quality check
    for i in range(len(image_set)):
       img_gained = ((image_set[i] * multiplier)-subtractor).astype("uint8") # Applying some gain to the image   
       img=np.clip(((img_gained-np.min(img_gained))/(np.max(img_gained)-np.min(img_gained))*255),0,255).astype("uint8")
       print("The following value should be 0: %f" %(np.min(img)))
       print("The following value should be 255: %f" %(np.max(img)))
       assert img is not None, "file could not be read, check with os.path.exists()" # check the existence of the file
       edge = cv.Canny(img,threshold1=bottom_threshold, threshold2=upper_threshold, apertureSize=3,edges=False,L2gradient=True) # create edge images using canny
       pillow_edge=Image.fromarray(np.array(edge).astype(np.uint8)) # Convert to a Pillow Image to transform from RGB to grayscale
       edge_grayscale = pillow_edge.convert("L")  # Convert each image to grayscale
       # output name creation:
       base_name=os.path.basename(ind_image_paths[i]) # take the original name
       out_name="%s/%s" % (out_path,base_name) # concatenate with output_file
       # recovering geotiff information
       raster = gdal.Open(ind_image_paths[i])
       gt =raster.GetGeoTransform()
       crs=raster.GetProjection()
       left=gt[0] 
       pixelSizeX = gt[1]
       top=gt[3] 
       pixelSizeY = gt[5]
# =============================================================================
#        with rasterio.open(ind_image_paths[i]) as dataset: # load the tif file with rasterio
#            bounds = dataset.bounds # Get the bounding box of the image
#            left, bottom, right, top = bounds.left, bounds.bottom, bounds.right, bounds.top # The bounds contain the extent of the image in the form of (left, bottom, right, top)  
#        # saving as geotiff
# =============================================================================
       # first convert it back to np array
       edge_array=np.array(edge_grayscale)
       # width & height for any band
       no_of_bands = 1
       height = edge_array.shape[0]
       width = edge_array.shape[1]
       
       driver = gdal.GetDriverByName('GTiff') # load the GTiff driver from gdal
       out_ds = driver.Create(out_name, width, height, no_of_bands, gdal.GDT_Float32) # create the target dataset
       out_ds.SetProjection(raster.GetProjection())
       out_ds.SetGeoTransform((left, pixelSizeX, 0, top, 0, pixelSizeY)) # Update the GeoTransform of the dataset.    
# Write data array into dataset bands.
       band = out_ds.GetRasterBand(1)
       band.WriteArray(edge_array)
       band.FlushCache()
       
       # plotting routine
       # edge_grayscale.save(out_name, compression="tiff_deflate")
    # edges_grayscale[0].save(image_out, save_all=True, append_images=edges_grayscale[1:], compression="tiff_deflate")  # Save the images as a multi-page TIFF
    print(f"Grayscale TIFFs saved at {out_path}")
    
    qual=input("Are the results good enough? (y/n): ")     # Quality check
    
    if (qual=="n"):
        # gen_ind=input('"Do you want to change the general parameters or individual? (g/i): "')
        # if (gen_ind=="g"):
            multiplier=float(input("Define multiplier: "))
            subtractor=float(input("Define subtractor: "))
            bottom_threshold=float(input("Define bottom_threshold: "))
            upper_threshold=float(input("Define upper_threshold: "))
# =============================================================================
#        elif (gen_ind=="i"):
#             multiplier=input('"Define multiplier: "')
#             subtractor=input('"Define subtractor: "')
#             bottom_threshold=input('"Define bottom_threshold: "')
#             upper_threshold=input('"Define upper_threshold: "')
# =============================================================================

# =============================================================================
# # %% Plotting single images
# # plotting routine 
# plt.subplot(121),plt.imshow(img) 
# plt.title('Original Image'), plt.xticks([]), plt.yticks([])
# plt.subplot(122),plt.imshow(edges)
# plt.title('Edge Image'), plt.xticks([]), plt.yticks([])
# plt.show()
# plt.savefig(image_out, bbox_inches='tight',dpi=600) # save file
# =============================================================================



