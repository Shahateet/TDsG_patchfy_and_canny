#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun  6 12:43:59 2024

@author: fernanka
"""

import rasterio
import glob
import sys
import os
from osgeo import gdal, osr, ogr
import numpy as np
from rasterio.features import shapes
from rasterio.features import geometry_mask
from shapely.geometry import shape, mapping
import geopandas as gpd
import shutil

# %%
image_path= sys.argv[1]
out_path="%s/buffered" % (image_path)
buf_dist= int(sys.argv[2])

ind_image_paths=glob.glob("%s/*tif" %(image_path)) # list all tif files

for i in range(len(ind_image_paths)):

    or_mask=rasterio.open(ind_image_paths[i])# open the tif file
    
    # String manipulation for the output name
    base_name=os.path.basename(ind_image_paths[i]) # take the original name
    base_name_split = os.path.splitext(base_name)[0] # Change the extension to .shp
    base_name_shp = f"{base_name_split}.shp" 
    base_name_shp_full_path="%s/%s" % (out_path,base_name_shp) # concatenate with output_file
    base_name_tif_full_path="%s/%s" % (out_path,base_name) # concatenate with output_file
    
    # Check if the directory exists and create it if it doesn't
    if not os.path.exists(out_path):
        os.makedirs(out_path)
    
    # %% polygonize, buffer, dissolve, buffer back, and rasterize
    
    with rasterio.open(ind_image_paths[i], 'r+') as dataset:
        data = dataset.read(1) # Read the data into a numpy array
        mask = data != 0 # only create the mask for cells that are not zero
        dataset.write(data, 1) # Write the modified data back to the raster file
        
        # Extract shapes (polygons) of non-NA cells
        results = (
            {'properties': {'raster_val': v}, 'geometry': s}
            for i, (s, v) in enumerate(shapes(data, mask=mask, transform=dataset.transform))
        )
    
        geoms = list(results) # Convert shapes to GeoDataFrame
        if not geoms: # check if the geometry is empty. If it is empty, just copy the input file and continue
            print("The list is empty. Copying the original file to the output")
            shutil.copyfile(ind_image_paths[i], base_name_tif_full_path)
            continue
        gdf = gpd.GeoDataFrame.from_features(geoms)
        gdf.set_crs(dataset.crs, inplace=True) # Set the CRS of the GeoDataFrame to match the raster's CRS
        gdf=gdf.buffer(buf_dist) # buffer 100m up.
        buffered_gdf = gpd.GeoDataFrame(geometry=gdf) # Create a new GeoDataFrame with buffered geometries
        dissolved = buffered_gdf.dissolve() # Dissolve the buffered geometries into a single geometry
        gdf=dissolved.buffer(-buf_dist) # buffer down back
        #gdf.to_file(base_name_shp_full_path) # Save to shapefile
        
        # convert the shapefile into raster
        meta = dataset.meta # Get metadata
        mask = geometry_mask(gdf.geometry, out_shape=dataset.shape, transform=dataset.transform, invert=True) # Rasterize the polygon to a mask
        
        # Apply the mask to the raster
        data = dataset.read(1)
        data[mask] = 255
        
        dataset.close()
        
        # Write the result to a new raster file
        with rasterio.open(base_name_tif_full_path, 'w', **meta) as dst:
            dst.write(data, 1)
    
    




