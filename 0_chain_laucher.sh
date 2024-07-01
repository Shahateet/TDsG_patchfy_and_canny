#!/bin/bash

######################################################################
###                                                                ###
### Flags for debugging                                            ###
###                                                                ###
######################################################################

flag_patchify=1
flag_edge=1
flag_buffer=1

######################################################################
###                                                                ###
### Pacthify                                                       ###
###                                                                ###
######################################################################
output_folder="Temp_patchified_images"
if [ "$flag_patchify" == "1" ]; then
echo "-------------------------------------------------"
echo "-                patchifying                    -"
echo "-------------------------------------------------"
echo ""
echo "Input Image: $1"
echo ""

in_name=$1
new_resampled_name=${in_name//".tif"/"_resampled_temp.tif"}
new_resampled_name_last=${in_name//".tif"/"_resampled.tif"}

# Definying patch size and step size
patchsize_default_x=8192 # default patch size in x
patchsize_default_y=8192 # default patch size in y
# stepsize_default=2048 # default step size
width_default=16384 # default width x
heigth_default=16384 # default heigth y


read -p "Define patch size in x ($patchsize_default_x): " patchsize_in_x # read user input for patch size in x
patchsize_x=${patchsize_in_x:=$patchsize_default_x} # if user does not define, take default
echo ""

read -p "Define patch size in y ($patchsize_default_y): " patchsize_in_y # read user input for patch size in y
patchsize_y=${patchsize_in_y:=$patchsize_default_y} # if user does not define, take default
echo ""

read -p "Define the target width ($width_default): " width_in # read user input for patch size in x
new_width=${width_in:=$width_default} # if user does not define, take default
echo ""

read -p "Define the target height ($heigth_default): " height_in # read user input for patch size in y
new_height=${height_in:=$heigth_default} # if user does not define, take default
echo ""

# get heigth, width, and resolution information from the input image
old_width=$(gdalinfo $1 | grep "Size is" | awk '{print $4}' FS=" ")
old_height=$(gdalinfo $1 | grep "Size is" | awk '{print $3}' FS=" " | awk '{print $1}' FS=",")
old_pixel_x=$(gdalinfo $1 | grep "Pixel Size" | awk '{print $2}' FS="=" | awk '{print $1}' FS="," | sed 's/(//g')
old_pixel_y=$(gdalinfo $1 | grep "Pixel Size" | awk '{print $2}' FS="=" | awk '{print $2}' FS="," | sed 's/)//g')

new_pixel_x=$(echo "($old_pixel_x*$old_width/$new_width)" | bc -l)
new_pixel_y=$(echo "($old_pixel_x*$old_height/$new_height)" | bc -l)

echo "The new x pixel size will be: $new_pixel_x"
echo "The new y pixel size will be: $new_pixel_y"
echo ""

# read -p "Define step size ($stepsize_default): " stepsize_in # read user input for step size
# stepsize=${stepsize_in:=$stepsize_default} # if user does not define, take default
# echo ""

#gdalwarp -tr $new_pixel_x $new_pixel_y -of GTiff -r lanczos $1 $new_resampled_name
gdalwarp -ts $new_width $new_height -of GTiff -r lanczos $1 $new_resampled_name_last
rm $new_resampled_name

gdal_retile.py -ps $patchsize_x $patchsize_y $new_resampled_name_last -targetDir $output_folder
# python code/patchify_KS.py $1 $output_folder $patchsize_x $patchsize_y $stepsize

fi

######################################################################
###                                                                ###
### Edge identification with Canny                                 ###
###                                                                ###
######################################################################
In_im=$PWD/Temp_patchified_images/
echo "Input Image: $In_im"
echo ""

output_path=$PWD/Output_images/

if [ "$flag_edge" == "1" ]; then
echo "-------------------------------------------------"
echo "-             Edge identification               -"
echo "-------------------------------------------------"
echo ""

multiplier_file=$(cat parameters/.saved_parameters_canny.txt | grep multiplier | awk '{print $2}' FS=": ")
subtractor_file=$(cat parameters/.saved_parameters_canny.txt | grep subtractor | awk '{print $2}' FS=": ")
bottom_threshold_file=$(cat parameters/.saved_parameters_canny.txt | grep bottom_threshold | awk '{print $2}' FS=": ")
upper_threshold_file=$(cat parameters/.saved_parameters_canny.txt | grep upper_threshold | awk '{print $2}' FS=": ")

echo "----------Image gain----------"

read -p "Define multiplier ($multiplier_file): " multiplier_in
multiplier=${multiplier_in:=$multiplier_file}
echo ""

read -p "Define subtractor ($subtractor_file): " subtractor_in
subtractor=${subtractor_in:=$subtractor_file}
echo ""

read -p "Define bottom_threshold ($bottom_threshold_file): " bottom_threshold_in
bottom_threshold=${bottom_threshold_in:=$bottom_threshold_file}
echo ""

read -p "Define upper_threshold ($upper_threshold_file): " upper_threshold_file_in
upper_threshold=${upper_threshold_in:=$upper_threshold_file}

python code/edge_detection_with_canny.py $In_im $output_path $multiplier $subtractor $bottom_threshold $upper_threshold

fi

rm $In_im/*

######################################################################
###                                                                ###
### Buffer tif image                                               ###
###                                                                ###
######################################################################
if [ "$flag_buffer" == "1" ]; then
echo "-------------------------------------------------"
echo "-                    Buffer                     -"
echo "-------------------------------------------------"
echo ""

buffer_default=100

read -p "Define the buffer distance ($buffer_default meters): " buffer_in
buffer=${buffer_in:=$buffer_default}
echo "buffer $buffer"

python code/buffer.py $output_path $buffer

fi


