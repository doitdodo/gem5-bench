#!/bin/bash -

CPU=`cat /proc/cpuinfo | grep vendor_id | head -n 1 | cut -d ' ' -f2-`
echo "Got CPU type: $CPU"

if [ "$CPU" != "M5 Simulator" ];
then
    echo "Not in gem5. Not loading script" | tee /home/gem5/gem5init.log
    export M5_CPU2006="/home/jmst/wrk/benchmark/cpu2006"
    echo "M5_CPU2006=$M5_CPU2006"
    /home/gem5/c.sh |& tee -a /home/gem5/gem5init.log
    exit 0
fi

# Try to read in the script from the host system
echo "In gem5. loading script" | tee /home/gem5/gem5init.log
/sbin/m5 readfile > /tmp/script
chmod 755 /tmp/script
if [ -s /tmp/script ]
then
    echo "Loaded script" | tee -a /home/gem5/gem5init.log
    # If there is a script, execute the script and then exit the simulation
    #su root -c 'export M5_CPU2006=/home/jmst/wrk/benchmark/cpu2006;/tmp/script' # gives script full privileges as root user in multi-user mode
    export M5_CPU2006=/home/jmst/wrk/benchmark/cpu2006 |& tee -a /home/gem5/gem5init.log
    /tmp/script |& tee -a /home/gem5/gem5init.log
    sync
    echo "Script done, exit in 10s" | tee -a /home/gem5/gem5init.log
    /sbin/m5 writefile /home/gem5/gem5init.log gem5init.log
    sleep 10
    /sbin/m5 exit
fi
echo "No script found"

