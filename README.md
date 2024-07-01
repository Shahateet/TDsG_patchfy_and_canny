# TDsG_IceDam
Project to facilitate the identification of fractures on glaciers

## Installations
The project makes use of bash (not sh) and python. We recommend using miniconda or micromamba to make the python installation in a virtual environment.
The list of installed packages with miniconda is listed in required_python_packages.txt. Following is the procedure to install the required packages on IGE-Calcul1 (ige-calcul1.u-ga.fr).

### Micromamba installation

First we need to install micromamba (in IGE-Calcul1 they recommend micromamba instead of miniconda. Refer to their original repository https://github.com/ige-calcul/public-docs/blob/main/clusters/Tools/micromamba.md. I would like to highlight here that differently of conda, we need to add some channels. Also, when pip command is ran, it installs outside the virtual environment.):
#### Create a virtual environment called ptor using python 3.12.3 and conda-forge as the channel.
micromamba create -n ptor python=3.12.3 -c conda-forge
#### activate virtual environment
micromamba activate ptor
#### install required packages with channels:
##### First pytorch and its dependencies. Note that I am using pytorch-cuda=12.1 despite the current cuda version is 12.4. This is the recommendation of the official pytorch website
micromamba install -c pytorch -c nvidia -c conda-forge -c defaults pytorch torchvision torchaudio pytorch-cuda=12.1
##### Other required packages
micromamba install -c conda-forge matplotlib
micromamba install -c conda-forge pillow
micromamba install -c conda-forge tifffile
micromamba install -c menpo -c conda-forge opencv
##### Install Segment-Anything Model
pip install git+https://github.com/facebookresearch/segment-anything.git # this installs SAM outside the virtual environment

## Training Dataset Generation (TDsG)
