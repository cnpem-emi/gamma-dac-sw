#!/usr/bin/env python-sirius
import os, sys, ast
from pick import pick
#from GammaDAC import DAC

#dac = DAC()

def write_file( key, value, ch=''):
    written = read_file()
    with open("./.dac_config.txt", "w") as doc:
        if ch == '':
            written[key] = value
        else:
            written[key][ch] = float(value)
        doc.write(str(written))
        doc.close()


def read_file():
    with open("./.dac_config.txt", "r") as doc:
        written = ast.literal_eval(str(doc.read()))
        doc.close()
    return (written)


if __name__ == "__main__":

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
            write_file('Voltages', volts, index_escrever)

        elif index_escrever == 4:
            title_referencia = 'Tensão de referência'
            options_referencia = [' ', '2.5V', '2.048V', '4.1V']

            option_referencia, index_referencia = pick(options_referencia, title_referencia, indicator='=>',
                                                               default_index=1)

            if options_referencia != 0:
                # dac.ref(0, index_referencia)
                write_file("Referencia", option_referencia)

        else:
            sys.exit()
