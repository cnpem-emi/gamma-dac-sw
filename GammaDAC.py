import board, busio

class DAC():

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

    def power(self, mode, DACs):
        self.send_bytes([f'010000{mode:02b}', f'0000{DACs:04b}', '00000000'])

    def config(self, All_DACs, LD_EN, DACs):
        self.send_bytes([f'0110{All_DACs:01b}00{LD_EN:01b}', f'0000{DACs:04b}', '00000000'])

    def ref(self, power, mode):
        self.voltageREF = self.modeRef[f'{mode:02b}']
        self.send_bytes([f'01110{power:01b}{mode:02b}', '00000000', '00000000'])

    def writeValue(self, value, all_ch=True, ch=0):
        data = ['10000010']
        for i in value:
            data.append(f'{i:08b}')
        if not (all_ch):
            data[0] = f'0011{ch:04b}'

        self.send_bytes(data)

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

    def clear(self):
        self.send_bytes(['01010000'])

    def reset(self):
        self.send_bytes(['01010001'])

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

    def read_power(self):
        data = ['01000000']
        self.send_bytes(data=data)

        result = bytearray(2)
        self.i2c.readfrom_into(self.I2C_addr, result)
        return(int(result.hex(), 16))

    def read_Ref(self):
        data = ['11111111']
        self.send_bytes(data=data)

        result = bytearray(2)
        self.i2c.readfrom_into(self.I2C_addr, result)
        return(self.modeRef[f'{int(result.hex(), 16):016b}'[-2:]])