import re

files = ["TEXTO_LISTAGEM.txt", "TEXTO_AFIRMATIVO.txt", "TEXTO_DESPEDIDA.txt", "TEXTO_NEGATIVO.txt", "TEXTO_CUMPRIMENTOS.txt"]

for c in files:
    input = "TEXTOS_ORIGINAIS/" + c
    output = "TEXTOS_ORIGINAIS/LIMPOS/LIMPO_" + c

    with open(input, 'r') as file:
        lines = file.readlines()

    for i, c in enumerate(lines):
        lines[i] = re.sub(r'\d+\.', '', c).strip()
        print(lines[i])

    mySetLines = set(lines)

    with open(output, 'w') as fileOut:
        for c in mySetLines:
            fileOut.write(c + '\n')