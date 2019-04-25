#!/bin/bash

output_dir=$1
scan_dir=$2

#prescan = ses 01
#postscan = ses 02


for subpath in ${scan_dir}/sub*.dscalar.nii; do

  sub_name=$(basename $subpath | cut -d '_' -f 1)

  prescan_file=${scan_dir}/${sub_name}_ses-01_task-rest_acq-CMH_run-01_bold_desc-clean01_bold_alff.dscalar.nii # Change file depending on falff or alff
  postscan_file=${scan_dir}/${sub_name}_ses-02_task-rest_acq-CMH_run-01_bold_desc-clean01_bold_alff.dscalar.nii # Change file depending on falff or alff

  output_file=${output_dir}/${sub_name}_task-rest_acq-CMH_run-01_bold_desc-clean01_bold_diff.dscalar.nii

  
  wb_command -cifti-math '(x-y)' ${output_file} -var x ${postscan_file} -var y ${prescan_file}

done

