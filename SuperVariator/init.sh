#!/bin/bash
mkdir -p data/cutlists
mkdir -p data/job_input
mkdir -p $SCRATCH/fit_results.SuperVariator
ln -sn $SCRATCH/fit_results.SuperVariator data/fit_results
mkdir -p $SCRATCH/logs.SuperVariator
ln -sn $SCRATCH/logs.SuperVariator logs
