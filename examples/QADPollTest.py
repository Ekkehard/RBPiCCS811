# Python Implementation: QADPollTest
##
# @file       QADPollTest.py
#
# @version    1.0.0
#
# @par Purpose
# This module provides Quick And Dirty Poll Test for the CCS811 module.  On
# the Raspberry Pi Pico, it is mandatory that the CCS811.py and the GPIO_AL.py 
# file both reside on the Raspberry Pi Pico's flash drive.
#
# Because of the nature of the class under test, this Unit Test cannot be
# completely automated and requires user interaction to set voltage levels on
# GPIO Pins or measure them with appropriate instruments.
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
# See COPYING.md and LICENSE.md files that come with this distribution.

# File history:
#
#      Date         | Author         | Modification
#  -----------------+----------------+------------------------------------------
#   Mon Nov 01 2021 | Ekkehard Blanz | created
#                   |                |

import sys

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

if ARCHITECTURE == 'RaspberryPi':
    import traceback
elif ARCHITECTURE == 'RaspberryPiPico':
    traceback = None

#  main program - Quick And Dirty Poll Test

if __name__ == "__main__":
    
    
    def main():
        """!
        @brief Quick And Dirty Poll Test for CCS811.
        """
        
        try:
            # use the I2C bus with default parameters only
            i2cBus = I2Cbus()
            print( 'Using I2C bus: {0}'.format( i2cBus ) )

            print( 'Measurements obtained in poll mode:' )
            aqSensor = CCS811( i2cBus )
            while True:
                if aqSensor.dataReady:
                    print( 'CO2: {0} ppm, total VOC: {1} '
                           'ppb'.format( aqSensor.CO2, aqSensor.tVOC ) )
                if aqSensor.errorCondition:
                    print( "Error: " + aqSensor.errorText )
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
