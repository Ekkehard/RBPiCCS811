# Python Implementation: CCS811UnitTest
##
# @file       CCS811UnitTest.py
#
# @version    1.0.1
#
# @par Purpose
# This module provides the Unit Test for the CCS811 module.  It has been
# separated from the CCS811 module to conserve some resources, as this code is
# intended to also run on an Raspberry Pi Pico MCU.  On this architecture, it is
# mandatory that the CCS811.py and GPIO_AL.py file both reside on the Raspberry
# Pi Pico's flash drive.
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
#   Fri Oct 29 2021 | Ekkehard Blanz | separated from CCS811L.py
#   Thu Dec 09 2021 | Ekkehard Blanz | added warning not to use hardware mode on
#                   |                | the Raspberry Pi
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
    exitChar = 'Ctrl-C'
except:
    traceback = None
    # keyboard interrupt on Raspberry Pi Pico is broken and gets "stuck"
    # so new inputs are also interrupted - use 'q' instead where possible
    exitChar = 'q'

#  main program - Unit Test

class Temperature( object ):

    ##! Freezing point in deg F
    F0 = 32
    ##! Absolute zero in deg C
    T0 = -273.15
    ##! ratio of difference of deg C to deg F
    CF_RATIO = 9. / 5.

    def __init__( self, kelvin=None, celsius=None, fahrenheit=None ):
        self.__kelvin = None
        if fahrenheit is not None:
            self.__kelvin = (fahrenheit - self.F0) / self.CF_RATIO - self.T0
        elif celsius is not None:
            self.__kelvin = celsius - self.T0
        elif kelvin is not None:
            self.__kelvin = kelvin
        return

    @property
    def kelvin( self ):
        return self.__kelvin

    @property
    def celsius( self ):
        return self.__kelvin + self.T0

    @property
    def fahrenheit( self ):
        return (self.__kelvin + self.T0) * self.CF_RATIO + self.F0


class Humidity( object ):
    def __init__( self, humidity ):
        self.__humidity = humidity
        return

    @property
    def humidity( self ):
        return self.__humidity


