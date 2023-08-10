files = ["listagem", "afirmativo"]

for c in files:
    inputFile = "TEXTOS_ORIGINAIS/LIMPO_TEXTO_" + c.upper() + ".txt"
    outputFolder = c + "/"

    with open(inputFile, 'r') as file:
        lines = file.readlines()

    for index, line in enumerate(lines):
        outputFile = outputFolder + f"texto{index}.txt"
        with open(outputFile, 'w') as fileOut:
            fileOut.write(line)