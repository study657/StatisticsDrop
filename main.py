import steam.webauth as wa
import datetime
import requests
import smtplib
import json
import time
import re
import os

current_time = str(datetime.datetime.today().strftime(f"%Y-%m-%d %H:%M:%S"))
work_time = str(datetime.datetime(2022, 6, 30, 0, 0, 0))
mistake_pass = 0
mistake_global = 0

with open('config.json') as json_file:
    dataJSON = json.load(json_file)
    items_for_search = dataJSON['items_for_search']


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
        global mistake_pass
        current_account_num = 1
        accounts_with_drop = []
        accounts_without_drop = []
        accounts_with_empty_inventory = []
        accounts_with_mistake_pass = []

        def getAllStatistic(accounts_with_mistake_pass, accounts_without_drop, accounts_with_empty_inventory, accounts_with_drop, folder=''):
            if len(accounts_with_mistake_pass) != 0:
                with open(folder + 'accounts_with_mistake_pass.txt', "w") as file:
                    file.writelines("%s\n" % line for line in accounts_with_mistake_pass)

            if len(accounts_without_drop) != 0:
                with open(folder + 'accounts_without_drop.txt', "w") as file:
                    file.writelines("%s\n" % line for line in accounts_without_drop)

            if len(accounts_with_empty_inventory) != 0:
                with open(folder + 'accounts_with_empty_inventory.txt', "w") as file:
                    file.writelines("%s\n" % line for line in accounts_with_empty_inventory)

            with open(folder + 'Accounts_with_drop.txt', "w") as file:
                file.writelines("%s\n" % line for line in accounts_with_drop)

            with open(folder + 'Statistic.txt', "w") as file:
                file.writelines('Общее кол-во кейсов: ' + sumCases(items_for_search) + '\n\n')
                file.writelines('Кол-во кейсов каждого вида:\n\n')
                for item in items_for_search:
                    file.writelines(item['name_item'] + ': ' + str(item['quantity']) + '\n')

        with open("Accounts.txt", "r") as file:
            for line in file:
                while True:
                    try:
                        loginAndPass = re.split(':', line.strip(), maxsplit=0)
                        print(loginAndPass[0], current_account_num)
                        
                        user = wa.WebAuth(loginAndPass[0])
                        try:
                            user.login(loginAndPass[1])
                            mistake_pass = 0
                        except (wa.CaptchaRequired, wa.LoginIncorrect) as exp:
                            if isinstance(exp, wa.LoginIncorrect):
                                if mistake_pass < 2:
                                    print('Неверный пароль. Засыпаю на 120 секунд!')
                                    mistake_pass = mistake_pass + 1
                                    time.sleep(120)
                                    continue
                                else:
                                    accounts_with_mistake_pass.append(loginAndPass[0] + ':' + loginAndPass[1])
                                    mistake_pass = 0
                                    current_account_num = current_account_num + 1
                                    print('С аккаунтом ' + loginAndPass[1] + ' какие-то проблемы, поэтому я его пропускаю!')
                                    time.sleep(10)
                                    break

                            if isinstance(exp, wa.CaptchaRequired):
                                print('Steam начал требовать captcha, поэтому засыпаю на 10 минут')
                                print(user.captcha_url)
                                time.sleep(600)
                                continue
                                # ask a human to solve captcha
                            # else:
                            #     captcha = None

                            # user.login(loginAndPass[1], captcha=captcha)

                        response = requests.get('https://steamcommunity.com/profiles/' + str(user.steam_id) + '/inventory/json/' + INVENTORY[GAME] + '/2', cookies=user.session.cookies, headers = {'User-agent': 'your bot 0.1'})

                        if response.status_code == 200: 
                            if response.json()['success']:
                                # try:
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
                                # except Exception as ex:
                                #     template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                                #     message = template.format(type(ex).__name__, ex.args)
                                #     print('У аккаунта ' + loginAndPass[0] + ' непредвиденная ошибка! ' + message)
                                #     time.sleep(25)
                            else:
                                current_account_num = current_account_num + 1
                                accounts_with_empty_inventory.append(loginAndPass[0] + ':' + loginAndPass[1])
                                print('У аккаунта ' + loginAndPass[0] + ' не создан инвентарь в Вашей игре!')
                                break
                        else:
                            print('Ошибка ', response.status_code + '. Засыпаю на 180 секунд!')
                            time.sleep(180)
                    except Exception as ex:
                        if mistake_global < 2:
                            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                            message = template.format(type(ex).__name__, ex.args)
                            mistake_global = mistake_global + 1
                            print('У аккаунта ' + loginAndPass[0] + ' ГЛОБАЛЬНАЯ ошибка! ' + message)
                            print('Засыпаю на 120 секунд')
                            time.sleep(120)
                            continue
                        else:
                            mistake_global = 0
                            os.mkdir("from_global_mistake")
                            getAllStatistic(accounts_with_mistake_pass, accounts_without_drop, accounts_with_empty_inventory, accounts_with_drop, folder='from_global_mistake/')
                            current_account_num = current_account_num + 1
                            with open('from_global_mistake/MISTAKE.txt', "w") as file:
                                file.writelines('Глобальная ошибка возникла на этом аккаунте: ' + loginAndPass[0] + ':' + loginAndPass[1] + '\n')
                            print('Пропускаю аккаунт ' + loginAndPass[0] + ' потому что с ним что-то не так!')
                            break
                time.sleep(25)

        os.mkdir("success_checking")
        getAllStatistic(accounts_with_mistake_pass, accounts_without_drop, accounts_with_empty_inventory, accounts_with_drop, folder='success_checking/')

        if dataJSON['send_mail'] == 1:
            smtpObj = smtplib.SMTP('smtp.mail.ru', 587)
            smtpObj.starttls()
            smtpObj.login(dataJSON['info_about_mail']['login'], dataJSON['info_about_mail']['pass'])

            message_info = 'Общее кол-во кейсов: ' + sumCases(items_for_search) + '\n\nКол-во кейсов каждого вида:\n\n'
            massage_about_cases = ''
            for item in items_for_search:
                massage_about_cases = massage_about_cases + item['name_item'] + ': ' + str(item['quantity']) + '\n'

            full_massage = message_info + massage_about_cases

            smtpObj.sendmail(dataJSON['info_about_mail']['login'], dataJSON['info_about_mail']['host_mail'], full_massage.encode(encoding='utf-8'))
            smtpObj.quit()
            print('Письмо отправлено на Вашу почту^_^')

        time_finish = str(datetime.datetime.today().strftime(f"%Y-%m-%d %H:%M:%S"))
        print('Программа завершила свою работу '  + str(time_finish) + '!')



    if dataJSON['your_items'] == 'no':
        if dataJSON['your_choose'] == 0:
            start_script('CS:GO', items_for_search_CSGO)
        elif dataJSON['your_choose'] == 1:
            start_script('Dota 2', items_for_search_DOTA)
        elif dataJSON['your_choose'] == 2:
            print('Данная опция реализованна только с Вашими личными предметами, поэтому заполните эти предметы в файле config.json^_^')
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