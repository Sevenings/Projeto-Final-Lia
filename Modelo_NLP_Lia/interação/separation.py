import re

files = ["TEXTO_LISTAGEM", "TEXTO_AFIRMATIVO", "TEXTO_DESPEDIDA", "TEXTO_NEGATIVO", "TEXTO_CUMPRIMENTOS"]
folders = ["LIST", "BUY", "GOODBYE", "REFUND", "GREETING"]

for index, item in enumerate(files):
    inputFile = "TEXTOS_ORIGINAIS/LIMPOS/LIMPO_" + item.upper() + ".txt"
    outputFolder =  folders[index] + "/"

    with open(inputFile, 'r') as file:
        lines = file.readlines()

    newLines = list()

    for i in lines:
        newLines.append(re.sub(r'[!"#$%&()*+,-./:;<=>?@[\]^_`{|}~]', "", i))

    for index, line in enumerate(newLines):
        outputFile = outputFolder + f"texto{index}.txt"
        with open(outputFile, 'w') as fileOut:
            fileOut.write(line)