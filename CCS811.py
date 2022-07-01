# Python Implementation: CCS811
##
# @file       CCS811.py
#
# @version    1.3.0
#
# @mainpage   Raspberry Pi CCS811 Python Driver
#
# @par Purpose
# This class encapsulates the Cambridge CMOS Sensors' Ultra-Low Power Digital
# Gas Sensor for Monitoring Indoor Air Quality CCS811.  It reads the
# CO<sub>2</sub> and tVOC (total Volatile Organic Compounds) values from the
# SparkFun CSS811 breakout board.
#
# @par Comments
# Note that a new sensor requires a 48 hour burn in. Once burned in, a sensor
# requires to run fo 20 minutes before readings are stable and considered valid.
#
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
#   Thu Sep 30 2021 | Ekkehard Blanz | created
#   Tue Oct 26 2021 | Ekkehard Blanz | now uses GPIO_AL
#   Sat Dec 18 2021 | Ekkehard Blanz | made a lot more robust to run on
#                   |                | Raspberry Pi
#   Wed Dec 22 2021 | Ekkehard Blanz | turned into properties what should be
#                   |                |


import time
import sys
try:
    # Raspberry Pi Pico has no os module - all modules need to be installed
    # in the system path or else the path needs to be appended manually
    import os.path
    import os
    sys.path.append( os.path.join( os.path.dirname( __file__ ),
                                   os.pardir,
                                   'GPIO_AL' ) )
except ImportError:
    pass

from GPIO_AL import GPIOError, IOpin


