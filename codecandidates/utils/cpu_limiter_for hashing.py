Python - limit cpu percentage for script
# It is sometimes useful to monitor how much cpu time or
# cpu percentage your script is consuming.
# This script will limit the cpu usage of your script

# This example demostrates how to calculate the system
# and user cpu time and cpu percentage

# Note: this example is in python 3.0
#   however, it is easily ported back to 2.x
#   by replaceing print() with print

import os
import time

def getPercentage(unew, uold, start):
    """
    calculate the percentage of cpu time
    """
    return 100 * (float(unew) - float(uold)) / (time.time()-float(start))

def looper(timeCount, percentageGoal):
    """
    loop over many tasks and keep the total cpu percentage
    consumtion to a desired level
    """
    start = time.time()
    time.sleep(0.1)
    keepLooping = True
    uold, sold, cold, c, e = os.times()
    percentage = 0.0
    while keepLooping:
        unew, snew, cnew, c, e = os.times()
        # since we are calculating the times from before we started looping the
        # percentages will be averaged over the duration of the script.
        print ("user %", percentage)

        # This just toggles to stop looping
        # when a time has been reached. In a real
        # script you would check for more work and
        # toggle off when there is no more work to
        # be done.
        if time.time()-start > timeCount:
            keepLooping = False
        #else:
        #    print( time.time()-start)

        # do work:
        #   In order for this script to actually help limit
        #   the cpu usage you would need to break your script into
        #   sections.
        #   For example: if you were going to iterate through a large
        #       list of data and perform actions on the contents
        #       of the list then you should perform on action here
        #       and keep looping through until all the actions
        #       are accomplished.
        #
        # in this case we're just eating cpu so we get some numbers
        print("do work...")
        for i in range(1,1000000):
            b = 8*342*i*234

        # tone back cpu usage
        while True:
            percentage = getPercentage(unew, uold, start)
            if percentage > percentageGoal:
                time.sleep(0.1)
            else:
                break;

if __name__ == '__main__':
    # loop through work (for 4 seconds) and keep the cpu %
    # to less than 30%
    looper(4, 30)

## my output:
##      user % 0.0
##      do work...
##      user % 0.0
##      do work...
##      user % 29.6673831301
##      do work...
##      user % 29.1137166495
##      do work...
##      user % 29.7617156875
##      do work...
##      user % 29.5707887319
##      do work...
##      user % 29.8122197706
##      do work...
##      user % 29.3053848216
##      do work...
##      user % 29.9385051866
##      do work...
