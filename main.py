import steam.webauth as wa
import time
import re


items_for_search_CSGO = [
    {
        'name_item': 'Кейс «CS20»',
        'classid': 3564864937,
        'quantity': 0
    },
    {
        'name_item': 'Револьверный кейс',
        'classid': 1432174707,
        'quantity': 0
    },
    {
        'name_item': 'Кейс «Горизонт»',
        'classid': 2948874694,
        'quantity': 0
    },
    {
        'name_item': 'Хромированный кейс #3',
        'classid': 1690096482,
        'quantity': 0
    },
    {
        'name_item': 'Гамма-кейс #2',
        'classid': 1923037342,
        'quantity': 0
    },
    {
        'name_item': 'Кейс «Спектр 2»',
        'classid': 2521767801,
        'quantity': 0
    }
]

items_for_search_DOTA = [
    {
        'name_item': 'DPC 2022 Spring Lineage Treasure',
        'classid': 4796723480,
        'quantity': 0
    },
]

INVENTORY = {
    'CSGO': '730',
    'dota': '570',
    'TF2': '440'
}

accounts_with_drop = []


def sumCases(dict):
    results = 0

    for item in dict:
        results = results + item['quantity']
    return str(results)

# if INVENTORY['CSGO']:
with open("Accounts.txt", "r") as file:
    for line in file:
        loginAndPass = re.split(':', line.strip(), maxsplit=0)
        print(loginAndPass[0])
        
        user = wa.WebAuth(loginAndPass[0])
        user.cli_login(password=loginAndPass[1])
        request = user.session.get('https://steamcommunity.com/profiles/' + str(user.steam_id) + '/inventory/json/' + INVENTORY['CSGO'] + '/2', cookies=user.session.cookies, headers = {'User-agent': 'your bot 0.1'})

        if request.status_code == 200:
            rgInventory_fromJSON = request.json()['rgInventory']
            if len(rgInventory_fromJSON) != 0:
                while True:        
                    if request.json()['success']:
                        keys_fromJSON = request.json()['rgInventory'].keys()
                
                        for key in keys_fromJSON:
                            for item in items_for_search_CSGO:
                                if str(item['classid']) == str(rgInventory_fromJSON[key]['classid']):
                                    item['quantity'] = item['quantity'] + 1

                        accounts_with_drop.append(loginAndPass[0] + ':' + loginAndPass[1])
                        break
                    else:
                        time.sleep(25)
        else:
            print('WRONG', request.status_code)
        time.sleep(25)

with open('Accounts_with_drop.txt', "w") as file:
    file.writelines("%s\n" % line for line in accounts_with_drop)

with open('Statistic.txt', "w") as file:
    file.writelines('Общее кол-во кейсов: ' + sumCases(items_for_search_CSGO) + '\n\n')
    file.writelines('Кол-во кейсов каждого вида:\n\n')
    for item in items_for_search_CSGO:
        file.writelines(item['name_item'] + ': ' + str(item['quantity']) + '\n')

print(items_for_search_CSGO)