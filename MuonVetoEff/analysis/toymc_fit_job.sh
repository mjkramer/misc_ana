#!/bin/bash
#SBATCH -N 1 -A dune -C knl -L project,projecta,SCRATCH -q regular -t 01:00:00

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
