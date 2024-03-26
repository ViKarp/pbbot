# TODO название бота, картинка бота
# TODO подгрузка табличек админам
# TODO проверка что есть админы в боте при регистрации и покупке. Функция админам "админы в сети"
# TODO в идеале сделать чтобы админы были и юзерами одновременно
# TODO переписать все на базы данных....

import config
import logging
import random as rd
import re
import smtplib
import traceback
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from platform import python_version
from datetime import date

import gspread
import pandas as pd
import math


def send_mail(email, key):
    sender = 'vikarp21@mail.ru'
    subject = 'PB_AMCP_bot'  # TODO возможно поменять название
    text = 'Код подтверждения авторизации: ' + str(key)
    html = '<html><head></head><body><p>' + text + '</p></body></html>'
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = 'PB AMCP SPBU <' + sender + '>'
    msg['To'] = email
    msg['Reply-To'] = sender
    msg['Return-Path'] = sender
    msg['X-Mailer'] = 'Python/' + (python_version())

    part_text = MIMEText(text, 'plain')
    part_html = MIMEText(html, 'html')

    msg.attach(part_text)
    msg.attach(part_html)

    mail = smtplib.SMTP_SSL(config.server, 465)
    mail.login(config.user, config.password)
    mail.sendmail(sender, email, msg.as_string())
    mail.quit()


