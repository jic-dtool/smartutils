With redis stuff
================

From smartutils repository, run:

.. code-block:: none

    export REDISHOST=j64n17
    singularity exec /jic/software/testing/smartutils/0.1.0/smartutils \
        python scripts/start_analysis.py \
        irods:///jic_archive/2707da2b-b0ca-4f48-b822-3f0d1fe70046 \
        file:///nbi/Research-Groups/JIC/Matthew-Hartley/data_intermediate/uauyc_cell_size_measurement/extra_lif_files_sept_2017_results

.. code-block:: none

    export 


adamskin_missing_tif_files       - irods:///jic_archive/4597209e-0634-4528-b643-15e663c276e2
adamskin_missing_file_results   - irods:///jic_overflow/rg-matthew-hartley/24f74940-0e9c-42da-8e47-2930b295dfca

input: 
output: file:///nbi/Research-Groups/JIC/Matthew-Hartley/data_intermediate/uauyc_cell_size_measurement/pre_anthesis_results

Notes
=====

From redis cli, to clear up:

.. code-block:: none

    del completed
    del inprogress

To restore from in progress to work queue (in case a worker blew up):

.. code-block:: none

    rpoplpush inprogress workqueue

projects/broken_rosetta
 clusman
 modulate
 rosetta_src
