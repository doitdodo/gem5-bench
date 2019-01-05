# -*- coding: utf-8 -*-
# Copyright (c) 2016 Jason Lowe-Power
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met: redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer;
# redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution;
# neither the name of the copyright holders nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# Authors: Jimmy Situ

import sys

import m5
from m5.objects import *

sys.path.append('configs/common/') # For the next line...
import SimpleOpts

from system import SimSystem

SimpleOpts.add_option("--script", default='',
                      help="Script to execute in the simulated system")

if __name__ == "__m5_main__":
    (opts, args) = SimpleOpts.parse_args()


    # create the system we are going to simulate
    system = SimSystem(opts, no_kvm=True)
    #system = SimSystem(opts)

    # Read in the script file passed in via an option.
    # This file gets read and executed by the simulated system after boot.
    # Note: The disk image needs to be configured to do this.
    system.readfile = opts.script

    # For workitems to work correctly
    # This will cause the simulator to exit simulation when the first work
    # item is reached and when the first work item is finished.
    system.work_begin_exit_count = 1
    system.work_end_exit_count = 1


    # set up the root SimObject and start the simulation
    root = Root(full_system = True, system = system)

    if system.getHostParallel():
        # Required for running kvm on multiple host cores.
        # Uses gem5's parallel event queue feature
        # Note: The simulator is quite picky about this number!
        root.sim_quantum = int(1e9) # 1 ms

    # instantiate all of the objects we've created above
    m5.instantiate()

    # Keep running until we are done.
    print("Running the simulation")
    curCpus = 'system.cpu'
    exit_event = m5.simulate()
    while exit_event.getCause() != "m5_exit instruction encountered":
        if exit_event.getCause() == "user interrupt received":
            print("User interrupt. Exiting")
            break

        print('Pause @ tick %i because %s' % (m5.curTick(),
                                              exit_event.getCause()))
        if exit_event.getCause() == "switchcpu":
            if 'system.cpu' == curCpus:
                system.switchCpus(system.cpu, system.timingCpu)
                curCpus = 'system.timingCpu'
            else:
                system.switchCpus(system.timingCpu, system.cpu)
                curCpus = 'system.cpu'
            m5.stats.reset()

        if exit_event.getCause() == "simulate() limit reached":
            if 'system.timingCpu' == curCpus:
                m5.stats.dump()
                m5.stats.reset()
                print("Continuing...")
                # run about 100us
                exit_event = m5.simulate(100000000)
            else:
                exit_event = m5.simulate()


    print('Exiting @ tick %i because %s' % (m5.curTick(),
                                            exit_event.getCause()))

