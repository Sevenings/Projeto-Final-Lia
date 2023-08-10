import re

files = ["TEXTO_LISTAGEM.txt", "TEXTO_AFIRMATIVO.txt"]

for c in files:
    input = "TEXTOS_ORIGINAIS/" + c
    output = "TEXTOS_ORIGINAIS/LIMPO_" + c

    with open(input, 'r') as file:
        lines = file.readlines()

    for i, c in enumerate(lines):
        lines[i] = re.sub(r'\d+\.', '', c).strip()
        print(lines[i])

    with open(output, 'w') as fileOut:
        for c in lines:
            fileOut.write(c + '\n')