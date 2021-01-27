#!/bin/bash
#SBATCH -A dayabay -C haswell -N 1 -n 2 -t 02:00:00 -q regular -L project,projecta,SCRATCH

source ~/mywork/ThesisAnalysis/IbdSel/code/ibd_prod/bash/job_env.inc.sh

conda activate ibdsel1pp        # for numpy and stuff

export LBNL_FIT_HOME=~/mywork/ThesisAnalysis/Fitter

memwatch() {
    while true; do
        date; top ibn1; free -g
        sleep 10
    done
}

sleep $(( RANDOM % 60 ))

memwatch &

# XXX change this to a cmdline option of fit_worker
export TIMEOUT_MINS=85

srun -n $SLURM_NTASKS ./fit_worker.py "$@"
