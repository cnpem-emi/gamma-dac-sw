import board
import busio

class DAC:

    def __init__(self, gammaAddr = 15):

        self.W_addr = int(f'0b001{gammaAddr:04b}0', 2)
        self.R_addr = int(f'0b001{gammaAddr:04b}1',2)

        self.i2c = busio.I2C(board.SCL, board.SDA, 200000)

        self.I2C_addr = [int(i) for i in self.i2c.scan()][0]
        self.voltageREF = 0

        self.modeRef = {'00': None, '01': 2.5, '10': 2, '11': 4.1}

    def send_bytes(self, *data):
        command = []
        for i in data[0]:
            command.append(int(i, 2))

        self.i2c.writeto(self.I2C_addr, bytes(command), stop=False)

    def power(self, mode, DACs):
        self.send_bytes([f'010000{mode:02b}', f'0000{DACs:04b}', '00000000'])

    def config(self, All_DACs, LD_EN, DACs):
        self.send_bytes([f'0110{All_DACs}00{LD_EN}', f'0000{DACs:04b}', '00000000'])

    def ref(self, power, mode):
        self.voltageREF = self.modeRef[f'{mode:02b}']
        self.send_bytes([f'01110{power}{mode:02b}', '00000000', '00000000'])

    def write_all(self, *value):
        data = ['10000010']
        for i in range(len(value[0])):
            data.append(f'{value[0][i]:08b}')

        self.send_bytes(data)

    def writeVolts(self, voltage, all_ch = True, ch =0):
        D = int((2**12)*voltage / self.voltageREF)

        if voltage > self.voltageREF:
            voltage = self.voltageREF

        data = ['10000010', f'{int(D//16):08b}', f'{int(D%16) << 4:08b}']

        if not(all_ch):
            data[0] = f'0011{ch:04b}'

        self.send_bytes(data)