class Shop:
    """Class of working with merch and points from event"""
    # Working dictionaries
    points_dict = dict()
    merch_dict = pd.DataFrame
    best_dict = dict()
    # Username
    user = ""

    def __init__(self, name, dict1="pointsfile.txt", dict2="merch.xlsx", dict3="bestfile.txt"):
        """Constructor to load dictionaries from files and apply username. Give a name"""

        self.user = name
        f = open(dict1, 'r')
        for line in f:
            try:
                surname, name, patronymic, points = line.rstrip("\n").split(',')
                self.points_dict[surname + ',' + name + ',' + patronymic] = float(points)
            except:
                surname, name, points = line.rstrip("\n").split(',')
                self.points_dict[surname + ',' + name] = float(points)
        f.close()
        self.merch_dict = pd.read_excel(dict2, header=0, index_col=0)
        f = open(dict3, 'r')
        for line in f:
            try:
                surname, name, patronymic, points = line.rstrip("\n").split(',')
                self.best_dict[surname + ',' + name + ',' + patronymic] = float(points)
            except:
                surname, name, points = line.rstrip("\n").split(',')
                self.best_dict[surname + ',' + name] = float(points)
        f.close()

    def update(self):
        """ Fun to update all dict"""
        dict1 = "pointsfile.txt"
        dict2 = "merch.xlsx"
        dict3 = "bestfile.txt"
        f = open(dict1, 'r')
        for line in f:
            try:
                surname, name, patronymic, points = line.rstrip("\n").split(',')
                self.points_dict[surname + ',' + name + ',' + patronymic] = float(points)
            except:
                surname, name, points = line.rstrip("\n").split(',')
                self.points_dict[surname + ',' + name] = float(points)

        f.close()
        self.merch_dict = pd.read_excel(dict2, header=0, index_col=0)
        f = open(dict3, 'r')
        for line in f:
            try:
                surname, name, patronymic, points = line.rstrip("\n").split(',')
                self.best_dict[surname + ',' + name + ',' + patronymic] = float(points)
            except:
                surname, name, points = line.rstrip("\n").split(',')
                self.best_dict[surname + ',' + name] = float(points)
        f.close()

    def save(self):
        """Fun to save all dict"""
        f = open('pointsfile.txt', 'w')
        for name in self.points_dict.keys():
            f.write(name + "," + str(self.points_dict[name]) + "\n")
        f.close()
        self.merch_dict.to_excel("merch.xlsx")
        f = open('bestfile.txt', 'w')
        for name in self.best_dict.keys():
            f.write(name + "," + str(self.best_dict[name]) + "\n")
        f.close()

    # Users functions
    def give_your_points(self):
        """Users fun to receive actual count of yours points"""
        self.update()
        if 4 < date.today().month <= 10:
            mero = "НПшку!"
        else:
            mero = "НФку!"
        return "В вашем кошельке " + str(self.points_dict[self.user]) + (" баллов. Пора придумывать мероприятия на "
                                                                         "следующую ") + mero

    def give_best(self):
        """Users fun to receive list of the most active people"""
        #TODO исправить отсутствие пробелов
        self.update()
        sorted_dict = sorted(self.best_dict.items(), key=lambda x: x[1], reverse=True)
        return sorted_dict[0][0] + "\n" + sorted_dict[1][0] + "\n" + sorted_dict[2][0] + "\n" + sorted_dict[3][
            0] + "\n" + sorted_dict[4][0] + "\n" + sorted_dict[5][0] + "\n" + sorted_dict[6][0] + "\n" + sorted_dict[7][
            0] + "\n" + sorted_dict[8][0] + "\n" + sorted_dict[9][0] + "\n"

    def give_merch(self):
        """Users fun to receive list of merch and prices"""
        pass

    def buy_merch(self, name):
        """Users fun to buy merch. Give a name of merch"""
        self.update()
        price = self.merch_dict["price"][name]
        if self.user not in self.points_dict.keys() or self.points_dict[self.user] < price:
            return 1
        self.points_dict[self.user] -= price
        self.merch_dict["count"][name] -= 1
        self.save()
        return 0


    # Admin functions
    def give_dict(self):
        """Admin fun to receive actual list of points"""
        self.update()
        return_object = ""
        for i, j in self.points_dict.items():
            return_object += i + " : " + str(j) + "\n"
        return return_object

    def add_table_event(self, path: str):
        self.update()
        """Admin fun to add new table from event. Give a path of table with format *.xlsx"""
        excel_reader = pd.ExcelFile(path)
        df_all = {sheet_name: excel_reader.parse(sheet_name) for sheet_name in excel_reader.sheet_names}
        tb = self.points_dict.keys()
        for df_name in df_all:
            df = pd.read_excel(path, sheet_name=df_name)
            size = df.shape[0]
            if "Главорг" in df.columns:
                for i in range(0, size):
                    if type(df["Главорг"][i]) == str:
                        name = df["Главорг"][i].replace("  ", " ").replace("\n", "")
                        name = ",".join(name.split(" "))
                        for snp in tb:
                            Flag = True
                            if name in snp:
                                self.points_dict[snp] += float(df["Итог"][i])
                                self.best_dict[snp] += float(df["Итог"][i])
                                Flag = False
                                break
                        if Flag:
                            self.points_dict[name] = float(df["Итог"][i])
                            self.best_dict[name] = float(df["Итог"][i])
            if "ФИО организатора" in df.columns:
                for i in range(0, size):
                    Flag = [True, True]
                    if type(df["ФИО организатора"][i]) == str:
                        name = ",".join(df["ФИО организатора"][i].split(" "))
                        for snp in tb:
                            if name in snp:
                                self.points_dict[snp] += float(df.iloc[i, 1])
                                self.best_dict[snp] += float(df.iloc[i, 1])
                                Flag[0] = False
                                break
                        if Flag[0]:
                            self.points_dict[name] = float(df.iloc[i, 1])
                            self.best_dict[name] = float(df.iloc[i, 1])
                    if type(df["ФИО волонтера"][i]) == str:
                        name1 = ",".join(df["ФИО волонтера"][i].split(" "))
                        for snp in tb:
                            if name1 in snp:
                                self.points_dict[snp] += float(df.iloc[i, 3])
                                self.best_dict[snp] += float(df.iloc[i, 3])
                                Flag[1] = False
                                break
                        if Flag[1]:
                            self.points_dict[name1] = float(df.iloc[i, 3])
                            self.best_dict[name1] = float(df.iloc[i, 3])
        excel_reader.close()
        self.save()

    def change_points(self, surname, points):
        """Admin fun to change of points from the organizer . Give a surname and num of points (ex. 15, 20, -50)"""
        self.update()
        tb = self.points_dict.keys()
        flag = True
        for snp in tb:
            if surname in snp:
                self.points_dict[snp] += float(points)
                self.best_dict[snp] += float(points)
                flag = False
                break
        if flag:
            self.points_dict[surname] = float(points)
            self.best_dict[surname] = float(points)
        self.save()

    def change_price(self, name, price):
        """Admin fun to change of price from the merch . Give a name of merch and price (ex. 15, 20)"""
        # TODO в папках поменять цену
        pass

    def add_merch(self, name, price):
        """Admin fun to add merch . Give a name of merch and price (ex. 15, 20)"""
        pass

    def delete_merch(self, name):
        """Admin fun to delete merch . Give a name of merch"""
        pass


