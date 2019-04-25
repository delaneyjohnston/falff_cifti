# fractional Amplitude Low Frequency Fluctuations (fALFF)
Delaney Johnston April 2019


## Running ciftify_clean_img.py and falff_nifti.py script on data using cleaned_and_falff_practice.sh 

[cleaned_and_falff_practice.sh](https://github.com/delaneyjohnston/falff_cifti/blob/master/bin/cleaned_and_falff_practice.sh)

Module load python and connectome-workbench. Input the following to [cleaned_and_falff_practice.sh](https://github.com/delaneyjohnston/falff_cifti/blob/master/bin/cleaned_and_falff_practice.sh): a directory for fMRI pre-processed 
`dtseries.nii` files (fMRIprep), an output directory for the calculated falff values, and a file with the chosen configurations. 
Clean output files from [ciftify_clean_img.py](https://github.com/edickie/ciftify/blob/master/ciftify/bin/ciftify_clean_img.py) will be inputted to [falff_nifti.py](https://github.com/delaneyjohnston/falff_cifti/blob/master/bin/falff_nifti.py) and saved in the given output directory as `dscalar.nii` falff files.

```
For Example: './cleaned_and_falff_practice.sh /scratch/colin/MST_open/fmriprep_ciftify /scratch/djohnston/faLFF/practice /scratch/djohnston/faLFF/MST_study/prefALFF_globalsignal.json'
```

Options for the [falff_nifti.py](https://github.com/delaneyjohnston/falff_cifti/blob/master/bin/falff_nifti.py) script can be entered by editing the [cleaned_and_falff_practice.sh](https://github.com/delaneyjohnston/falff_cifti/blob/master/bin/cleaned_and_falff_practice.sh) script following the docopt options. 


## Running pre- and post-treatment difference calculation using prepost_scan_diff.sh

[prepost_scan_diff.sh](https://github.com/delaneyjohnston/falff_cifti/blob/master/bin/prepost_scan_diff.sh)

Module load connectome_workbench. Input the following: an output directory for difference values and an input pre- and post-treatment scan directory. The scan directory must contain variable x as the post-treatment (ses-02) scan `dscalar.nii` falff file and variable y as the pre-treatment (ses-01) scan `dscalar.nii` falff file.


