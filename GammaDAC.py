import os

class DAC:

    def __init__(self, i2cAddr, gammaAddr = 15):

        self.W_addr = int(f'0b001{gammaAddr:04b}0', 2)
        self.R_addr = int(f'0b001{gammaAddr:04b}1',2)

        self.I2C_addr = str(i2cAddr)
        self.voltageREF = 0

        self.modeRef = {'00': None, '01': 2.5, '10': 2, '11': 4.1}

    def power(self, mode, DACs):
        command = ''
        for i in [f'0b010000{mode:02b}', f'0b0000{DACs:04b}', '0b00000000']:
            command += f'{int(i, 2):#04x} '
        print("i2cset -y -r 2 {} {} 0x00 0x00 {} i".format(self.I2C_addr, f'{self.W_addr:#04x}', command))
        os.system("i2cset -y -r 2 {} {} 0x00 0x00 {} i".format(self.I2C_addr, f'{self.W_addr:#04x}', command))

    def config(self, All_DACs, LD_EN, DACs):
        command = ''
        for i in [f'0b0110{All_DACs}00{LD_EN}', f'0b0000{DACs:04b}', '0b00000000']:
            command += f'{int(i, 2):#04x} '
        print("i2cset -y -r 2 {} {} 0x00 0x00 {} i".format(self.I2C_addr, f'{self.W_addr:#04x}', command))
        os.system("i2cset -y -r 2 {} {} 0x00 0x00 {} i".format(self.I2C_addr, f'{self.W_addr:#04x}', command))

    def ref(self, power, mode):
        command = ''
        self.voltageREF = self.modeRef[f'{mode:02b}']
        for i in [f'0b01110{power}{mode:02b}', f'0b00000000', '0b00000000']:
            command += f'{int(i, 2):#04x} '

        print("i2cset -y -r 2 {} {} 0x00 0x00 {} i".format(self.I2C_addr, f'{self.W_addr:#04x}', command))
        os.system("i2cset -y -r 2 {} {} 0x00 0x00 {} i".format(self.I2C_addr, f'{self.W_addr:#04x}', command))

    def write_all(self, *value):
        command = ''
        for i in range(len(value[0])):
            command += f'{value[0][i]:#04x} '
        print("i2cset -y -r 2 {} {} 0x00 0x00 0x82 {} i".format(self.I2C_addr, f'{self.W_addr:#04x}', command))
        os.system("i2cset -y -r 2 {} {} 0x00 0x00 0x82 {} i".format(self.I2C_addr, f'{self.W_addr:#04x}', command))

    def writeVolts(self, voltage, all_ch = True):
        D = int((2**12)*voltage / self.voltageREF)

        if voltage > self.voltageREF:
            voltage = self.voltageREF

        command =  f'{int(D//16):#04x} ' + f'{int(D%16) << 4:#04x}'

        if all_ch:
            print("i2cset -y -r 2 {} {} 0x00 0x00 0x82 {} i".format(self.I2C_addr, f'{self.W_addr:#04x}', command))
            os.system("i2cset -y -r 2 {} {} 0x00 0x00 0x82 {} i".format(self.I2C_addr, f'{self.W_addr:#04x}', command))

        else:
            print("i2cset -y -r 2 {} {} 0x00 0x00 0x82 {} i".format(self.I2C_addr, f'{self.W_addr:#04x}', command))
            os.system("i2cset -y -r 2 {} {} 0x00 0x00 0x82 {} i".format(self.I2C_addr, f'{self.W_addr:#04x}', command))

    def clear(self):
        print("i2cset -y -r 2 {} {} 0x00 0x00 0x50 i".format(self.I2C_addr, f'{self.W_addr:#04x}'))
        os.system("i2cset -y -r 2 {} {} 0x00 0x00 0x50 i".format(self.I2C_addr, f'{self.W_addr:#04x}'))

    def reset(self):
        print("i2cset -y -r 2 {} {} 0x00 0x00 0x51 i".format(self.I2C_addr, f'{self.W_addr:#04x}'))
        os.system("i2cset -y -r 2 {} {} 0x00 0x00 0x51 i".format(self.I2C_addr, f'{self.W_addr:#04x}'))
