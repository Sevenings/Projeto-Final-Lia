import json


class Item:
    def __init__(self, name, type, price, image_path):
        self.name = name
        self.type = type
        self.price = price
        self.image = None
        if image_path is not None:
            self.image = pygame.image.load(image_path)


def loadItens(path):
    file = open(path)
    json_data = json.loads(file.read())
    item_list = []
    for itemdata in json_data['itens']:
        name = itemdata['name']
        type = itemdata['type']
        price = itemdata['price']
        image_path = itemdata['image']
        item_list.append(Item(name, type, price, image_path))
    return item_list


item_list = loadItens('itens/itens.json')


for item in item_list:
    print(item.name)



# Algoritmo

entrada = input("Input entrada: ").lower()
saida = {}
pontuacao_maior = 0
maior = None


for item in item_list:
    referencia = item.name.lower();
    letras_comuns = 0
    tamanho = len(entrada)
    for i in range(tamanho):
        if referencia.startswith(entrada[:i+1]):
            letras_comuns += 1
        else:
            break
    pontuacao = letras_comuns/tamanho
    if pontuacao > pontuacao_maior:
        maior = item
        pontuacao_maior = pontuacao
    saida[referencia] = pontuacao

for key in saida:
    print(key, saida[key])
print("Resultado:",maior.name, pontuacao_maior)
