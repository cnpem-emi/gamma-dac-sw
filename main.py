import os, sys, ast, threading
from pick import pick
from pcaspy import SimpleServer, Driver
#from GammaDAC import DAC


def read_file():
    with open("./.dac_config.txt", "r") as doc:
        written = ast.literal_eval(str(doc.read()))
        doc.close()
    return(written)


#dac = DAC()

PVs = {}

for ch in range(4):
    PVs[f"GammaDAC:Channel{ch}"] = {'type':'float','unit':'Pulse/s', 'prec': 5}

# ---------------------------------------
# EPICS driver
class PSDriver(Driver):
    # class constructor
    def __init__(self):
        # call the superclass constructor
        Driver.__init__(self)

    # writing in PVs function
    def write(self, reason, value):
        self.setParam(reason, value)
        self.updatePVs()
        return (False)

class main(threading.Thread):

    def __init__(self) :
        threading.Thread.__init__(self)
        self.driver = PSDriver()

    def run(self):
        while(True):

            title = 'Seleção de operação'
            options = ['Leitura', 'Escrita']

            option_op, index_op = pick(options, title, indicator='=>', default_index=0)

            if index_op == 0:
                print(read_file())

            elif index_op == 1:
                title_escrever = 'Seleção de Escrita'
                options_escrever = ['Canal 0', 'Canal 1', 'Canal 2', 'Canal 3', 'Tensão de Referência', 'Sair']

                option_escrever, index_escrever = pick(options_escrever, title_escrever, indicator='=>', default_index=0)

                if index_escrever < 4:
                    os.system('clear')
                    volts = input("\nSelecione tensão para o canal {}: ".format(index_escrever))
                    # dac.writeVolts(float(volts), ch = index_escrever)
                    self.write_file('Voltages', volts, index_escrever)

                    self.driver.write(f"GammaDAC:Channel{index_escrever}", float(volts))

                elif index_escrever == 4:
                    title_referencia = 'Tensão de referência'
                    options_referencia = [' ', '2.5V', '2.048V', '4.1V']

                    option_referencia, index_referencia = pick(options_referencia, title_referencia, indicator='=>',
                                                               default_index=1)

                    if options_referencia != 0:
                        # dac.ref(0, index_referencia)
                        self.write_file("Referencia", option_referencia)

                else:
                    sys.exit()

    def write_file(self, key, value, ch = ''):
        written = read_file()
        with open("./.dac_config.txt", "w") as doc:
            if ch == '':
                written[key] = value
            else:
                written[key][ch] = float(value)
            doc.write(str(written))
            doc.close()

def thread_1():
    while (True):
        CAserver.process(0.1)


if __name__ == "__main__":
    server = SimpleServer()
    # start EPICS server
    CAserver = SimpleServer()
    CAserver.createPV("", PVs)
    global driver
    driver = PSDriver()

    t1 = threading.Thread(target=thread_1, args=[])
    t1.start()

    dacConfigs = main()
    dacConfigs.daemon = True
    dacConfigs.start()

else:
    configs = read_file()

    #dac.power(configs['Power_Mode'])
    #dac.config(configs['DAC_Config'])
    #dac.ref(configs['Referencia'])

    #for channel, voltage in enumerate(configs['Voltages']):
        #dac.writeVolts(voltage, ch = channel)
