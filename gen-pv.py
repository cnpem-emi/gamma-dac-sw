import threading, time, ast
from gammadac import DAC
from pcaspy  import Driver, SimpleServer

PVs = {}

for ch in range(4):
    PVs[f"GammaDAC:Channel{ch}"] = {'type':'float','unit':'Volts', 'prec': 5}

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

    def __init__(self):
        threading.Thread.__init__(self)
        self.dac = DAC()
        
        self.read_file()
        self.references_value = {" ":0, "2.5V":1, "2.048V":2, "4.1V":3}

        self.dac.power(self.written['Power_Mode'], 0x0f)
        self.dac.config(self.written['DAC_Config'][0], self.written['DAC_Config'][1], self.written['DAC_Config'][2])
        self.dac.ref(0, self.references_value[self.written['Referencia']])

        for channel, voltage in enumerate(self.written['Voltages']):
            self.dac.writeVolts(voltage, ch = channel)

    def run(self):
        while(True):
            self.read_file()

            for ch in range(4):
                driver.write(f"GammaDAC:Channel{ch}", self.written['Voltages'][ch])

            time.sleep(30)

    def read_file(self):
        with open("./.dac-config.txt", "r") as doc:
            self.written = ast.literal_eval(str(doc.read()))
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

    geraPV = main()
    geraPV.daemon = True
    geraPV.start()

    t1 = threading.Thread(target=thread_1, args=[], daemon=True )
    t1.start()

    while True:
        time.sleep(10)
