#!/usr/bin/env python

"""
Calculates fractional amplitude of low-frequency fluctuations (fALFF)


Usage:
    falff_nifti.py <func.nii.gz> <output.nii.gz> [options]

Arguments:
    <func.nii.gz>  The functional 4D nifti files
    <output.nii.gz>  Output filename
    <maskfile.nii.gz>  A brainmask for the functional file
    <tempfile.nii>  Temp cifti file to match cifti output conversion

Options:
  --min-low-freq 0.01  Min low frequency range value Hz [default: 0.01]
  --max-low-freq 0.08  Max low frequency range value Hz [default: 0.08]
  --min-total-freq 0.00  Min total frequency range value Hz [default: 0.00]
  --max-total-freq 0.25  Max total frequency range value Hz [default: 0.25]
  --mask-file <maskfile.nii.gz>  Input brain mask
  --cifti-temp-file <tempfile.dscalar.nii> Input cifti temp file dcsalar.nii

  --debug  Debug logging
  -h,--help  Print help
"""

import os
import numpy as np
import nibabel as nib
from scipy.fftpack import fft
import matplotlib.pyplot as plt
from docopt import docopt
import tempfile
import shutil
from nilearn import plotting, image
import subprocess as proc
import pdb
import sys


def main():
    ''''''
    arguments = docopt(__doc__)
    funcfile = arguments['<func.nii.gz>']
    outputname = arguments['<output.nii.gz>']
    min_low_freq = arguments['--min-low-freq']
    max_low_freq = arguments['--max-low-freq']
    min_total_freq = arguments['--min-total-freq']
    max_total_freq = arguments['--max-total-freq']
    maskfile = arguments['--mask-file']
    cifti_tempfile = arguments['--cifti-temp-file']

    DEBUG = arguments['--debug']

    if DEBUG: print(arguments)

    #makes a temp dircetory for fake input nifti and fake output nifti
    tmpdir = tempfile.mkdtemp()
    print(tmpdir)
    fake_nifti_input = os.path.join(tmpdir, 'input_fake.nii.gz')
    fake_nifti_output = os.path.join(tmpdir, 'output_fake.nii.gz')

    #IF INPUT IS NIFTI FILE 
    #sets input funcfile equal to inputfile 
    inputfile = funcfile

    #IF INPUT IS CIFTI FILE
    #convert cifti input file to nifti input file
    if 'nii.gz' not in funcfile:
        convert_cifti_to_nifti(funcfile, fake_nifti_input)
        inputfile = fake_nifti_input
    

    output_3D = calc_nifti(inputfile, maskfile, min_low_freq, max_low_freq, min_total_freq, max_total_freq, fake_nifti_output)


    #convert nifti output file to cifti output file
    if 'nii.gz' not in funcfile:
        fake_nifti_output = output_3D
        convert_nifti_to_cifti(fake_nifti_output, funcfile, outputname)
    else:
        #IF INPUT IS NIFTI FILE
        #if funcfile was not cifti file, save as nifti file to output name 
        output_3D.to_filename(outputname)

    #remove tmpdir and all it's contents
    #shutil.rmtree(tmpdir)



#runs the wb command on separate terminal 
def run(cmd):
    '''
    Runs a subprocess command:

    Arguments:
        cmd                     BASH command to Runs
    Returns:

    '''
    p = proc.Popen(cmd,stdin=proc.PIPE, stdout=proc.PIPE, shell=True)
    std, err = p.communicate()

    if p.returncode:
        print('Connectome workbench crashed with error {}'.format(err))
        sys.exit(1)
    return



#if input is cifti - we convert to fake nifti (fake_nifti_input)
##convert to nifti
def convert_cifti_to_nifti(funcfile, fake_nifti_input):

    run('wb_command -cifti-convert -to-nifti {} {} '.format(funcfile, fake_nifti_input))
    return fake_nifti_input


#if input is cifti - we convert nifti output (fake_nifti_output) back to cifti
##convert to cifti

# need temp file to match????

def convert_nifti_to_cifti(fake_nifti_output, cifti_tempfile, outputname):

    run('wb_command -cifti-convert -from-nifti {} {} {} -reset-scalars'.format(fake_nifti_output, cifti_tempfile, outputname))
    return outputname


#takes input files to give to falff function and returns output file 
def calc_nifti(inputfile, maskfile, min_low_freq, max_low_freq, min_total_freq, max_total_freq, outputname):
    '''
    calculates falff from nifti input and retruns nifti output 
    '''
    #load in func data
    func_img = nib.load(inputfile)
    func_data = func_img.get_data()

    #if given input of mask, load in mask file
    #OR if not given input of mask, create mask using std
    if maskfile:
        #1. given input of mask file
        mask = (nib.load(maskfile)).get_data()
    else:
        #2. manually create mask
        mask = np.std(func_data, axis=3)

    #find indices where mask does not = 0
    indx,indy,indz = np.where(mask != 0)

    #define affine array
    affine = func_img.affine

    #define x,y,z,t coordinates
    x,y,z,t = func_data.shape

    #create empy array to save values
    falff_vol = np.zeros((x,y,z))

    #loop through x,y,z indices, send to calculate_falff func
    for x,y,z in zip(indx,indy,indz):
        falff_vol[x,y,z] = calculate_falff(func_data[x,y,z,:], min_low_freq, max_low_freq, min_total_freq, max_total_freq)

    #save falff values to nifti file
    output_3D = nib.Nifti1Image(falff_vol, affine)

    return output_3D


#CALCULATES FALFF
def calculate_falff(timeseries, min_low_freq, max_low_freq, min_total_freq, max_total_freq):
    ''' this will calculate falff from a timeseries'''

    n = len(timeseries)
    time = (np.arange(n))*2

    #takes fast fourier transform of timeseries
    fft_timeseries = fft(timeseries)
    #calculates frequency scale
    freq_scale = np.fft.fftfreq(n, 1/0.5)

    #calculates power of fft
    mag = (abs(fft_timeseries))**0.5

    #finds low frequency range (0.01-0.08) and total frequency range (0.0-0.25)
    low_ind = np.where((float(min_low_freq) <= freq_scale) & (freq_scale <= float(max_low_freq)))
    total_ind = np.where((float(min_total_freq) <= freq_scale) & (freq_scale <= float(max_total_freq)))

    #indexes power to low frequency index, total frequency range
    low_power = mag[low_ind]
    total_power = mag[total_ind]
    #calculates sum of lower power and total power
    low_pow_sum = np.sum(low_power)
    total_pow_sum = np.sum(total_power)

    #calculates falff as the sum of power in low frequnecy range divided by sum of power in the total frequency range
    falff = np.divide(low_pow_sum, total_pow_sum)

    return falff


if __name__=='__main__':
    main()
