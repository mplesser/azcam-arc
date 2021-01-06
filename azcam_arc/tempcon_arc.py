"""
Contains the base TempConArc class.
"""

import math

import azcam
from azcam.tempcon import TempCon


class TempConArc(TempCon):
    """
    Defines the ARC temperature control class.
    This is used for Gen1, Gen2, and Gen3 ARC controllers.
    """

    def __init__(self, obj_id="tempcon", name="tempcon_arc"):

        super().__init__(obj_id, name)

        self.num_temp_reads = 5
        self.control_temperature = +25.0

        self.last_temps = 3 * [self.bad_temp_value]  # last readings for during exposure

        return

    def set_control_temperature(self, temperature=None, temperature_id=0):
        """
        Set controller/detector control temperature.
        Ignored if no utlity board is installed.
        Temperature is temperature to set in Celsius.
        """

        if not self.enabled:
            azcam.AzcamWarning(f"{self.name} is not enabled")
            return

        TEMPSET = 0x01C

        # ignore if no utlity board
        if not azcam.api.controller.utility_board_installed:
            return

        # ignore if controller is not reset
        if not azcam.api.controller.is_reset:
            return

        if temperature is None:
            temperature = self.control_temperature
        else:
            self.control_temperature = float(temperature)

        temperature_id = int(temperature_id)
        self.control_temperature_number = temperature_id
        counts = self.convert_temp_to_counts(2, self.control_temperature)
        azcam.api.controller.write_memory(
            "Y", azcam.api.controller.UTILITYBOARD, TEMPSET, int(counts)
        )

        return

    def get_temperatures(self):
        """
        Updates and returns current CAMTEMP, DEWTEMP, and DIODETEMP temperatures from utility board.
        -999.9 value updated if no utility board is installed or other any error occurs.
        Returns [Temp1,Temp2,Temp3] where Temps are temperaturess in Celsius.
        """

        # return bad_temp_value if no utlity board
        if not azcam.api.controller.utility_board_installed:
            return 3 * [self.bad_temp_value]

        # Don't read hardware while exposure is in progess, return last values read
        flag = azcam.api.exposure.exposure_flag
        if flag != azcam.api.exposure.exposureflags["NONE"]:
            return self.last_temps

        camtemp = self.get_temperature(0)

        dewtemp = self.get_temperature(1)

        diodetemp = self.get_temperature(2)

        if self.log_temps:
            azcam.log(f"templog: {camtemp} {dewtemp} {diodetemp} -999.9", logconsole=0)

        return [camtemp, dewtemp, diodetemp]

    def get_temperature(self, temperature_id=0):
        """
        Read a utlity board temperature.
        TemperaureID's are:
        0 => CAMTEMP
        1 => DEWTEMP
        2 => DIODETEMP
        """

        if not self.enabled:
            # azcam.AzcamWarning("Tempcon not enabled")
            return -999.9

        if not self.initialized:
            # azcam.AzcamWarning("Tempcon not initialized")
            return -999.9

        if not azcam.api.controller.utility_board_installed:
            return self.bad_temp_value

        if not azcam.api.controller.is_reset:
            return self.bad_temp_value

        # define DSP address
        if temperature_id == 0:
            Address = 13
        elif temperature_id == 1:
            Address = 14
        elif temperature_id == 2:
            Address = 12
        else:
            return "ERROR bad TemperatureID"

        # Don't read hardware while exposure is in progess
        flag = azcam.api.exposure.exposure_flag
        if flag != azcam.api.exposure.exposureflags["NONE"]:
            return self.last_temps[temperature_id]

        # read temperature
        cmd = "RDM"
        avecount = 0
        try:
            for _ in range(self.num_temp_reads):
                reply = azcam.api.controller.board_command(
                    cmd, azcam.api.controller.UTILITYBOARD, 0x400000 | Address
                )  # Y space
                counts = int(reply)
                avecount += counts
        except ValueError:
            raise azcam.AzcamError("could not read temperature")
        counts = avecount / self.num_temp_reads

        # convert from counts to Celsius
        temp = self.convert_counts_to_temp(
            self.temperature_cals[temperature_id], counts
        )

        temp = self.apply_corrections(temp, temperature_id)

        # make nice float
        temp = float(int(temp * 1000.0) / 1000.0)

        # use some limits
        if temp > 100.0 or temp < -300.0:
            temp = -999.9

        # save temp
        self.last_temps[temperature_id] = temp

        return temp

    def convert_counts_to_temp(self, calflag: int, counts: int) -> float:
        """
        Convert counts (DN) to degrees Celsius.
        Uses Chebyechev polynomial.

        :param calflag: calibration curve to use
        :param counts: value to convert

          * 0 => convert DT670  counts to degrees C
          * 1 => convert AD590  counts to degrees C
          * 2 => convert 1N4148 counts to degrees C
          * 3 => convert 1N914  counts to degrees C
        """

        MAXBOUND = 11
        B = [
            82.017868,
            -59.064244,
            -1.356615,
            1.055396,
            0.837341,
            0.431875,
            0.440840,
            -0.061588,
            0.209414,
            -0.120882,
            0.055734,
            -0.035974,
        ]
        C = [
            306.592351,
            -205.393808,
            -4.695680,
            -2.031603,
            -0.071792,
            -0.437682,
            0.176352,
            -0.182516,
            0.064687,
            -0.027019,
            0.010019,
        ]
        A = MAXBOUND * [0]
        MAXDIODE = 19
        DC = [
            2600,
            2728,
            2823,
            2966,
            3003,
            3009,
            3070,
            3107,
            3118,
            3139,
            3166,
            3183,
            3217,
            3256,
            3269,
            3329,
            3357,
            3379,
            3417,
        ]  # diode count array
        DT = [
            311,
            277,
            250,
            210,
            200,
            190,
            180,
            170,
            160,
            155,
            150,
            147,
            137,
            127,
            117,
            107,
            97,
            87,
            77,
        ]  # diode temp array

        NOAO = [471.3507, -581.5675, 558.4024, -786.8676, 628.3720, -219.7995]

        VMIN = 0.07000
        VMAX = 1.122751
        VOLTMAX = 3.0
        VOLTMIN = -3.0
        COUNTMAX = 4095
        COUNTMIN = 0
        GAIN = 2.0  # this is the gain before ADC

        if calflag == 0:  # DT670 counts to Celsius

            # convert counts to voltage
            voltage = (
                ((VOLTMAX - VOLTMIN) / (COUNTMAX - COUNTMIN + 1))
                * (counts - 2048)
                / GAIN
            )

            if voltage > VMAX:
                temp = -999.9
                return temp
            elif voltage < VMIN:
                temp = +999.9
                return temp

            if voltage >= 0.986974:
                for i in range(MAXBOUND):  # 24.5 to 100.0 K
                    A[i] = B[i]
                    zl = 0.909416
                    zu = 1.122751
            else:
                for i in range(MAXBOUND):  # 100 to 500k
                    A[i] = C[i]
                    zl = 0.07000
                    zu = 0.99799

            x = ((voltage - zl) - (zu - voltage)) / (zu - zl)
            temp = 0.0
            for i in range(MAXBOUND):
                temp += A[i] * math.cos(i * math.acos(x))
            temp -= 273.13  # K to C
            return temp

        elif calflag == 1:  # AD590 case counts to Celsius
            temp = 0.16012 * counts - 599.5
            return temp

        elif calflag == 2:  # 1N4148 diode counts to Celsius
            if counts < DC[0]:
                temp = +999.9
                return temp
            elif counts > DC[MAXDIODE - 1]:
                temp = -999.9
                return temp

            for i in range(MAXDIODE):
                if counts < DC[i]:
                    inc = ((DT[i - 1] - DT[i]) / (DC[i - 1] - DC[i])) * (counts - DC[i])
                    temp = DT[i] + inc - 273.13  # simple for now
                    break
            return temp

        elif calflag == 3:  # 1N914 diode voltage to Celsius

            # convert counts to voltage
            voltage = (
                ((VOLTMAX - VOLTMIN) / (COUNTMAX - COUNTMIN + 1))
                * (counts - 2048)
                / GAIN
            )

            temp = (
                NOAO[0]
                + voltage * NOAO[1]
                + pow(voltage, 2) * NOAO[2]
                + pow(voltage, 3) * NOAO[3]
                + pow(voltage, 4) * NOAO[4]
                + pow(voltage, 5) * NOAO[5]
                - 273.13
            )
            return temp

        else:
            raise azcam.AzcamError("ConvertCountsToTemp", "invalid calflag")

    def convert_temp_to_counts(self, calflag: int, temperature: float) -> float:
        """
        Convert degrees Celsius to counts.

        :param calflag: calibration flag to use
        :param temperature: temperature in C to convert
        """

        NOAOINV = [6.00e-09, -3.50e-06, -0.0021, 1.1616]  # inverse of NOAO

        if calflag == 2:  # 1N914 diode case Celsius to counts
            VOLTMAX = 3.0
            VOLTMIN = -3.0
            COUNTMAX = 4095
            COUNTMIN = 0
            GAIN = 2.0  # this is the gain before ADC

            inp = temperature + 273.13  # C to K
            voltage = (
                NOAOINV[3]
                + inp * NOAOINV[2]
                + pow(inp, 2) * NOAOINV[1]
                + pow(inp, 3) * NOAOINV[0]
            )
            counts = ((COUNTMAX - COUNTMIN + 1) / (VOLTMAX - VOLTMIN)) * (
                voltage * GAIN
            ) + 2048

        else:
            raise azcam.AzcamError("convert_temp_to_counts invalid calflag")

        return counts
