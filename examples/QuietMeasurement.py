# Python Implementation: QuietMeasurement
##
# @file       QuietMeasurement.py
#
# @version    1.0.0
#
# @par Purpose
# This module provides an example of how to use the CCS811 sensor on a Raspberry
# Pi Mod. 3.  The I2C bus on these systems is pretty messy resulting in multiple
# errors.  If one is only interested in the measurements, however, these can be
# ignored.  This code shows how to do that.
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
#   Wed Dec 22 2021 | Ekkehard Blanz | created
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

#  main program - Quick And Dirty Interrupt Test

if __name__ == "__main__":
    
    
    def main():
        """!
        @brief Quick And Dirty Interrupt Test for CCS811.
        """

        try:
            # use the I2C bus with default parameters only
            i2cBus = I2Cbus()
            print( 'Using I2C bus: {0}'.format( i2cBus ) )

            # CCS811 interrupt Pin hard coded as 6
            interruptPin = 6
            
            input( 'Connect CCS811 interrupt Pin to Pin {0} of the Raspberry '
                   'Pi and hit Enter when done'.format( interruptPin ) )
            
            interval = int( input( 'Enter measurement interval (1, 2, or 3'
                                   ' for 1 s, 10 s, or 60 s): ' ) )
            
            print( 'Measurements obtained under interrupt control:' )

            aqSensor = CCS811( i2cBus,
                               measInterval=interval,
                               interruptPin=interruptPin )
            
            while True:
                if not aqSensor.staleMeasurements:
                    if aqSensor.errorCondition:
                        continue
                    print( 'CO2: {0} ppm, total VOC: '
                           '{1} ppb'.format( aqSensor.CO2, aqSensor.tVOC ) )
        except KeyboardInterrupt:
            pass
        except Exception as e:
            print( e )
        
        print( 'Exiting...' )
        try:
            aqSensor.close()
        except:
            pass
        i2cBus.close()

        return 0

    sys.exit( int( main() or 0 ) )

