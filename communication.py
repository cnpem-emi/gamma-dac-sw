from threading import Thread
from GammaDAC import DAC
from time import sleep
import socket, datetime, sys, struct

#BSMPS Variables
#---------------------------------
SET_POWER_CONFIG    = 0x01
SET_DAC_CONFIG      = 0x02
SET_REFERENCE       = 0x03

WRITE_VALUE_CH      = 0x11
WRITE_VOLTS_CH      = 0x12
WRITE_VALUE_ALL     = 0x13
WRITE_VOLTS_ALL     = 0x14

CLEAR_DAC           = 0x21
RESET_DAC           = 0x22

READ_DAC_CH         = 0x31
READ_CODE_CH        = 0x32
READ_DAC_ALL        = 0x33
READ_CODE_ALL       = 0x34
READ_POWER          = 0x35
READ_REFERENCE      = 0X36
#---------------------------------

# Datetime string
def time_string():
    return(datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S.%f")[:-4] + " - ")

def verify_CheckSum(list_values):
    counter = 0

    for values in list_values:
        counter += values
    counter = (counter & 0xFF)
    return (counter == 0)

def include_CheckSum(list_values):
    counter = 0

    for values in list_values:
        counter += values
    counter = (counter & 0xFF)
    counter = (256 - counter) & 0xFF
    return list_values + [counter]


def sendVariables(variableID, value, size):
    send_message = [0x00, variableID] + [c for c in struct.pack("!h", size)]
    if size == 1:
        send_message = send_message + [value]
    elif size == 2:
        send_message = send_message + [c for c in struct.pack("!h", value)]
    elif size == 4:
        send_message = send_message + [c for c in struct.pack("!I", value)]
    elif size == 8:
        send_message = send_message + [c for c in struct.pack("!H", value)]
    return "".join(map(chr, include_CheckSum(send_message)))

class Communication(Thread):
    def __init__(self, port):
        Thread.__init__(self)
        self.port = port
        self.dac = DAC()

    def run(self):
        while(True):
            try:
                self.tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.tcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.tcp.bind(("", self.port))
                self.tcp.listen(1)

                sys.stdout.write("----- CountingPRU DAC control Socket -----\n")
                sys.stdout.write(time_string() + "TCP/IP Server on port " + str(self.port) + " started.\n")
                sys.stdout.flush()

                while(True):
                    sys.stdout.write(time_string() + "Waiting for connection.\n")
                    sys.stdout.flush()
                    con, client_info = self.tcp.accept()

                    # New connection
                    sys.stdout.write(
                        time_string() + "Connection accepted from " + client_info[0] + ":" + str(client_info[1]) + ".\n")
                    sys.stdout.flush()

                    while (True):
                        # Get message
                        message = [ord(i) for i in con.recv(100).decode('latin-1')]
                        if (message):
                            if (verify_CheckSum(message)):
                                # Reads Variable
                                if message[1] == 0x10:
                                    if message[4] == READ_DAC_CH:
                                        value = self.dac.read_dac(ch = message[5])
                                        sys.stdout.write(
                                            f"{time_string()}DAC read\nChannel: {message[5]}\nValue: {value}\n")
                                        sys.stdout.flush()
                                        con.send(
                                            sendVariables(variableID=0x11, value=int(value[1]*1000), size=8).encode(
                                                'latin-1'))

                                    elif message[4] == READ_CODE_CH:
                                        value = self.dac.read_code(ch = message[5])
                                        sys.stdout.write(
                                            f"{time_string()}CODE read\nChannel: {message[5]}\nValue: {value}\n")
                                        sys.stdout.flush()
                                        con.send(
                                            sendVariables(variableID=0x11, value=value<<4, size=8).encode(
                                                'latin-1'))
                                    elif message[4] == READ_POWER:
                                        con.send(
                                            sendVariables(variableID=0x11, value=self.dac.read_power(), size=1).encode(
                                                'latin-1'))

                                    elif message[4] == READ_REFERENCE:
                                        value = self.dac.read_Ref()
                                        sys.stdout.write(
                                            f"{time_string()}REFERENCE read \nValue: {value}\n")
                                        sys.stdout.flush()
                                        con.send(
                                            sendVariables(variableID=0x11, value=int(value*1000), size=4).encode(
                                                'latin-1'))

                                # Reads Group
                                #@TODO
                                elif message[1] == 0x12:
                                    if   message[4] == READ_DAC_ALL:
                                        con.send(
                                            sendVariables(variableID=0x13, value=on_battery_status, size=0).encode(
                                                'latin-1'))
                                    elif message[4] == READ_CODE_ALL:
                                        con.send(
                                            sendVariables(variableID=0x13, value=on_battery_status, size=0).encode(
                                                'latin-1'))

                                # Writes Variable
                                elif message[1] == 0x20:
                                    if   message[4] == SET_POWER_CONFIG:
                                        sys.stdout.write(
                                            f"{time_string()}Power DAC configuration\nMode: {message[5]}\nDACs: {message[6]}\n")
                                        sys.stdout.flush()
                                        self.dac.power(mode = message[5], DACs = message[6])
                                        #con.send(sendVariables(variableID=0x20, value=0xe0, size=1).encode('latin-1'))

                                    elif message[4] == SET_DAC_CONFIG:
                                        sys.stdout.write(
                                            f"{time_string()}Latch DAC configuration\nAll_DACS: {message[5]}\nLD_EN: {message[6]}\nDACs: {message[7]}\n")
                                        sys.stdout.flush()
                                        self.dac.config(All_DACs = message[5], LD_EN = message[6], DACs = message[7])
                                        #con.send(sendVariables(variableID=0x20, value=0xe0, size=1).encode('latin-1'))

                                    elif message[4] == SET_REFERENCE:
                                        voltages = {'00': None, '01': 2.5, '10': 2.048, '11': 4.1}
                                        sys.stdout.write(
                                            f"{time_string()}Voltage Referance set to {voltages[f'{message[5]:02b}']}\nPower mode: {message[6]}\n")
                                        sys.stdout.flush()
                                        self.dac.ref(power = message[6], mode = message[5])
                                        #con.send(sendVariables(variableID=0x20, value=0xe0, size=1).encode('latin-1'))

                                    elif message[4] == WRITE_VALUE_CH:
                                        sys.stdout.write(
                                            f"{time_string()}{message[5]} wrote at channel {message[6]}\n")
                                        sys.stdout.flush()
                                        self.dac.writeValue(value = message[5], all_ch = False, ch = message[6])
                                        #con.send(sendVariables(variableID=0x20, value=0xe0, size=1).encode('latin-1'))

                                    elif message[4] == WRITE_VOLTS_CH:
                                        value = ((message[6] << 8) + message[7])/10000
                                        sys.stdout.write(
                                            f"{time_string()}{value}V set to channel {message[5]}\n")
                                        sys.stdout.flush()
                                        self.dac.writeVolts(voltage = value, all_ch = False, ch = message[5])
                                        #con.send(sendVariables(variableID=0x20, value=0xe0, size=1).encode('latin-1'))

                                # Writes Group
                                elif message[1] == 0x22:
                                    if message[4] == WRITE_VALUE_ALL:
                                        sys.stdout.write(
                                            f"{time_string()}{message[5]} wrote at all channels\n")
                                        sys.stdout.flush()

                                        self.dac.writeValue(value = message[5])
                                        #con.send(sendVariables(variableID=0x22, value=0xe0, size=1).encode('latin-1'))

                                    elif message[4] == WRITE_VOLTS_ALL:
                                        value = (message[5]*256 + message[6]) / 10000
                                        sys.stdout.write(
                                            f"{time_string()}{value}V set to all channels\n")
                                        sys.stdout.flush()

                                        self.dac.writeVolts(voltage = value)
                                        #con.send(sendVariables(variableID=0x22, value=0xe0, size=1).encode('latin-1'))

                                    elif message[4] == CLEAR_DAC:
                                        sys.stdout.write(
                                            f"{time_string()}Cleaning DAC\n")
                                        sys.stdout.flush()
                                        self.dac.clear()
                                        #con.send(sendVariables(variableID=0x20, value=0xe0, size=1).encode('latin-1'))

                                    elif message[4] == RESET_DAC:
                                        sys.stdout.write(
                                            f"{time_string()}Resetting DAC\n")
                                        sys.stdout.flush()
                                        self.dac.reset()
                                        #con.send(sendVariables(variableID=0x20, value=0xe0, size=1).encode('latin-1'))

                            else:
                                sys.stdout.write(time_string() + "Unknown message: {}\n".format(message))
                                sys.stdout.flush()
                                continue

                        else:
                            # Disconnection
                            sys.stdout.write(
                                time_string() + "Client " + client_info[0] + ":" + str(client_info[1]) + " disconnected.\n")
                            sys.stdout.flush()
                            break

            except Exception as e:
                self.tcp.close()
                sys.stdout.write(time_string() + "Connection problem. TCP/IP server was closed.\n", e, "\n")
                sys.stdout.flush()
                sleep(5)

# --------------------- MAIN LOOP ---------------------
# -------------------- starts here --------------------
# Socket thread
net = Communication(5000)
net.daemon = True
net.start()

while(True):
    sleep(10)
