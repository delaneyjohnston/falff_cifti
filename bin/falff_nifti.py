#!/usr/bin/env python

"""
Calculates fractional amplitude of low-frequency fluctuations (fALFF)


Usage:
    falff_nifti.py <func.nii.gz> <output.nii.gz> [options]

Arguments:
    <func.nii.gz>  The functional 4D nifti files
    <mask.nii.gz>  A brainmask for the functional file
    <output.nii.gz>  Output filename

Options:
  --min-low-freq 0.01  Min low frequency range value Hz [default: 0.01]
  --max-low-freq 0.08  Max low frequency range value Hz [default: 0.08]
  --min-total-freq 0.00  Min total frequency range value Hz [default: 0.00]
  --max-total-freq 0.25  Max total frequency range value Hz [default: 0.25]
  --mask-file <mask.nii.gz>  Input brain mask 

  --debug  Debug logging
  -h,--help  Print help
"""

import numpy as np
import nibabel as nib
from scipy.fftpack import fft
import matplotlib.pyplot as plt
from docopt import docopt

arguments = docopt(__doc__)
funcfile = arguments['<func.nii.gz>']
outputname = arguments['<output.nii.gz>']
min_low_freq = arguments['--min-low-freq']
max_low_freq = arguments['--max-low-freq']
min_total_freq = arguments['--min-total-freq']
max_total_freq = arguments['--max-total-freq']
maskfile = arguments['--mask-file']

DEBUG = arguments['--debug']

if DEBUG: print(arguments)


def calculate_falff(timeseries, min_low_freq, max_low_freq, min_total_freq, max_total_freq):
    ''' this will calculated falff from a timeseries'''

    #FALFF CALCULATION
    n = len(timeseries)
    time = (np.arange(n))*2

    #takes fast fourier transform of timeseries
    fft_timeseries = fft(timeseries)
    #calculates frequency scale
    freq_scale = np.fft.fftfreq(n, 1/1)

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

#load in func and mask data
func_img = nib.load(funcfile)
func_data = func_img.get_data()


#if given input of mask, load in mask file
#OR if not given input of mask, create mask using std 
try:
    #1. given input of mask file
    mask = (nib.load(maskfile)).get_data()
except:
    #2. manually create mask 
    mask = np.where(func_data > (np.std(func_data, axis=(0, 1, 2))), func_data, 0)

    
#define affine array
affine = func_img.affine

#define x,y,z,t coordinates
x,y,z,t = func_data.shape

#find indices where mask does not = 0
indx,indy,indz,indt = np.where(mask != 0)

#create empy array to save values
falff_vol = np.zeros((x,y,z))

#loop through x,y,z indices, send to calculate_falff func
for x,y,z, t in zip(indx,indy,indz,indt):
    falff_vol[x,y,z] = calculate_falff(func_data[x,y,z,:], min_low_freq, max_low_freq, min_total_freq, max_total_freq)
    
#save falff values to nifti file 
output_3D = nib.Nifti1Image(falff_vol, affine)
output_3D.to_filename(outputname)

