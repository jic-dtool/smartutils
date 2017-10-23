Doing an analysis with dtool
============================

Steps
-----

1. Create a dataset from your raw data using dtool.
2. Copy the dataset to irods:///jic_raw_data
3. Run the script create_overlays.py from the `smartutils project <https://github.com/jic-dtool/smartutils>`_, e.g:

.. code-block:: none

    python scripts/create_overlays.py irods:///jic_raw_data/rg-matthew-hartley/94bbad68-f386-4a6b-ae27-3ed0eb6bbd38

This will create an overlay called ``useful_name`` which will be used to name output files.
4. Create an output dataset:

.. code-block:: none

    dtool create adamskin_pre_anthesis_tif_files /jic_overflow/rg-matthew-hartley irods

5. (Optional) Test with:


.. code-block:: none

    singularity exec /jic/software/testing/convertlif/0.1.0/convertlif \
      python /scripts/convertlif.py \
      -d irods:///jic_raw_data/rg-matthew-hartley/94bbad68-f386-4a6b-ae27-3ed0eb6bbd38 \
      -o irods:///jic_overflow/rg-matthew-hartley/3d86ffe0-e12e-4c27-99f0-994fd9f8e9d9 \
      -i 5307967bb77d9a129c5b5f65d1284ff4be49ff69

6. Generate slurm scripts with:

.. code-block:: none

    python scripts/generate_slurm_scripts.py \
      irods:///jic_raw_data/rg-matthew-hartley/94bbad68-f386-4a6b-ae27-3ed0eb6bbd38 \
      irods:///jic_overflow/rg-matthew-hartley/3d86ffe0-e12e-4c27-99f0-994fd9f8e9d9

7. Copy output to the cluster, separate into separate scripts using split, e.g.:

.. code-block:: none

    split -n 8 all_slurm_submission_scripts submit_lif_conversion.slurm

8. Submit to slurm:

.. code-block:: none

    for FILE in submit_*; do
        sbatch $FILE
    done

To do
-----

* Consider adapting to jobqueue (redis based) approach
* Automate where possible (steps 1, 2, 3 then 4, 6, 7, 8)
* Add dtool freeze at end
