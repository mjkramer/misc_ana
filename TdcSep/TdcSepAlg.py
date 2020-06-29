#!/usr/bin/env python

# from collections import defaultdict
# import pdb
import IPython
# import ipdb
import sys

# Load DybPython
from DybPython.DybPythonAlg import DybPythonAlg
from GaudiPython import SUCCESS, FAILURE
from GaudiPython import gbl
from DybPython.Util import irange
import GaudiKernel.SystemOfUnits as units

# Make shortcuts to any ROOT classes you want to use
TH1F = gbl.TH1F
TimeStamp = gbl.TimeStamp
Detector = gbl.DayaBay.Detector

# class HistDict(defaultdict):
#     def __missing__(self, key):
#         pass

# Make your algorithm
class TdcSepAlg(DybPythonAlg):
    def __init__(self,name):
        DybPythonAlg.__init__(self,name)
        self.hists = {}
        return

    def hist(self, det, board, conn):
        name = "%s-B%d-C%d" % (det, board, conn)
        if name not in self.hists:
            self.hists[name] = TH1F(name, name, 801, -0.5, 800.5)
            self.stats["/file1/TdcSep/%s" % name] = self.hists[name]
        return self.hists[name]

    def initialize(self):
        status = DybPythonAlg.initialize(self)
        if status.isFailure(): return status
        self.info("initializing")

        # Define histograms, initialize services here

        return SUCCESS

    def execute(self):
        evt = self.evtSvc()

        # Access the Readout Header.  This is a container for the readout data
        readoutHdr = evt["/Event/Readout/ReadoutHeader"]
        if readoutHdr == None:
            self.error("Failed to get current readout header")
            return FAILURE

        # Access the Readout.  This is the data from one trigger.
        readout = readoutHdr.daqCrate().asPmtCrate()
        if readout == None:
            # self.info("No readout this cycle")
            return SUCCESS

        # Get the detector ID for this trigger
        detector = readout.detector()
        if not detector.isAD():
            return SUCCESS

        # Loop over each channel data in this trigger
        for channel in readout.channelReadouts():
            sys.stdin = open("/dev/tty")
            IPython.embed()

            channelId = channel.channelId()

            hist = self.hist(channelId.detName(),
                             channelId.board(), channelId.connector())

            for hitIdx in range(1, channel.hitCount()):
                tdc = channel.tdc(hitIdx)
                prevTdc = channel.tdc(hitIdx - 1)
                hist.Fill(prevTdc - tdc)

        return SUCCESS
        
    def finalize(self):
        self.info("finalizing")
        status = DybPythonAlg.finalize(self)
        return status

#####  Job Configuration for nuwa.py ########################################

some_option = None

def configure( argv=[] ):
    """ Template job module """
    # Process module command line arguments here
    from optparse import OptionParser
    parser = OptionParser() 

    # Example module option
    parser.add_option("-s","--some-option",
                      default=1,
                      type="int",
                      help="Some example option  [default: %default]")

    (options,args) = parser.parse_args(args=argv)

    # Must save option so it can be use in 'run()' function
    global some_option 
    some_option = options.some_option
    print " Set some option to ", some_option

    # Add more configuration here
    
    return

def run(app):
    '''
    Configure and add the algorithm to job
    '''
    # Add Python algorithm to job here
    myAlg = TdcSepAlg("MyTdcSepAlg")
    # Retrieve module option, and set in algorithm
    global some_option
    myAlg.some_option = some_option
    # Add algorithm to job
    app.addAlgorithm(myAlg)
    pass

