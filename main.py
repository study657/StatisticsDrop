import steam.webauth as wa
import datetime
import requests
import json
import time
import re

current_time = str(datetime.datetime.today().strftime(f"%Y-%m-%d %H:%M:%S"))
work_time = str(datetime.datetime(2022, 6, 12, 0, 0, 0))


if current_time < work_time:
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
        'CS:GO': '730',
        'Dota 2': '570',
        'TF2': '440'
    }

    def sumCases(dict):
        results = 0

        for item in dict:
            results = results + item['quantity']
        return str(results)


    def start_script(GAME, items_for_search):
        current_account_num = 1
        accounts_with_drop = []
        accounts_without_drop = []
        accounts_with_empty_inventory = []

        with open("Accounts.txt", "r") as file:
            for line in file:
                while True:
                    loginAndPass = re.split(':', line.strip(), maxsplit=0)
                    print(loginAndPass[0], current_account_num)
                    
                    user = wa.WebAuth(loginAndPass[0])
                    session = user.cli_login(loginAndPass[1])

                    response = requests.get('https://steamcommunity.com/profiles/' + str(user.steam_id) + '/inventory/json/' + INVENTORY[GAME] + '/2', cookies=user.session.cookies, headers = {'User-agent': 'your bot 0.1'})

                    if response.status_code == 200:   
                        if response.json()['success']:
                            try:
                                rgInventory_fromJSON = response.json()['rgInventory']

                                if len(rgInventory_fromJSON) != 0:
                                    keys_fromJSON = response.json()['rgInventory'].keys()
                            
                                    for key in keys_fromJSON:
                                        for item in items_for_search:
                                            if str(item['classid']) == str(rgInventory_fromJSON[key]['classid']):
                                                item['quantity'] = item['quantity'] + 1

                                    current_account_num = current_account_num + 1
                                    accounts_with_drop.append(loginAndPass[0] + ':' + loginAndPass[1])
                                    break
                                else:
                                    current_account_num = current_account_num + 1
                                    accounts_without_drop.append(loginAndPass[0] + ':' + loginAndPass[1])
                                    print('У аккаунта ' + loginAndPass[0] + ' инвентарь пуст!')
                                    break
                            except:
                                print('У аккаунта ' + loginAndPass[0] + ' непредвиденная ошибка!')
                                time.sleep(25)
                        else:
                            current_account_num = current_account_num + 1
                            accounts_with_empty_inventory.append(loginAndPass[0] + ':' + loginAndPass[1])
                            print('У аккаунта ' + loginAndPass[0] + ' не создан инвентарь в Вашей игре!')
                            break
                    else:
                        print('Ошибка ', response.status_code + '. Засыпаю на 180 секунд!')
                        time.sleep(180)
                time.sleep(25)

        if len(accounts_without_drop) != 0:
            with open('accounts_without_drop.txt', "w") as file:
                file.writelines("%s\n" % line for line in accounts_without_drop)

        if len(accounts_with_empty_inventory) != 0:
            with open('accounts_with_empty_inventory.txt', "w") as file:
                file.writelines("%s\n" % line for line in accounts_with_empty_inventory)

        with open('Accounts_with_drop.txt', "w") as file:
            file.writelines("%s\n" % line for line in accounts_with_drop)

        with open('Statistic.txt', "w") as file:
            file.writelines('Общее кол-во кейсов: ' + sumCases(items_for_search) + '\n\n')
            file.writelines('Кол-во кейсов каждого вида:\n\n')
            for item in items_for_search:
                file.writelines(item['name_item'] + ': ' + str(item['quantity']) + '\n')

        print('Программа завершила свою работу!')


    with open('config.json') as json_file:
        dataJSON = json.load(json_file)
        items_for_search = dataJSON['items_for_search']

        if dataJSON['your_items'] == 'no':
            if dataJSON['your_choose'] == 0:
                start_script('CS:GO', items_for_search_CSGO)
            elif dataJSON['your_choose'] == 1:
                start_script('Dota 2', items_for_search_DOTA)
            elif dataJSON['your_choose'] == 2:
                print('Данная опция реализованна только с Вашими личными предметами, поэтому заколните эти предметы в файле config.json^_^')
        else:
            if dataJSON['your_choose'] == 0:
                start_script('CS:GO', items_for_search)
            elif dataJSON['your_choose'] == 1:
                start_script('Dota 2', items_for_search)
            elif dataJSON['your_choose'] == 2:
                start_script('TF2', items_for_search)
else:
    print('Неизвестная ошибка 404, обратитесь к создательнице программы!')
input()