if __name__ == "__main__":

    DEBUG = True

    def main():
        """!
        @brief Unit Test for CCS811.
        """

        i2cBus = None
        aqSensor = None

        print( 'In all cases accept default values (in parentheses) by '
               'hitting Enter\n' )

        try:
            while True:
                print( '\nSet up I2C bus parameters' )
                print( '-------------------------' )
                print( 'Enter {0} to end this test\n'
                       ''.format( exitChar ) )
                try:
                    try:
                        sdaPin = int( input(
                            '\nsda Pin ({0}): '
                            ''.format( I2Cbus.DEFAULT_DATA_PIN ) ) )
                    except ValueError:
                        sdaPin = I2Cbus.DEFAULT_DATA_PIN

                    try:
                        sclPin = int( input(
                            'scl Pin ({0}): '
                            ''.format( I2Cbus.DEFAULT_CLOCK_PIN ) ) )
                    except ValueError:
                        sclPin = I2Cbus.DEFAULT_CLOCK_PIN

                    try:
                        mode = int( input( 'mode - {0} for HW, {1} for SW ('
                                           '{2})'
                                           ''.format( I2Cbus.HARDWARE_MODE,
                                                      I2Cbus.SOFTWARE_MODE,
                                                      I2Cbus.DEFAULT_MODE ) ) )
                    except ValueError:
                        mode = I2Cbus.DEFAULT_MODE

                    if mode == I2Cbus.SOFTWARE_MODE or isPico():
                        try:
                            frequency = int( input(
                                'frequency in Hz ({0} Hz): '
                                ''.format( I2Cbus.DEFAULT_I2C_FREQ ) ) )
                        except ValueError:
                            frequency = I2Cbus.DEFAULT_I2C_FREQ
                    else:
                        frequency = I2Cbus.DEFAULT_I2C_FREQ

                    try:
                        attempts = int( input( 'number of attempts {0}: '
                                               ''.format( I2Cbus.ATTEMPTS ) ) )
                    except ValueError:
                        attempts = I2Cbus.ATTEMPTS
                except KeyboardInterrupt:
                    print()
                    break

                try:
                    i2cBus = I2Cbus( sdaPin, sclPin, mode, frequency, attempts )
                    print( 'I2C bus opened successfully: {0}'.format( i2cBus ) )
                    break
                except (ValueError, GPIOError) as e:
                    print( e )
                    continue

            while i2cBus is not None:
                print( '\nSet up CCS811 sensor parameters' )
                print( '-------------------------------' )
                print( 'Again, enter {0} to end this input and '
                       'start over\n'.format( exitChar ) )
                try:
                    try:
                        i2cAddr = int( input( 'Enter CCS811 device address in '
                                              'hex (0x{0:02X}): '
                                              ''.format( CCS811.DEFAULT_ADDR )
                                            ), 16 )
                    except ValueError:
                        i2cAddr = CCS811.DEFAULT_ADDR

                    try:
                        interruptPin = int( input( 'Enter interrupt Pin or '
                                                   'empty line for poll '
                                                   'mode: ' ) )
                    except ValueError:
                        interruptPin = None

                    try:
                        wakeupPin = int( input( 'Enter wakeup Pin or empty '
                                                'line: ' ) )
                    except ValueError:
                        wakeupPin = None

                    print( 'Enter measurement interval' )
                    print( '1 s .... {0} (default)'
                           ''.format( CCS811.MEAS_INT_1 ) )
                    print( '10 s ... {0}'.format( CCS811.MEAS_INT_10 ) )
                    print( '60 s ... {0}'.format( CCS811.MEAS_INT_60 ) )
                    print( '250 ms . {0}'.format( CCS811.MEAS_INT_250MS ) )
                    try:
                        measInterval = int( input( '> ' ) )
                    except ValueError:
                        measInterval = CCS811.MEAS_INT_1

                    try:
                        temp = float( input( 'Enter temperature in deg F to '
                                             'use dummy temp object or empty '
                                             'line: ' ) )
                        tempObj = Temperature( fahrenheit=float( temp ) )
                    except ValueError:
                        tempObj = None

                    try:
                        humid = float( input( 'Enter humidity in % to use '
                                              'dummy humidity object or '
                                              'empty line: ' ) )
                        humObj = Humidity( float( humid ) )
                    except ValueError:
                        humObj = None
                except KeyboardInterrupt:
                    print()
                    break

                try:
                    aqSensor = CCS811( i2cBus,
                                       measInterval,
                                       interruptPin,
                                       wakeupPin,
                                       tempObj,
                                       humObj,
                                       i2cAddr )
                    print( 'Successfully opened CCS811 sensor: {0}'
                           ''.format( aqSensor ) )

                except ValueError as e:
                    if traceback is not None:
                        traceback.print_exc()
                    else:
                        print( '\nCCS811 ERROR: {0}'.format( e ) )
                    try:
                        del aqSensor
                    except:
                        pass
                    aqSensor = None
                    continue
                except GPIOError as e:
                    if traceback is not None:
                        traceback.print_exc()
                    else:
                        print( '\nGPIO ERROR: {0}'.format( e ) )
                    try:
                        del aqSensor
                    except:
                        pass
                    aqSensor = None
                    continue

                try:
                    print( 'Enter Ctrl-C to end data acquisition' )
                    answer = input( 'Hit Enter to start test or q to quit' )
                    if answer == 'q':
                        break
                    if wakeupPin is None:
                        if interruptPin is None:
                            print( 'Testing in regular poll mode...' )
                            while True:
                                aqSensor.waitforData()
                                print( 'CO2: {0} ppm, total VOC: '
                                       '{1} ppb'.format( aqSensor.CO2,
                                                         aqSensor.tVOC ) )
                                if aqSensor.errorCondition:
                                    print( aqSensor.errorText )
                        else:
                            print( 'Testing in regular interrupt mode...' )
                            while True:
                                if not aqSensor.staleMeasurements:
                                    print( 'CO2: {0} ppm, total VOC: '
                                           '{1} ppb'.format( aqSensor.CO2,
                                                             aqSensor.tVOC ) )
                                if aqSensor.errorCondition:
                                    print( aqSensor.errorText )
                    else:
                        print( 'Testing sleep/wake functionality in ', end='' )
                        if interruptPin is None:
                            print( 'poll mode...' )
                            while True:
                                startTime = time.time()
                                while time.time() - startTime < 10:
                                    aqSensor.waitforData()
                                    print( 'CO2: {0} ppm, total VOC: {1} '
                                           'ppb'.format( aqSensor.CO2,
                                                         aqSensor.tVOC ) )
                                print( 'sending sensor to sleep '
                                       '(should not see measurements)...' )
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
                    print( '\nGot keyboard interrupt' )
                    if aqSensor is not None:
                        aqSensor.close()
                        aqSensor = None

        except KeyboardInterrupt:
            if aqSensor is not None:
                aqSensor.close()
                aqSensor = None

        except ValueError as e:
            if traceback is not None:
                traceback.print_exc()
            else:
                print( '\nCCS811 ERROR: {0}'.format( e ) )
        except GPIOError as e:
            if traceback is not None:
                traceback.print_exc()
            else:
                print( '\nGPIO ERROR: {0}'.format( e ) )
        except Exception as e:
            if traceback is not None:
                traceback.print_exc()
            else:
                print( '\nERROR: {0}'.format( e ) )

        print( '\nClosing CCS811 and I2Cbus objects (in that order)...' )
        if aqSensor is not None:
            aqSensor.close()
        if i2cBus is not None:
            i2cBus.close()

        print( '\nExiting...\n' )
        return 0


    sys.exit( int( main() or 0 ) )