class Account:
    """Class to authorization and registration user"""
    accounts = dict()

    def __init__(self):
        """Load accounts"""
        f = open('accounts.txt', 'r')
        for line in f:
            try:
                surname, name, patronymic, key = line.rstrip('\n').split(',')
                self.accounts[surname + ',' + name + ',' + patronymic] = key
            except:
                surname, name, key = line.rstrip("\n").split(',')
                self.accounts[surname + ',' + name] = key
        f.close()

    def save_accounts(self):
        f = open('accounts.txt', 'w')
        for name in self.accounts.keys():
            f.write(name + "," + self.accounts[name]+"\n")
        f.close()

    def registration(self, user):
        """User fun to give a key to user with st email. Give a name of user"""
        # key to authorization by user
        key = str(rd.randint(10000000, 99999999))

        # Tables of all student
        bak = pd.read_excel("bak.xlsx")
        mag = pd.read_excel("mag.xlsx")
        asp = pd.read_excel("asp.xlsx")
        patronymic = ""
        try:
            surname, name, patronymic = user.split(' ')
        except:
            surname, name = user.split(' ')
        # Find user email in all tables
        filtered_bak = bak[bak["Фамилия"] == surname]
        filtered_mag = mag[mag["Фамилия"] == surname]
        filtered_asp = asp[asp["Фамилия"] == surname]
        filtered_bak = filtered_bak[filtered_bak["Имя"] == name]
        filtered_mag = filtered_mag[filtered_mag["Имя"] == name]
        filtered_asp = filtered_asp[filtered_asp["Имя"] == name]
        if patronymic != "":
            filtered_bak = filtered_bak[filtered_bak["Отчество"] == patronymic]
            filtered_mag = filtered_mag[filtered_mag["Отчество"] == patronymic]
            filtered_asp = filtered_asp[filtered_asp["Отчество"] == patronymic]
        # else:
        #     filtered_bak = filtered_bak[filtered_bak["Отчество"] == ""]
        #     filtered_mag = filtered_mag[filtered_mag["Отчество"] == ""]
        #     filtered_asp = filtered_asp[filtered_asp["Отчество"] == ""]

        #res = pd.concat([filtered_bak, filtered_mag, filtered_asp], sort=False)
        res = filtered_bak
        if res.shape[0] == 1:
            recipients = res["Корпоративный email"].tolist()[0]
        elif res.shape[0] == 0:
            # TODO админ находит почту в тимс, находит почту и отправляет в бота почту
            if patronymic != "":
                self.accounts[surname + ',' + name + ',' + patronymic] = key
            else:
                self.accounts[surname + ',' + name] = key
            self.save_accounts()
            return key
        else:
            # TODO Как поступать при полном совпадении ФИО
            return 2
        # User mailing
        send_mail(recipients, key)

        # Change accounts and save to file
        if patronymic != "":
            self.accounts[surname + ',' + name + ',' + patronymic] = key
        else:
            self.accounts[surname + ',' + name] = key
        self.save_accounts()

        return 0

    def authorization(self, user, key):
        """User fun to apply authorization. Give a name and key"""
        try:
            surname, name, patronymic = user.split(' ')
        except:
            surname, name = user.split(' ')
            patronymic = ""
        if patronymic != "":
            if surname + ',' + name + ',' + patronymic in self.accounts and self.accounts[surname + ',' + name + ',' + patronymic] == key:
                # Username to create instance of Shop
                return surname + ',' + name + ',' + patronymic
            else:
                # Wrong authorization or user not registrate
                return 0
        else:
            if surname + ',' + name in self.accounts and self.accounts[surname + ',' + name] == key:
                # Username to create instance of Shop
                return surname + ',' + name
            else:
                # Wrong authorization or user not registrate
                return 0


class Logs:
    """Admin class to working with logs and version control"""
    # List of string logs
    logs = []

    def give_log(self):
        """Admin fun to give a log of changes. You receive a log using a file in format *.txt"""
        pass

    def save_log(self):
        """"""
        pass

    def change_back(self, log):
        pass
