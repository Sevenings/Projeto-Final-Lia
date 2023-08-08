import re
with open("texto2200.txt") as file:
    lines = file.readlines()


for i, c in enumerate(lines):
    lines[i] = re.sub(r'\d+\.', '', c).strip()
    print(lines[i])

with open("txtOut.txt", 'w') as fileOut:
    for c in lines:
        fileOut.write(c + '\n')