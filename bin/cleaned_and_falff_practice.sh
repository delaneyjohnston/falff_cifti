#!/bin/bash

fmriprep_dir=$1
output_dir=$2
clean_config=$3

#/scratch/djohnston/faLFF/replicate_argyelan2016_prefALFF.json

for subpath in ${fmriprep_dir}/sub*; do

  echo $subpath
  sub_name=$(basename $subpath)

  for sespath in ${fmriprep_dir}/${sub_name}/MNINonLinear/Results/ses*; do

    echo $sespath
    ses_folder=$(basename $sespath)

    confounds_file=${subpath}/MNINonLinear/Results/${ses_folder}/${sub_name}_${ses_folder}_confounds.tsv
    left_surface=${subpath}/MNINonLinear/fsaverage_LR32k/${sub_name}.L.midthickness.32k_fs_LR.surf.gii
    right_surface=${subpath}/MNINonLinear/fsaverage_LR32k/${sub_name}.R.midthickness.32k_fs_LR.surf.gii
    uncleaned_file=${subpath}/MNINonLinear/Results/${ses_folder}/${ses_folder}_Atlas_s0.dtseries.nii
    output_file=${output_dir}/${sub_name}_${ses_folder}_desc-clean01_bold.dtseries.nii

    ciftify_clean_img --clean-config=${clean_config} --output-file=${output_file} --confounds-tsv=${confounds_file} --left-surface=${left_surface} --right-surface=${right_surface} ${uncleaned_file}


    input_falff=${output_file}
    output_falff=${output_dir}/${sub_name}_${ses_folder}_desc-clean01_bold_falff.dscalar.nii

    echo $input_falff
    echo $output_falff
    /scratch/djohnston/faLFF/falff_nifti.py ${input_falff} ${output_falff}


  done
done
