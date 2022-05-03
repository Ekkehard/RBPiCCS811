# Python Implementation: QADPollTest
##
# @file       I2cSignalTest.py
#
# @version    1.0.0
#
# @par Purpose
# This program generates signals on the I2C bus suitable for Logic Analyzer
# investigation to analyze the performance of hardware I2C control and
# software I2C control (bit banging) on the Raspberry Pi.  The CCS811 sensor
# is thereby used as a test object.
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
# Copyright 2022 W. Ekkehard Blanz
# See NOTICE.md and LICENSE.md files that come with this distribution.

# File history:
#
#      Date         | Author         | Modification
#  -----------------+----------------+------------------------------------------
#   Tue May 03 2022 | Ekkehard Blanz | created
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

from GPIO_AL import GPIOError, I2Cbus
from CCS811 import CCS811

if __name__ == "__main__":

    def main():
        """!
        @brief main program - I2C bus Signal Generator for Logic Analyzer.
        """
        f = float( input( 'Enter I2C bus frequency in Hz: ' ) )
        m = int( input( 'Enter mode ({0} hardware mode, {1} software mode): '
                        ''.format( I2Cbus.HARDWARE_MODE,
                                   I2Cbus.SOFTWARE_MODE ) ) )
        a = int( input( 'Enter number of communication attempts to be '
                        'made: ' ) )
        n = int( input( 'Enter number of reads to be made: ' ) )

        _ = input( 'Arm Logic Analyzer - hit Enter when done' )

        try:
            # use the I2C bus with user-entered parameters
            i2cBus = I2Cbus( frequency=f,
                             mode=m,
                             attempts=a )

            try:
                aqSensor = CCS811( i2cBus )
                for _ in range( n ):
                    try:
                        while not aqSensor.dataReady:
                            pass
                        if aqSensor.errorCondition:
                            raise GPIOError( aqSensor.errorText )
                        print( 'CO2: {0} ppm, total VOC: {1} ppb'
                               ''.format( aqSensor.CO2, aqSensor.tVOC ) )
                    except GPIOError as e:
                        print( 'Error reading data: {0}'.format( e ) )
                aqSensor.close()
            except GPIOError as e:
                print( 'Error: could not initialize CCS811 sensor ({0})'
                       ''.format( e ) )
            i2cBus.close()
        except GPIOError as e:
            print( 'Error: Could not initialize I2C bus ({0})'.format( e ) )

        print( 'Exiting...' )

        return 0


    sys.exit( int( main() or 0 ) )
