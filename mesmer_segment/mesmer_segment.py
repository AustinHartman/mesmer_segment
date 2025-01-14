
## Jacob Gutierrez | Satpathy Lab | jacobog@stanford.edu | 5/5/22
## This script is a callable function which is input with a directory path to nanostring SMI results. Extracts the CellComposite Images for MESMER segmentation. MESMER segmentation masks are written to file for downstream use. Additional plotting functions to visualize the mask output on the DAPI channel compared directly to the Nanostring CellSegmentation images. 

## Libraries
import click ## Pretty Commandline
import glob ## Directory Parsing
import os ## To check files, directories
from mesmer_helper import * ## import all my functions to do the things
from skimage import io, color ## to make interpretable plot of segmentation
from matplotlib import pyplot as plt ## to show plots not needed in final
from deepcell.applications import Mesmer ## The good stuff.
import numpy as np ## Image processing

@click.command()
@click.option('--input', '-i', required=True, help='Path to SMI output directory (not the CellComposite Directory!) for resegmentation with MESMER')
@click.option('--visual', '-v', default = False, required=False, help='Logical Flag to generate plots of new segmentation compared to default SMI segmentation')

def mesmer_segment(input, visual):
    """
    mesmer_segment: Process SMI CellComposite images for segmentation.\n
    Jacob Gutierrez
    """
    
    ## set working dir as input. 
    wd = input
    
    ## Check if directory valid and return input cellcomposite paths for analysis
    all_in_paths = check_smi_dirs(input)
    
    ## Extract FOV names for easy writing and reading.  
    all_fovs = [os.path.splitext(os.path.basename(n))[0].split("_")[1] for n in all_in_paths]

    ## Create output path 
    seg_dir = "{}/MesmerSegmentation/".format(wd)
    os.makedirs(seg_dir, exist_ok=True) 

    
    ## We have files now so Spark up Mesmer 
    app = Mesmer()
    
    ## Loop over each FOV and create segmentation
    ## In theory could parallelize across images here depending on MESMER size which I am not pythonic enough to answer
    ## i is a string...
    for i , fov in enumerate(all_fovs):
        
        click.echo("Processing: {}".format(fov))
        fov_GB = prepare_composite(all_in_paths[int(i)])
        
        ## this gives an N x M x 2 matrix. Index 0 == Whole-Cell | Index 1 == Nueclear
        seg_fov = app.predict(fov_GB,compartment= 'both') ## Do the thing! Takes ~80-120 seconds per image 
        
        ## Squash the extra batch dim
        seg_fov = np.squeeze(seg_fov)
       
        
        ## Save Whole Cell Mask
        nuc_path = "{}/mesmer_whole_cell_{}.csv".format(seg_dir,fov)
        np.savetxt(nuc_path,seg_fov[:, :, (0)] ,delimiter = ',')
        
        ## Save Nuclear Mask
        nuc_path = "{}/mesmer_nucleus_{}.csv".format(seg_dir,fov)
        np.savetxt(nuc_path,seg_fov[:, :, (1)] ,delimiter = ',')
        
        ## Logical for Visualization
        if visual: 
            vis_fov(fov,wd,seg_fov)
            click.echo("VISUALIZATION WRITTEN")
        



    
    click.echo("All FOV's segmented DONE")

if __name__ == '__main__':
    mesmer_segment()
    