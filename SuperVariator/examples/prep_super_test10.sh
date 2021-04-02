#!/bin/bash

cd ~/mywork/ThesisAnalysis/misc_ana/SuperVariator

study=super_test10
tag=2021_02_03

export IBDSEL_CONFIGDIR=/global/u2/m/mkramer/mywork/ThesisAnalysis/IbdSel/data/config_sets/$study

./gen_cutlist.py -n 10 > data/cutlists/$study.txt

./gen_ibdsel_conf.py data/cutlists/$study.txt

jobsPerConfig=4         # NB: Two configs didn't quite finish for delcut_first. 3 didn't for second.

configs=$(ls $IBDSEL_CONFIGDIR | sed 's/^config\.//' | sed 's/\.txt$//')

cd ~/mywork/ThesisAnalysis/IbdSel/code/ibd_prod

for conf in $configs; do
    scripts/prep_stage2.sh $tag $conf
done

for _ in $(seq $jobsPerConfig); do
    for conf in $configs; do
        scripts/submit_stage2_knl.sh $tag $conf 1 -A dune
    done
done

remconfigs=$(wc -l ../../data/stage2_input/$tag\@${study}_*/*done | head -n -1 | grep -v 5676 | sort | awk '{print $2}' | xargs -l dirname | xargs -l basename | cut -d@ -f2 | tr '\n' ' ')

# use sbatch_premium here
for conf in $remconfigs; do
    scripts/filter_done.sh stage2 $tag@$conf
done

for conf in $remconfigs; do
    scripts/submit_stage2_knl.sh $tag $conf 1 -A dune
done

mkdir -p ~/mywork/ThesisAnalysis/IbdSel/data/merge2_input/$study

(for c in $configs; do echo $tag $c; done) > ~/mywork/ThesisAnalysis/IbdSel/data/merge2_input/$study/input.list

mergecmd="python/merge2_worker.py -l ~/mywork/ThesisAnalysis/IbdSel/data/merge2_input/$study/input.list"
fullcmd="load-ibdsel1pp; cd ~/mywork/ThesisAnalysis/IbdSel/code/ibd_prod; nohup $mergecmd &>/dev/null </dev/null &"

for i in $(seq 3); do
    for node in 05 06 07 08; do
        ssh cori$node "$fullcmd"
    done
done

for conf in $configs; do
    ../fit_prep/fit_prep.py $tag $conf &
done

cd ~/mywork/ThesisAnalysis/misc_ana/SuperVariator

mkdir -p data/job_input/$study
./gen_data_job_input.py data/cutlists/$study.txt ~/mywork/ThesisAnalysis/IbdSel/data/fit_input/$tag@$study > data/job_input/$study/input.list

go() {
    jobname=$study
    wc -l data/job_input/$jobname/input.list || return
    mkdir -p logs/$jobname
    sbatch -A dune -C haswell -n 2 -t 02:00:00 -o logs/$jobname/jorb-%A_%t.log fit_job.sh data/job_input/$jobname/input.list $jobname
}

for _ in $(seq 5); do go; done
