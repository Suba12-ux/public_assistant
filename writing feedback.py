import tkinter as tk
from tkinter import messagebox
from functools import lru_cache
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
        self.tkinter_window = tk()
        self.tkinter_window.geometry("200x100")
        self.tkinter_window.title("Asistent_\\m/")
        self.tkinter_window.lable("")

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