class CCS811( object ):
    """!
    @brief Class to communicate with Cambridge CMOS Sensors' Ultra-Low Power
    Digital Gas Sensor for Monitoring Indoor Air Quality, CCS811, and read the
    CO<sub>2</sub> and tVOC (total Volatile Organic Compounds) values from this
    chip.

    The class makes the measured values available through the properties CO2 and
    tVOC which provide measured CO<sub>2</sub> levels in parts per million (
    ppm) and measured total Volatile Organic Compounds in parts per billion
    (ppb).

    Communication between a Raspberry Pi or Raspberry Pi Pico host and the
    CCS811 are handled via an I<sup>2</sup>C bus object of type I2Cbus from
    module GPIO_AL found here https://github.com/Ekkehard/RBPiGPIO_AL. For
    details on this class see the documentation of the module GPIO_AL.  Both
    packages must be installed as subdirectories of a common parent directory
    on Raspberry Pis running an Operating System; both GPIO_AL.py and CCS811.py
    must be installed on the flash of a Raspberry Pi Pico.

    There are two operation modes this class can run in: there is first the poll
    mode, where the calling program repeatedly checks for the availability of
    new data, which will then be read automatically as soon as it becomes
    available.  Secondly, there is the interrupt mode, where the sensor
    interrupts the host program when new data is ready which then immediately
    reads new measurements from the sensor without any interaction from the
    calling program.  Also, the sensor can be run powering its internal heater
    continuously, which results in a sampling interval of 1 second or in two
    different power saving modes with sampling intervals of 10 seconds and 60
    seconds, respectively.  In all cases, the calling program can always check
    the CO<sub>2</sub> and tVOC properties of this class to get the latest
    measurements available.  Moreover, the class provides a sleep() method to
    send the sensor to sleep to conserve even more power.  The wake() method
    must then be used to wake the sensor up again and resume operation.

    To obtain more accurate measurements, this class also accepts objects that
    encapsulate temperature and humidity sensors as arguments, the measurements
    of which will then be used to improve upon the accuracy of the air quality
    results.  Suitable classes must have properties "kelvin" and "humidity,"
    respectively to obtain the temperature in Kelvin and the humidity in percent.
    If appropriate classes are available but their properties are named
    differently, classes with properly named properties can be easily derived
    from them.  Of course, if a particular object has both properties, it can be
    passed as both arguments individually.  If no temperature object is
    supplied, 298.15 Kelvin (25&deg;C or 77&deg;F) is assumed; if no humidity
    object is supplied, 50% humidity is assumed.

    Note that a new sensor requires a 48 hour burn in. Once burned in, a sensor
    must run for 20 minutes after power on before readings are stable and
    considered valid.
    """

    # static public constants
    # -----------------------
    # possible values for measurement interval  are 1 s, 10 s, 60 s, and 250 ms
    # (s. data sheet p. 11)
    MEAS_INT_IDLE = 0
    MEAS_INT_1 = 1
    MEAS_INT_10 = 2
    MEAS_INT_60 = 3
    MEAS_INT_250MS = 4
    DEFAULT_MEAS_INT = MEAS_INT_1
    # ADDR is set by wiring ADDR Pin 1 to HIGH or LOW (s. data sheet p. 4)
    ADDR_LOW = 0x5A
    ADDR_HIGH = 0x5B
    # default I2C Address for CCS811 device
    DEFAULT_ADDR = ADDR_HIGH
    # number of attempts in dataReady() before we give up
    ATTEMPTS = 5

    # static private constants:
    # -------------------------
    # operation modes
    __POLL_MODE = 0
    __INTERRUPT_MODE = 1
    # CCS811 Hardware ID
    __HW_ID = 0x81
    # CCS881 registers (s. data sheet p. 17)
    __STATUS_REG = 0x00
    __MEAS_MODE_REG = 0x01
    __ALG_RESULT_DATA_REG = 0x02
    __RAW_DATA_REG = 0x03
    __ENV_DATA_REG = 0x05
    __NTC_REG = 0x06
    __THRESHOLDS_REG = 0x10
    __BASELINE_REG = 0x11
    __HW_ID_REG = 0x20
    __HW_VERSION_REG = 0x21
    __FW_BOOT_VERSION_REG = 0x23
    __FW_APP_VERSION_REG = 0x24
    __ERROR_ID_REG = 0xE0
    __APP_START_REG = 0xF4
    __SW_RESET_REG = 0xFF
    # status register bits (s. data sheet p. 18)
    __FW_MODE_BIT = 7
    __APP_ERASE_BIT = 6
    __APP_VERIFY_BIT = 5
    __APP_VALID_BIT = 4
    __DATA_READY_BIT = 3
    __ERROR_BIT = 0
    # measurement mode register bits (s. data sheet p. 19)
    __DRIVE_MODE_BIT = 4  # actually bits 4, 5, and 6 - this is the shift amount
    __INT_DATARDY_BIT = 3
    __INT_THRESH_BIT = 2


    def __init__( self,
                  i2cBus,
                  measInterval=DEFAULT_MEAS_INT,
                  interruptPin=None,
                  wakeupPin=None,
                  tempDevice=None,
                  humidDevice=None,
                  i2cAddress=DEFAULT_ADDR ):
        """!
        @brief Constructor for class CCS811.

        This constructor initializes the I2C library module as well as the host
        hardware and provides the abstraction from the Raspberry Pi module it is
        used on for other methods.
        @param i2cBus object of type I2Cbus from module GPIO_AL
        @param measInterval measurement interval, one of
               - CCS811.MEAS_INT_1 - measurement interval 1 s (default)
               - CCS811.MEAS_INT_10 - measurement every 10 seconds
               - CCS811.MEAS_INT_60 - measurement every 60 seconds
               - CCS811.MEAS_INT_250MS - for test purposes only (250 ms)
        @param interruptPin GPIO Pin number for interrupt mode operation -
               defaults to None, which means that interrupt functionality is
               disabled, which in turn results in poll mode operation
        @param wakeupPin GPIO Pin number for wakeup function - defaults to None,
               which means that wakeup functionality is disabled
        @param tempDevice object encapsulating a temperature measurement device
               with a "kelvin" property to get the temperature in Kelvin -
               default is None
        @param humidDevice object encapsulating a humidity measurement device
               with a "humidity" property to get the humidity in percent -
               default is None
        @param i2cAddress I2C address selected on CCS811, one of
               - ADDR_LOW (0x5A - Pin 1 wired LOW)
               - ADDR_HIGH (0x5B - Pin1 wired HIGH - default)
        """

        # do some minimal parameter checking
        if i2cAddress != self.ADDR_LOW and i2cAddress != self.ADDR_HIGH:
            raise ValueError( 'wrong i2cAddress specified for CCS811' )
        if measInterval < self.MEAS_INT_1 or measInterval > self.MEAS_INT_250MS:
            raise ValueError( 'wrong measInterval specified' )

        # we declare ALL class properties here

        # set (constant) private properties from parameters
        self.__i2cBus = i2cBus
        self.__i2cAddress = i2cAddress
        self.__tempDevice = tempDevice
        self.__humidDevice = humidDevice
        self.__measInterval = measInterval
        self.__attempts = self.ATTEMPTS
        if interruptPin is None:
            self.__mode = self.__POLL_MODE
        else:
            self.__mode = self.__INTERRUPT_MODE

        # initialize other (variable) private properties
        self.__stopped = True  # in case we get interrupts early (and we do...)
        self.__tVOC = None
        self.__CO2 = None
        self.__staleCO2 = True
        self.__staletVOC = True
        self.__open = False
        self.__errorCode = 0

        # wait time after power up (see data sheet p. 7)
        # chances are it took us a lot longer to get here, but just in case...
        time.sleep( 20.0E-03 )

        try:

            if interruptPin is not None:
                self.__interruptPin = IOpin( interruptPin,
                                             IOpin.INPUT_PULLUP,
                                             self.readData,
                                             IOpin.FALLING )
            else:
                self.__interruptPin = None

            if wakeupPin is not None:
                self.__wakeupPin = IOpin( wakeupPin,
                                          IOpin.OUTPUT )
                self.__wakeupPin.level = IOpin.LOW
            else:
                self.__wakeupPin = None

            # initialize the CCS811 chip
            # first perform a software reset to bring CCS811 in a known state
            try:
                self.reset()
            except:
                # but ignore errors - it might not even be a CCS811 after all
                pass

            # make sure there is a CCS811 at this address
            if self.__i2cBus.readByteReg( self.__i2cAddress,
                                          self.__HW_ID_REG ) != self.__HW_ID:
                raise ValueError( 'CCS811 not found at I2C address '
                                  '0x{0:02X}'.format( self.__i2cAddress ) )

            # We have the correct chip, so we consider it "opened," i.e. it can
            # and should be closed in case of an error when we have to leave
            self.__open = True

            # check if status is OK
            status = self.__i2cBus.readByteReg( self.__i2cAddress,
                                                self.__STATUS_REG )
            if (status & (1 << self.__ERROR_BIT)) != 0:
                self.__errorCode = \
                    self.__i2cBus.readByteReg( self.__i2cAddress,
                                               self.__ERROR_ID_REG )
                raise ValueError( 'Error at Startup: ' + self.errorText )
            if not status & (1 << self.__APP_VALID_BIT):
                raise ValueError( 'Error: CCS811 internal App not valid.' )

            # Put chip in start mode
            self.__i2cBus.writeByte( self.__i2cAddress, self.__APP_START_REG )
            # time after APP_START command - see data sheet p. 7
            time.sleep( 2.0E-03 )
            if self.errorCondition:
                # from here on, we need to reset the chip if anything fails
                # or else it hangs
                raise ValueError( 'Error at AppStart:' + self.errorText )

            # select user-supplied measuring interval
            self.__setModeReg( self.__mode, self.__measInterval )

            if self.errorCondition:
                raise ValueError( 'Error at setMode setting modeReg to {0}: '
                                  ''.format( self.__measInterval )
                                  + self.errorText )
        except (ValueError, GPIOError) as e:
            self.close()
            raise e

        if self.__interruptPin is not None:
            # this fake read request is needed to convince the CCS811 to release
            # the interrupt Pin and not pull it low all the time
            self.readData()

        # set stopped to False and let the measurements begin...
        self.__stopped = False

        return


    def __del__( self ):
        """!
        @brief Destructor - not supported by MicroPython.  Destructors have no
               use in production on an MCU, but during Unit Test they may be
               useful even on an MCU.
        """
        self.close()
        return


    def __str__( self ):
        """!
        @brief String representing initialization parameters used by this class.
        """
        measIntStr = ['', '1 s', '10 s', '60 s', '250 ms']
        return 'i2cBus: ({0}), meas. int. {1}, interrupt Pin: {2}, '\
               'wakeup Pin: {3} tempDevice: {4}, humidDevice: {5}, ' \
               'i2cAddress: 0x{6:02X}' \
               ''.format( self.__i2cBus,
                          measIntStr[self.__measInterval],
                          self.__interruptPin,
                          self.__wakeupPin,
                          self.__tempDevice,
                          self.__humidDevice,
                          self.__i2cAddress )


    def reset( self ):
        """!
        @brief Perform a software reset on the CCS811.
        """
        # s. data sheet p. 25
        self.__i2cBus.writeByte( self.__i2cAddress,
                                 self.__SW_RESET_REG,
                                 [0x11, 0xE5, 0x72, 0x8A] )
        time.sleep( 5.0E-03 )  # s. data sheet p. 7
        return


    def __enter__( self ):
        """!
        @brief Allow object of this class to operate under a context manager.
        """
        self.open()
        return self


    def __exit__( self, type, value, traceback ):
        """!
        @brief Allow object of this class to operate under a context manager.

        The exit method simply closes the CCS811 device.  If the with block
        is left "naturally" (without throwing an exception) all three
        parameters are None.
        @param type type of exception forcing control to leave with block
        @param value value of exception forcing control to leave with block
        @param traceback traceback information associated with this exception
        @return False indicating that exception has not been handled
        """
        self.close()
        return False


    def open( self ):
        """!
        @brief Just provide an open method that does nothing - the init method
        already opens the device.
        """
        return


    def close( self ):
        """!
        @brief Close the CCS811 device and Pins we may have opened.

        This method closes all open Pins, turns off interrupt generation and
        puts the CCS811 in boot mode.  Do NOT close the I2C bus as other devices
        may still use it - it ios a bus after all...
        """
        if self.__interruptPin is not None:
            try:
                self.__interruptPin.close()
            except:
                pass
            self.__interruptPin = None
        if self.__wakeupPin is not None:
            try:
                self.__wakeupPin.close()
            except:
                pass
            self.__wakeupPin = None
        if self.__open:
            try:
                self.reset()
            except:
                pass
            self.__open = False
        return


    def __setModeReg( self, mode, measInterval ):
        """!
        @brief Private method to set the internal CCS811 mode register, i.e. the
               interrupt mode flag and the measurement interval.
        @param mode one of __POLL_MODE or __INTERRUPT_MODE
        @param measInterval one of MEAS_INT_IDLE, MEAS_INT_1, MEAS_INT_10,
               MEAS_INT_60, or MEAS_INT_250MS
        """
        modeReg = measInterval << self.__DRIVE_MODE_BIT
        modeReg |= mode << self.__INT_DATARDY_BIT
        self.__i2cBus.writeByteReg( self.__i2cAddress,
                                    self.__MEAS_MODE_REG,
                                    modeReg )
        return


    def __toCCSfloat( self, number ):
        """!
        @brief Convert a regular float to the float format used by CCS.

        Cambridge CMOS Sensors uses a two-byte representation for a float in
        which the exponent is always zero (and not stored) and the significand
        is split in a portion before and one after the radix point.  The portion
        before the radix point is stored in the 7 most significant bits of the
        high byte of the CCS floating point representation as a regular binary
        integer, and the portion after the radix point in the least significant
        bit of the high byte and all 8 bits of the low byte as a 9 bit regular
        binary fraction.  CCS floating point format has no sign bit.  This means
        that the floating point numbers that can be represented in this format
        are in the interval [0., 128.) and this method therefore first clips its
        argument to that interval.  It then converts it to the CCS floating
        point format.  The result is returned as a 2-element list with the high
        byte in the first and the low byte in the second position.
        @param number floating point number to be converted
        @return list with high and low byte of converted number as elements
        """
        num = max( 0., min( number, 127.999 ) )
        inum = int( num )
        fraction = num - inum
        floatHigh = inum << 1
        bits = 0
        binFrac = 1.
        for i in range( 1, 10 ):
            binFrac = binFrac / 2.
            if fraction >= binFrac:
                fraction -= binFrac
                bits |= 1 << (9 - i)
        floatHigh |= bits >> 8
        floatLow = bits & 0xFF
        return [floatHigh, floatLow]


    @property
    def errorText( self ):
        """!
        @brief Works as a property that contains human-readable error text from
               errors indicated by the device.
        @return string with error description
        """
        message = ''
        if self.__errorCode == 0xFF:
            return 'All error code bits set'
        if self.__errorCode & (1 << 0):
            message += 'Write request to wrong register received, '
        if self.__errorCode & (1 << 1):
            message += 'Read request for wrong register received, '
        if self.__errorCode & (1 << 2):
            message += 'Invalid MeasMode received, '
        if self.__errorCode & (1 << 3):
            message += 'Sensor resistance reached max resistance, '
        if self.__errorCode & (1 << 4):
            message += 'Heater Current is not in range, '
        # s. data sheet p. 24
        if self.__errorCode & (1 << 5):
            message += 'Heater supply voltage is not applied correctly, '
        if self.__errorCode & (1 << 6):
            message += 'Could not read error registers, '
        if self.__errorCode & (1 << 7):
            message += 'Unspecified error, '

        return message[:-2]


    @property
    def errorCondition( self ):
        """!
        @brief Works as a property that indicates if an error condition
               exists on the device.

        As a side effect, this property method also sets the internal errorCode.
        @return True if there is an error condition - False otherwise
        """
        try:
            status = self.__i2cBus.readByteReg( self.__i2cAddress,
                                                self.__STATUS_REG )
            if (status & (1 << self.__ERROR_BIT)) == 0:
                self.__errorCode = 0
                return False
            self.__errorCode = self.__i2cBus.readByteReg( self.__i2cAddress,
                                                          self.__ERROR_ID_REG )
            if self.__errorCode == 0:
                # Weird - status has error flag set but error code reads 0...
                self.__errorCode = 1 << 7
            return True
        except Exception:
            # error reading status or error code itself
            self.__errorCode = 1 << 6
            return True


    def sleep( self ):
        """!
        @brief Send sensor to sleep.

        The method assures that a minimal sleep time if 20 &mu;s is kept by
        stalling for that time.
        """
        # disable chip clock
        self.__setModeReg( self.__POLL_MODE, self.MEAS_INT_IDLE )
        if self.__wakeupPin is None:
            raise ValueError( 'wakeup Pin not set' )
        # send chip to sleep
        self.__wakeupPin.level = IOpin.HIGH
        time.sleep( 20.0E-06 ) # s. data sheet p. 7
        self.__stopped = True
        return


    def wake( self ):
        """!
        @brief Wake sensor up.

        The method only returns after the sensor is ready for I<sup>2</sup>C
        traffic again, i.e. it will stall for 50 &mu;s after asserting the
        wakeup Pin low.
        """
        if self.__wakeupPin is None:
            raise ValueError( 'wakeup Pin not set' )
        # wake chip up
        self.__wakeupPin.level = IOpin.LOW
        time.sleep( 50.0E-06 ) # s. data sheet p. 7
        # re-enable chip clock
        self.__setModeReg( self.__mode, self.__measInterval )
        self.__stopped = False
        return


    @property
    def dataReady( self ):
        """!
        @brief Works as a property to check if new measurement data is
               available.

        As an internal side effect, this property method will immediately read
        and store the measurements internally and make them available for
        examination via the CO<sub>2</sub> and tVOC properties.

        The property is used only in poll mode.  In interrupt mode use the
        property staleMeasurement.
        @return True if measurement data are available - False otherwise
        """

        if self.__stopped:
            return False

        count = self.__attempts
        while count > 0:
            try:
                # we do that count times as it sometimes times out
                status = self.__i2cBus.readByteReg( self.__i2cAddress,
                                                    self.__STATUS_REG )
                break
            except OSError:
                count = count - 1
        if count <= 0:
            return False
        ready = (status & (1 << self.__DATA_READY_BIT)) != 0
        if ready:
            # if the device is ready, read its measurements
            self.readData()
        return ready


    def waitforData( self ):
        """!
        @brief Method blocks until new measurements are available, which will
        then be immediately read and stored internally and made available for
        examination via the CO<sub>2</sub> and tVOC properties.

        Blocking method for poll mode.
        """
        while not self.dataReady:
            pass
        return


    def readData( self, pin=None, level=None, tick=None ):
        """!
        @brief Method to read measurements from the CCS811 - used internally and
        as an ISR for which it needs to be public and have, depending on the
        target architecture, either a Pin object as the only argument on the
        Pico, or the Pin number, the voltage level at the Pin, and the number of
        microseconds since boot on the Raspberry Pi as its arguments; neither
        one of the arguments are used here except the Pin for debug output.
        When used internally, the method is called with no arguments.

        User code should not call this method.
        @param pin where interrupt happened - unused
        @param level - unused, supplied only at Raspberry Pi, 0 - change to low,
               1 - change to high 2 - no level change
        @param tick - unused, supplied only at Raspberry Pi, number of
               microseconds since boot - wraps around about every 72 minutes
        """
        # always read the data to make the method more versatile
        data = self.__i2cBus.readBlockReg( self.__i2cAddress,
                                           self.__ALG_RESULT_DATA_REG,
                                           4 )

        if self.__stopped:
            # if this method is called while stopped, it performs a "fake read"
            # to convince the CCS811 to release the interrupt Pin - also
            # interrupts from the CCS811 sometimes happen when they shouldn't...
            return


        try:
            self.__CO2 = (data[0] << 8) | data[1]
            if self.__CO2 < 400:
                # CO2 values below 400 ppm indicate invalid measurements
                self.__CO2 = None
                self.__tVOC = None
                self.__staleCO2 = True
                self.__staletVOC = True
            else:
                self.__tVOC = (data[2] << 8) | data[3]
                self.__staleCO2 = False
                self.__staletVOC = False
        except IndexError:
            # We ignore errors silently
            self.__CO2 = None
            self.__tVOC = None
            self.__staleCO2 = True
            self.__staletVOC = True

        if self.__tempDevice is not None or self.__humidDevice is not None:
            # write environmental data to the sensor
            if self.__tempDevice is not None:
                # temperature value is degrees in Celsius with 25 deg. offset
                # s. data sheet p. 21
                envList = self.__toCCSfloat( self.__tempDevice.kelvin
                                             - 273.15
                                             + 25.0 )
            else:
                envList = [0x64, 0x00]
            if self.__humidDevice is not None:
                envList.extend(
                    self.__toCCSfloat( self.__humidDevice.humidity ) )
            else:
                envList.extend( [0x64, 0x00] )
            self.__i2cBus.writeBlockReg( self.__i2cAddress,
                                         self.__ENV_DATA_REG,
                                         envList )

        return


    @property
    def CO2( self ):
        """!
        @brief Works as a property to get the last CO<sub>2</sub> measurement
               obtained from device in ppm.
        """
        self.__staleCO2 = True
        return self.__CO2


    @property
    def tVOC( self ):
        """!
        @brief Works as a property to get the last tVOC measurement obtained
               from device in ppb.
        """
        self.__staletVOC = True
        return self.__tVOC


    @property
    def staleMeasurements( self ):
        """!
        @brief Works as a property and returns True if there are any stale
               (already read) measurements.

        This is useful in interrupt mode when the calling program cannot know
        whether the internally stored data is the latest one.  This property can
        be used in interrupt mode in the (rare) cases when this becomes
        relevant.
        """
        return self.__staleCO2 | self.__staletVOC



#  main program - NO Unit Test - Unit Test is in separate file

if __name__ == "__main__":

    import sys

    def main():
        """!
        @brief Main program - to save some resources, we do not include the
               Unit Test here.
        """
        print( 'Please use included CCS811UnitTest.py for Unit Test' )
        return 0


    sys.exit( int( main() or 0 ) )
