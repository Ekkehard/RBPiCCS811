# Python Implementation: QADWakeupTest
##
# @file       QADWakeupTest.py
#
# @version    1.0.0
#
# @par Purpose
# This module provides Quick And Dirty Wakeup Test for the CCS811 module.  On
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
# See NOTICE.md and LICENSE.md files that come with this distribution.

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

try:
    import traceback
except:
    traceback = None

#  main program - Quick And Dirty Wakeup Test

if __name__ == "__main__":


    def main():
        """!
        @brief Quick And Dirty Wakeup Test for CCS811.
        """

        i2cBus = I2Cbus()
        aqSensor = None

        # CCS811 parameter(s):
        interruptPin = 6
        wakeupPin = 5
        print( 'Connect GPIO Pin 5 to nWAK and GPIO Pin 6 to nINT' )
        input( 'Hit Enter when done' )

        try:
            aqSensor = CCS811( i2cBus,
                               interruptPin=interruptPin,
                               wakeupPin=wakeupPin )
            while True:
                if not aqSensor.staleMeasurements:
                    print( 'CO2: {0} ppm, total VOC: '
                            '{1} ppb'.format( aqSensor.CO2, aqSensor.tVOC ) )
                if aqSensor.errorCondition:
                    print( aqSensor.errorText )

                if interruptPin is None:
                    print( 'poll mode...' )
                    while True:
                        startTime = time.time()
                        while time.time() - startTime < 10:
                            if aqSensor.dataReady:
                                print( 'CO2: {0} ppm, total VOC: {1} '
                                       'ppb'.format( aqSensor.CO2,
                                                     aqSensor.tVOC ) )
                        print( 'sending sensor to sleep '
                               '(expect no measurements)...' )
                        aqSensor.sleep()
                        startTime = time.time()
                        while time.time() - startTime < 10:
                            if aqSensor.dataReady:
                                print( 'CO2: {0} ppm, total VOC: {1} '
                                       'ppb'.format( aqSensor.CO2,
                                                     aqSensor.tVOC ) )
                        print( 'waking sensor up again '
                               '(expect new measurements)!' )
                        aqSensor.wake()
                else:
                    print( 'interrupt mode...' )
                    while True:
                        startTime = time.time()
                        while time.time() - startTime < 20:
                            if not aqSensor.staleMeasurements:
                                print( 'CO2: {0} ppm, total VOC: {1} '
                                       'ppb'.format( aqSensor.CO2,
                                                     aqSensor.tVOC ) )
                        print( 'sending sensor to sleep '
                               '(expect no measurements '
                               'and no interrupt signals)...' )
                        aqSensor.sleep()
                        startTime = time.time()
                        while time.time() - startTime < 20:
                            if not aqSensor.staleMeasurements:
                                print( 'CO2: {0} ppm, total VOC: {1} '
                                       'ppb'.format( aqSensor.CO2,
                                                     aqSensor.tVOC ) )
                        print( 'waking sensor up again '
                               '(expect new measurements)!' )
                        aqSensor.wake()
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
