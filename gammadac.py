import board, busio

class DAC:

    def __init__(self, gammaAddr = 15):
        self.W_addr = int(f'0b001{gammaAddr:04b}0', 2)
        self.R_addr = int(f'0b001{gammaAddr:04b}1', 2)

        self.i2c = busio.I2C(board.SCL, board.SDA, 200000)

        self.I2C_addr = [int(i) for i in self.i2c.scan()][0]
        self.voltageREF = 0

        self.modeRef = {'00': None, '01': 2.5, '10': 2.048, '11': 4.1}

    def send_bytes(self, data='', readBack=False):
        command = []

        if not (readBack):
            for i in data:
                command.append(int(i, 2))

            self.i2c.writeto(self.I2C_addr, bytes(command), stop=False)

        else:
            result = bytearray(2)
            self.i2c.readfrom_into(self.I2C_addr, result)
            register_Value = int(result.hex()[:-1], 16)

            if self.voltageREF == 0:
                self.voltageREF = self.read_Ref()

            return([register_Value, (register_Value * self.voltageREF) / 4096])

    """
    Function power
    Sets the power mode of the selected DACs 
        
    This function receives two parameters:
     - Mode: Power Mode 
            00 = Normal
            01 = PD 1k Ohm
            10 = PD 100kOhm
            11 = PD Hi-Z
    
    - DACs: DACs selected with a 1 in the corresponding DACn bit are updated, DACs with a 0 in the corresponding DACn bit are not impacted.
            Range: 0x00 to 0x0f.
    """

    def power(self, mode, DACs):
        self.send_bytes([f'010000{mode:02b}', f'0000{DACs:04b}', '00000000'])

    """
        Function config
        Sets the DAC Latch Mode of the selected DACs.

        This function receives three parameters:
         - All_DACs: Set the configuration to all DACs.
                1 - Select all DACs.
                0 - Doesn't select.
    
        - LD_EN: Load DAC by hardware or software enable.
                0 - DAC latch is operational (LOAD and LDAC controlled).
                1 - DAC latch is transparent.
                
        - DACs: Only DACS with a 1 in the selection bit are updated by the command
                Range: 0x00 to 0x0f.
    """

    def config(self, All_DACs, LD_EN, DACs):
        self.send_bytes([f'0110{All_DACs:01b}00{LD_EN:01b}', f'0000{DACs:04b}', '00000000'])

    """
        Function ref
        Sets the reference operating mode.

        This function receives two parameters:
            - power: Defines when the internal reference will be powered.
                    0 - Internal reference is only powered if at least one DAC is powered
                    1 - Internal reference is always powered

            - mode: Sets the value of reference (internal or external).
                    00 - External reference.
                    01 - Internal reference of 2.5V.
                    10 - Internal reference of 2.048V.
                    11 - Internal reference of 4.1V.
    """

    def ref(self, power, mode):
        self.voltageREF = self.modeRef[f'{mode:02b}']
        self.send_bytes([f'01110{power:01b}{mode:02b}', '00000000', '00000000'])

    """
    Function WriteValue
    Sets the value of DACs.

    This function receives three parameters:
        - Value: List of two data bytes, using just three most significant nibbles.
                Range: [0x00, 0x00] to [0xff, 0xf0].
                
        - all_ch: Sets the value to all outputs.
        
        - ch: Set the value to a specific channel.
                Range: 0 to 3.
    """

    def writeValue(self, value, all_ch=True, ch=0):
        data = ['10000010']
        for i in value:
            data.append(f'{i:08b}')
        if not (all_ch):
            data[0] = f'0011{ch:04b}'

        self.send_bytes(data)

    """
    Function WriteVolts
    Sets a specific voltage value to DACs.

    This function receives three parameters:
        - Voltage: Voltage value to set on dac.
                Range: 0V to reference.  

        - all_ch: Sets the voltage to all outputs.

        - ch: Set the voltage to a specific channel.
                Range: 0 to 3.
    """

    def writeVolts(self, voltage, all_ch = False, ch =0):

        if self.voltageREF == 0:
            self.voltageREF = self.read_Ref()

        if voltage > self.voltageREF:
            voltage = self.voltageREF

        D = int((2**12)*voltage / self.voltageREF)

        data = ['10000010', f'{int(D//16):08b}', f'{int(D%16) << 4:08b}']

        if not(all_ch):
            data[0] = f'0011{ch:04b}'

        self.send_bytes(data)

    """
    Function clear
    Executes a software clear (all CODE and DAC registers cleared to their default values).
    """

    def clear(self):
        self.send_bytes(['01010000'])

    """
    Function reset
    Executes a software reset (all CODE, DAC, and control registers returned to their default values).
    """
    def reset(self):
        self.send_bytes(['01010001'])

    """
    Function read_dac
    Reads the dac value.

    This function receives two parameters:
        - readAll: Reads All DACs.  

        - ch: Reads a specific channel.
                Range: 0 to 3.
    
    Return: The function returns a list with two data, the value of dac register (0 to 4095) and this value converted to volts.
    """

    def read_dac(self, readAll = False,  ch = 0):
        if readAll:
            value_return = []
            data = ['10000001']
            self.send_bytes(data=data)
            for i in range(4):
                value_return.append(self.send_bytes(readBack=True)[1])
            return(value_return)

        else:
            data = [f'0011{ch:04b}']
            self.send_bytes(data=data)
            return(self.send_bytes(readBack=True))

    """
    Function read_code
    Reads the code register.

    This function receives two parameters:
        - readAll: Reads All DACs.  

        - ch: Reads a specific channel.
                Range: 0 to 3.

    Return: The function returns the value of code register (0 to 4095).
    """

    def read_code(self, readAll = False, ch = 0):
        if readAll:
            value_return = []
            data = ['10000000']
            self.send_bytes(data=data)
            for i in range(4):
                value_return.append(self.send_bytes(readBack=True)[0])
            return(value_return)

        else:
            data = [f'0000{ch:04b}']
            self.send_bytes(data=data)
            return(self.send_bytes(readBack=True)[0])

    """
    Function read_power
    Reads the state of DACs outputs.

    Return: Integer value output states.
            0 - Output ON.
            1 - Output OFF.
            Range: 0 to 15.
    """
    def read_power(self):
        data = ['01000000']
        self.send_bytes(data=data)

        result = bytearray(2)
        self.i2c.readfrom_into(self.I2C_addr, result)
        return(int(result.hex(), 16))

    """
    Function read_Ref
    Reads the value of reference.

    Return: Float value of DACs's reference.
    """
    def read_Ref(self):
        data = ['11111111']
        self.send_bytes(data=data)

        result = bytearray(2)
        self.i2c.readfrom_into(self.I2C_addr, result)
        return(self.modeRef[f'{int(result.hex(), 16):016b}'[-2:]])
