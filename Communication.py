from threading import Thread
from GammaDAC import DAC
import socket

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
READ_DAC_ALL        = 0x31
READ_CODE_ALL       = 0x32
READ_POWER          = 0x33
#---------------------------------

def verify_CheckSum(list_values):
    counter = 0
    for value in list_values:
        counter += value
    return ((counter - 256) == 0)

def include_CheckSum(list_values):
    counter = 0
    for values in list_values:
        counter += values
    cs = 256 - counter
    return(list_values + [cs])

def sendVariables(variableID, value, size):
    send_message = [0x00, variableID] + [c for c in struct.pack("!h", size)]
    if size == 1:
        send_message = send_message + [value]
    elif size == 2:
        send_message = send_message + [c for c in struct.pack("!h", value)]
    elif size == 4:
        send_message = send_message + [c for c in struct.pack("!I", value)]
    return "".join(map(chr, includeChecksum(send_message)))

class Communication:
    def __init__(self, port):
        self.port = port
        self.dac = DAC()

    def run(self):
        while(True):
            try:
                self.tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.tcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.tcp.bind(("", self.port))
                self.tcp.listen(1)

                sys.stdout.write("----- CountongPRU DAC control Socket -----")
                sys.stdout.write(time_string() + "TCP/IP Server on port " + str(self.port) + " started.\n")
                sys.stdout.flush()

                while (True):
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
                            if (verifyChecksum(message)):
                                # Reads Variable
                                if message[1] == 0x10:
                                    if message[4] == READ_DAC_CH:
                                        con.send(
                                            sendVariable(variableID=0x11, value=on_battery_status, size=0).encode(
                                                'latin-1'))

                                    elif message[4] == READ_CODE_CH:
                                        con.send(
                                            sendVariable(variableID=0x11, value=on_battery_status, size=0).encode(
                                                'latin-1'))
                                    elif message[4] == READ_POWER:
                                        con.send(
                                            sendVariable(variableID=0x11, value=on_battery_status, size=0).encode(
                                                'latin-1'))
                                # Reads Group
                                elif message[1] == 0x12:
                                    if   message[4] == READ_DAC_ALL:
                                        con.send(
                                            sendVariable(variableID=0x13, value=on_battery_status, size=0).encode(
                                                'latin-1'))
                                    elif message[4] == READ_CODE_ALL:
                                        con.send(
                                            sendVariable(variableID=0x13, value=on_battery_status, size=0).encode(
                                                'latin-1'))

                                # Writes Variable
                                elif message[1] == 0x20:
                                    if   message[4] == SET_POWER_CONFIG:
                                        dac.power(mode = message[5], DACs = message[6])
                                        con.send(sendVariable(variableID=0x20, value=0xe0, size=1).encode('latin-1'))

                                    elif message[4] == SET_DAC_CONFIG:
                                        dac.config(All_DACs = message[5], LD_EN = message[6], DACs = message[7])
                                        con.send(sendVariable(variableID=0x20, value=0xe0, size=1).encode('latin-1'))

                                    elif message[4] == SET_REFERENCE:
                                        dac.ref(power = message[5], mode = message[6])
                                        con.send(sendVariable(variableID=0x20, value=0xe0, size=1).encode('latin-1'))

                                    elif message[4] == WRITE_VALUE_CH:
                                        dac.writeValue(value = message[5], all_ch = False, ch = message[6])
                                        con.send(sendVariable(variableID=0x20, value=0xe0, size=1).encode('latin-1'))

                                    elif message[4] == WRITE_VOLTS_CH:
                                        dac.writeVolts(voltage = message[5], all_ch = False, ch = message[6])
                                        con.send(sendVariable(variableID=0x20, value=0xe0, size=1).encode('latin-1'))

                                    elif message[4] == CLEAR_DAC:
                                        dac.clear()
                                        con.send(sendVariable(variableID=0x20, value=0xe0, size=1).encode('latin-1'))

                                    elif message[4] == RESET_DAC:
                                        dac.reset()
                                        con.send(sendVariable(variableID=0x20, value=0xe0, size=1).encode('latin-1'))

                                # Writes Group
                                elif message[1] == 0x22:
                                    if message[4] == WRITE_VALUE_ALL:
                                        dac.writeValue(value = message[5])
                                        con.send(sendVariable(variableID=0x22, value=0xe0, size=1).encode('latin-1'))
                                    elif message[4] == WRITE_VOLTS_ALL:
                                        dac.writeValue(value = message[5])
                                        con.send(sendVariable(variableID=0x22, value=0xe0, size=1).encode('latin-1'))

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
                print(e)
                self.tcp.close()
                sys.stdout.write(time_string() + "Connection problem. TCP/IP server was closed.\n")
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