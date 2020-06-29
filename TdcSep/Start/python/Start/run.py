#!/usr/bin/env python                                                           
#
#  -- Usage:
#     In this directory
#       >  nuwa.py -n 10 -m run
#     In other directories use Start.run
#       >  nuwa.py -n 10 -m Start.run OptionalInput.root
#     

from Gaudi.Configuration import ApplicationMgr
theApp = ApplicationMgr()

# Add myself into the queue                                                 
from Start.StartConf import Start
MyAlg=Start()
theApp.TopAlg.append(MyAlg)
