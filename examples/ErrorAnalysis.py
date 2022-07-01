# Python Implementation: ErrorAnalysis
##
# @file       ErrorAnalysis.py
#
# @version    1.0.0
#
# @par Purpose
# Produce a trigger signal after a CCS811 error situation occurs.
#
# @par Comments
# This is Python 3 code!  PEP 8 guidelines are decidedly NOT followed in some
# instances, and guidelines provided by "Coding Style Guidelines" a "Process
# Guidelines" document from WEB Design are used instead where the two differ,
# as the latter span several programming languages and are therefore applicable
# also for projects that require more than one programming language; it also
# provides consistency across hundreds of thousands of lines of legacy code.
# Doing so, ironically, is following PEP 8.
#
# @par Known Bugs
# None
#
# @author
# W. Ekkehard Blanz <Ekkehard.Blanz@gmail.com>
#
# @copyright
# Copyright 2021 W. Ekkehard Blanz
# See NOTICE.md and LICENSE.md files that come with this distribution.

# File history:
#
#      Date         | Author         | Modification
#  -----------------+----------------+------------------------------------------
#   Tue Dec 21 2021 | Ekkehard Blanz | created
#                   |                |

import sys
import time

try:
    import os.path
    import os
    sys.path.append( os.path.join( os.path.dirname( __file__ ),
                                   os.pardir ) )
    sys.path.append( os.path.join( os.path.dirname( __file__ ),
                                   os.pardir,
                                   os.pardir,
                                   'GPIO_AL' ) )
except ImportError:
    # on the Pico there is no os.path but all modules are in the same directory
    pass


from GPIO_AL import *
from CCS811 import *

try:
    import traceback
except:
    traceback = None

#  main program - Quick And Dirty Poll Test

if __name__ == "__main__":


    def main():
        """!
        @brief generate trigger signal when CCS811 error occurs.
        """
        aqSensor = None
        i2cBus = None
        
        try:

            # use the I2C bus with default parameters only
            i2cBus = I2Cbus()
            print( 'Using I2C bus: {0}'.format( i2cBus ) )

            pin = int( input( 'Enter Pin number for trigger signal: ' ) )
            triggerPin = IOpin( pin, IOpin.OUTPUT )
            print( 'Using trigger Pin: {0}'.format( triggerPin ) )
            triggerPin.level = IOpin.LOW

            aqSensor = CCS811( i2cBus )
            while True:
                _ = aqSensor.dataReady
                if aqSensor.errorCondition:
                    triggerPin.level = IOpin.HIGH
                    triggerPin.level = IOpin.LOW
                    print( "Error: " + aqSensor.errorText )
                if not aqSensor.staleMeasurements:
                    print( 'CO2: {0} ppm, total VOC: {1} '
                           'ppb'.format( aqSensor.CO2, aqSensor.tVOC ) )
        except KeyboardInterrupt:
            pass
        except Exception as e:
            if traceback is not None:
                traceback.print_exc()
            else:
                print( e )

        print( 'Exiting...' )
        try:
            aqSensor.close()
        except:
            pass
        i2cBus.close()

        return 0

    sys.exit( int( main() or 0 ) )
