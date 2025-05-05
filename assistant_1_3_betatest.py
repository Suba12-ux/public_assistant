import tkinter as tk
from tkinter import messagebox
from functools import lru_cache
from collections import namedtuple
import pathlib, os
from funk_assistent import *
from datetime import datetime, timedelta, date
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time, csv

class Profil:
    def __init__(self):
        self.ulk = None 
        self.login = None 
        self.password = None 
    #    self.url = None

    @staticmethod
    def encryption(text, ulk):
        if not ulk:
            raise ValueError("Ключ не должен быть пустым!")

        encrypted_text = ""
        ulk_length = len(ulk)
        for i, char in enumerate(text):
            shift = ord(ulk[i % ulk_length])
            encrypted_char = chr(ord(char) + shift)
            encrypted_text += encrypted_char

        return encrypted_text

    @staticmethod
    def decryption(encrypted_text, ulk):
        if not ulk:
            raise ValueError("Ключ не должен быть пустым!")

        decrypted_text = ""
        ulk_length = len(ulk)
        for i, char in enumerate(encrypted_text):
            shift = ord(ulk[i % ulk_length])
            decrypted_char = chr(ord(char) - shift)
            decrypted_text += decrypted_char

        return decrypted_text

    def find_profile(self, login, key): 
        self.ulk = key
        self.login = login
        lib_path = 'data_profiles.csv'
        
        if not os.path.exists(lib_path): 
            with open(lib_path, 'w+') as path_:
                writer = csv.writer(path_, delimiter=';')
                writer.writerow(['login','password'])

        with open(lib_path, 'r+', encoding='utf-8') as prof:
            sl = csv.DictReader(prof, delimiter=';', quotechar='"')
            exod = Profil.encryption(self.login, self.ulk)
            for i in sl:
                if exod == i['login']:  
                    self.login = Profil.decryption(i['login'], self.ulk)
                    #self.login = i['login']
                    self.password = Profil.decryption(i['password'], self.ulk)
                    #self.password = i['password']
                    messagebox.showinfo("Success", "Профиль найден.")
                    return self.login, self.password 

        messagebox.showwarning("Failure", "Профиль не найден.") 
        return False
        

    def creating_profile(self, key, login, password):
        self.ulk = key
        self.login = login
        self.password = password

        lib_path = 'data_profiles.csv'
        if not os.path.exists(lib_path): 
            with open(lib_path, 'w+') as path_:
                writer = csv.writer(path_, delimiter=';')
                writer.writerow(['login','password'])

        with open(lib_path, 'a', encoding='utf-8') as prof:  
            writer = csv.writer(prof, delimiter=';')
            
            writer.writerow([
                Profil.encryption(self.login, self.ulk),
                Profil.encryption(self.password, self.ulk)
            ])
        messagebox.showinfo("Success", "Профиль создан.")

class URL_request:
    def __init__(self, login, password):
        self.login = login
        self.password = password

    def open_downloading_window(self):
        reg_window2 = tk.Toplevel()
        reg_window2.geometry("200x100")
        reg_window2.title("URL_запрос")

        tk.Label(reg_window2, text="URL_адрес:").pack()
        URL_entry = tk.Entry(reg_window2)
        URL_entry.pack()

        tk.Button(
            reg_window2,
            text="ЗАПУСК_WEB_драйвера", 
            command = lambda:[ self.main_cycle(str(URL_entry.get())), reg_window2.destroy()]).pack()

    def main_cycle(self, url):
        #url, login, password = url, self.login, self.password
        try:
            students, name_group = zapros_url(url, str(self.login), str(self.password))
            if students == None or name_group == None:
                    raise ValueError ("Недостаточно данных из URL.")
            txt = gender(students)
            print('После гендера')
            print(*txt, sep='\n')

            global_obj = tuple(map(lambda a: a._replace(data_numder=URL_record_data(a.login_student, a.password_student)) if a.visits >= 2 else a, txt))
        
            way = pathlib.Path('os_group.txt').resolve()
            if not os.path.exists(way): 
                with open(way, 'w') as path_writer:
                    print('name/surname', 'characteristic', file=path_writer)
            with open(way, 'a') as path_writer:
                print(f"Группа: {date.today()- timedelta(3)}", '\t'+str(*name_group), file=path_writer)
                txt = creating_templates(global_obj)
                print('после темплета')
                print(*txt, sep='\n')
                for k in txt:
                    print(k.name + ' ' + k.surname, k.feedback, file=path_writer)
                print('****************************************************************************', file=path_writer)
                print('Данные сохранены в текстовый файл os_group', f'Путь сохронения: {way}', sep='\n')
        except ValueError: 
            print('Не найдены нужные значения.\nУбедитесь в правельности ссылки')

class registration(Profil):
    def __init__(self, ulk):
        super().__init__()
        self.ulk = ulk
        self.profilAdd = registration.open_registration_window(self)

    def open_registration_window(self):
        reg_window = tk.Toplevel()
        reg_window.title("Зарегистрировать профиль")

        tk.Label(reg_window, text="Логин:").pack()
        login_entry = tk.Entry(reg_window)
        login_entry.pack()

        tk.Label(reg_window, text="Пароль:").pack()
        password_entry = tk.Entry(reg_window, show='*')
        password_entry.pack()

        tk.Button(
            reg_window, 
            text="Создать профиль", 
            command=lambda: [
            self.create_new_profile(self.ulk, login_entry.get(), password_entry.get()),  # Создаем профиль
            reg_window.destroy()  # Закрываем окно после создания профиля
                ]).pack()

    def create_new_profile(self, ulk, login, password):
        super().creating_profile( self.ulk, login, password)
        print(f"Новый профиль. \n\tЛогин: {self.login}, \n\tПароль: {self.password}")

class ProfilApp:
    def __init__(self, master):
        self.master = master


        self.master.geometry("200x100")
        master.title("Profile Management")

        
        self.profil = Profil()

        #self.registration = registration(self.key_entry.get())

        self.label1 = tk.Label(master, text="Ключ:")
        self.label1.pack()

        self.key_entry = tk.Entry(master)
        self.key_entry.pack()

        self.label2 = tk.Label(master, text="Логин:")
        self.label2.pack()

        self.login_entry = tk.Entry(master)
        self.login_entry.pack()

        self.find_button = tk.Button(master, text="Найти профиль", command=self.find_profile_in_data)
        self.find_button.pack()

        #self.request_stage = tk.Button(master, text="Перейти к запросу группы.", command = )
        #self.request_stage.pack()

    def find_profile_in_data(self):
        quest_1 = self.profil.find_profile(self.login_entry.get(), self.key_entry.get())
        if quest_1 == False: 
        	registration(self.key_entry.get()).open_registration_window
        else:
            self.profil.login, self.profil.password = quest_1
            URL_request(self.profil.login, self.profil.password).open_downloading_window()


root = tk.Tk()
root.geometry("200x100")
app = ProfilApp(root)
root.mainloop()