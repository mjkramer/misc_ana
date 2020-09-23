#!/bin/bash

go() {
    conf=$1; shift
    confdir=$IBDSEL_HOME/../data/config_sets/accIsol
    exe=$IBDSEL_HOME/selector/_build/stage2.exe
    infile=$IBDSEL_HOME/../data/stage1_dbd/2020_01_26/EH1/stage1.dbd.eh1.0001.root
    outfile=stage2_files/$(echo $conf | sed 's/config/stage2/' | sed 's/txt/root/')
    $exe $confdir/$conf $infile $outfile 1 1 1
}

# go config.1000_1000_0.7.txt &
go config.1000_1000_10.txt &
go config.1000_1000_3.txt &
go config.1000_1000_8.txt &
go config.1000_200_0.7.txt &
go config.1000_200_10.txt &
go config.1000_200_3.txt &
go config.1000_200_8.txt &
go config.1000_400_0.7.txt &
go config.1000_400_10.txt &
go config.1000_400_3.txt &
go config.1000_400_8.txt &
go config.1000_700_0.7.txt &
go config.1000_700_10.txt &
go config.1000_700_3.txt &
go config.1000_700_8.txt &
go config.400_1000_0.7.txt &
go config.400_1000_10.txt &
go config.400_1000_3.txt &
go config.400_1000_8.txt &
go config.400_200_0.7.txt &
go config.400_200_10.txt &
go config.400_200_3.txt &
go config.400_200_8.txt &
go config.400_400_0.7.txt &
go config.400_400_10.txt &
go config.400_400_3.txt &
go config.400_400_8.txt &
go config.400_700_0.7.txt &
go config.400_700_10.txt &
go config.400_700_3.txt &
go config.400_700_8.txt &
go config.700_1000_0.7.txt &
go config.700_1000_10.txt &
go config.700_1000_3.txt &
go config.700_1000_8.txt &
go config.700_200_0.7.txt &
go config.700_200_10.txt &
go config.700_200_3.txt &
go config.700_200_8.txt &
go config.700_400_0.7.txt &
go config.700_400_10.txt &
go config.700_400_3.txt &
go config.700_400_8.txt &
go config.700_700_0.7.txt &
go config.700_700_10.txt &
go config.700_700_3.txt &
go config.700_700_8.txt &

wait
