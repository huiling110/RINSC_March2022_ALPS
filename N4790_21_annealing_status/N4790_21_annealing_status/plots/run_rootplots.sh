#!/usr/bin/env bash
#use Python >=3.6
#tested with 6.06 and 6.22

action() {
    local src_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && /bin/pwd )"
    local origin="$( pwd )"

    export PYTHONPATH=$PWD:$PYTHONPATH;
    # export HEXPLOT_DIR=/home/marta/HGCAL_sensor_analysis/;
    export HEXPLOT_DIR=/afs/cern.ch/work/h/hhua/HGCal_sensorTest/Hexplot/HGCAL_sensor_analysis/;
    export DATA_DIR=$PWD/../data/;
    # source /home/marta/root/bin/thisroot.sh; 

    cd "$src_dir"
    (
        python3 annealing_iv/overlay_iv_curve.py;
        python3 annealing_iv/current_vs_annealing.py;
    )
    (
        python3 annealing_Vdep/overlay_cv_curve.py;
    )      
    cd "$origin"
}
action "$@"  