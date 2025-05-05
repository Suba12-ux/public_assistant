from functools import lru_cache
import pathlib, os
from datetime import datetime, timedelta, date
from selenium import webdriver
from selenium.webdriver.common.by import By
from collections import namedtuple
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time, csv

def zapros_url(url, login, password):
    ''' 
    url - урл адресс группы
    login - логин от профиля
    password - пароль от профиля
    '''
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.keys import Keys
    import time

    try:
        # Создаем экземпляр веб-драйвера
        driver = webdriver.Chrome()

        # Открываем страницу входа
        driver.get(url)

        # Вводим логин и пароль
     
        try:
            # Находим поля ввода логина
            login_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "login"))
            )
            #if not login_field: raise ValueError
            # Заполняем поля ввода логина
            login_field.send_keys(login)
        except TimeoutException:
            driver.quit()
            return None, None, None 
        # Нажимаем кнопку входа
        driver.find_element(By.XPATH, '//button[@type="submit"]').click()

        # Находим поля ввода пароля
        password_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "password"))
        )

        # Заполняем поля ввода
        password_field.send_keys(password)

        # Нажимаем кнопку входа
        driver.find_element(By.XPATH, '//button[@type="submit"]').click()

        # переходим к группам

        # Find all link elements within the div element
        links = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//div[@class='GroupStudent__body']//a[starts-with(@href, '/student/update/')]"))
        )

        data_group = []
        # Print the text of each link element
        for link in links: data_group.append(link.text)

        #****************************************************************************
        passed_box_elements1 = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//div[@class='GroupStudent__body']//div[@class='Expandable GroupStudent__item']//div[@class='Expandable__header']//div[@class='GroupStudent__row']//div[@class='GroupStudent__col GroupStudent__col__progress']//div[@class='StudentProgress']//div[@class='PassedBox__group']"))
        )
        txt = []
        # Iterate over each passed box element
        for passed_box_element in passed_box_elements1:
            # Find all elements with class "PassedBox_box PassedBox_present glyphicon" within the passed box element
            present_elements = passed_box_element.find_elements(By.XPATH, ".//span[@class='PassedBox_box PassedBox_present glyphicon']")
            txt.append(len(present_elements))

        # Получаем статус и название группы ******************************************

        gro = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.XPATH, "//div[@class='EditableArea__input']"))
        )
        x = list(filter(lambda a: a!='', [gs.text for gs in gro]))
        #****************************************************************************

        passed_box_elements2 = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//div[@class='GroupStudent__info']"))
        )

        lg_pas = [i.text.split(': ') for i in passed_box_elements2]
        # Закрываем веб-драйвер
        driver.quit()
        txt = list(map(int, txt))
        data_group = list(map(lambda a: a.split(), data_group))

        UserEntry = namedtuple('UserEntry', 'name surname visits login_student password_student gender feedback data_numder')
        data_groupt = tuple(map(lambda a,b,c: UserEntry[1](name=a[1], surname=a[0], visits=b, login_student=c[0], password_student=c[1], gender=None, feedback=None, data_numder=None) , data_group, txt, lg_pas))
        return data_groupt, x
    except TimeoutException:
        driver.quit()
        return None, None, None
    except ValueError:
        driver.quit()
        return None, None, None

def URL_record_data(login_student, password_student):
    '''
        Получает логин и пароль ученика
    '''
    # Инициализация драйвера
    driver = webdriver.Chrome()

    try:
        # Переход на страницу логина
        driver.get("https://learn.algoritmika.org/login")

        # Ожидаем, пока элементы логина и пароля станут доступными
        username_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[data-qa-id="login-input"]'))  # Используем data-qa-id для логина  ngoncharovb7: 9352
        )
        username_input.send_keys(login_student)

        driver.find_element(By.XPATH, '//button[@type="submit"]').click() #  class="sc-hylbpc cuEwql"

        password_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[data-qa-id="password-input"]'))  # Обратите внимание, вы также должны использовать правильный селектор для пароля
        )
        # Вводим ваши учетные данные
          # Замените на ваш логин
        password_input.send_keys(password_student)    # Замените на ваш пароль

        driver.find_element(By.XPATH, '//button[@type="submit"]').click()

        time.sleep(3)

        driver.find_element(By.XPATH, '//a[@class="sc-hylbpc cuEwql"]').click() # class="sc-jTrGia edjRnU"

        time.sleep(3)
        #*********************************************
        try:
            # Пытаемся найти и кликнуть на кнопку
            driver.find_element(By.XPATH, '//button[@data-qa-id="popup-stories-button-next-slide"]').click()
        except Exception as e:
            # Если кнопка не найдена, просто выводим сообщение и продолжаем
            print("Кнопка не найдена:")

        element1 = WebDriverWait(driver, 20).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a[data-qa-id="task"]')))

        passed_levels = (i.get_attribute('data-qa-passed-levels') for i in element1)
        total_levels = (i.get_attribute('data-qa-total-levels') for i in element1)

        total_quest = tuple(map(lambda a,b: (a,b,) , passed_levels, total_levels))
        total_quest = tuple((total_quest[i],total_quest[i+1],total_quest[i+2],total_quest[i+3],) for i in range(0,len(total_quest),4))
        return total_quest
    except Exception:
        return None
    finally:
        # Закрываем браузер
        driver.quit()

def main_cycle(login, password):
    
    url = input('Введите url адрес группы.\n')

    students, visits, name_group = zapros_url(url, login, password)

    txt = gender(students, visits)

    #************************************** ЭТАП 3 **************************************
    
    way = pathlib.Path(find_file('os_group.tsv')).resolve()
    with way.open('a', encoding='utf-8') as lib:
        ts = creating_templates(txt)
        print(f"Группа: {date.today()- timedelta(3)}", '\t'+str(*name_group), file=lib)
        for k in ts:
            print(k[0], k[-1], file=lib)
        print('****************************************************************************', file=lib)
        print('Данные сохранены в текстовый файл os_group', f'Путь сохронения: {way}', sep='\n')

def find_file(file_name):
    '''Получает имя файла в формате str'''
    # перебераем все диски:
    for drive in ['C:', 'A:', 'D:', 'E:', 'B:', 'F:', 'G:']: # нужно заменить при необходимости
        for root, dirs, files in os.walk(drive):
            if file_name in files: return os.path.join(root, file_name) #проверка на совпадения
    return None

def gender(txt):
    '''
    Функция на определение пола.
    Получает именовой кортеж. namedtuple
    '''
    way = pathlib.Path('GenderData.csv').resolve()
    col = ['name', 'gender']
    
    #создаем файл если нет.
    if not way.exists():
        with way.open('w', encoding='utf-8', newline='') as lib:
            writer = csv.writer(lib, delimiter=';', quoting=csv.QUOTE_NONNUMERIC)
            writer.writerow(col)

    # Читаем существующие данные
    with way.open('r', encoding='utf-8', newline='') as path_1:
        data_base = tuple(csv.reader(path_1, delimiter=';'))
        # Преобразуем списки в кортежи
        data_base = tuple(map(lambda a: tuple(a), data_base[1:]))
        print('дата бэйс', data_base)
        # Выставляем пол всем
        global_obj_lokal = tuple(map(lambda a: (a.name, a.surname, pol(a.name+' '+a.surname),) ,txt))
        print('глобал1', global_obj_lokal)
        # Меняем согласно списку гендера
        global_obj_lokal_dop = tuple()
        for a in global_obj_lokal:
            for b in data_base:
                if a[0] == b[0]: 
                    global_obj_lokal_dop += ((a[0], a[1], b[1],),)
                    break
            else:
                global_obj_lokal_dop += (a,)
        print('глобал2', global_obj_lokal_dop)



        # Фильтруем тех учеников которых нет в списке
        set_studens_etalon = set([(i[0], i[1]) for i in data_base])
        set_studens_current = set(map(lambda a: (a[0], a[2],), global_obj_lokal_dop))
        total = tuple(set_studens_current - set_studens_etalon)
        print('тотал1', set_studens_etalon)
        print('тотал1', set_studens_current)


        with way.open('a', encoding='utf-8', newline='') as path_2:
            writer = csv.writer(path_2, delimiter=';', quoting=csv.QUOTE_NONNUMERIC)
            if len(total) != 0:
                for element in total:
                    writer.writerow([element[0], element[1]])
    
    new_namdtuple = tuple(map(lambda a, b: a._replace(gender=b[2]) ,txt, global_obj_lokal_dop))  
    
    return new_namdtuple

def users():
    '''
    Аргументов не принимает, создет файл users.txt в корневой части папки проета.
    Проверка профелей так же идет из файла users.txt.
    '''
    UL_key = sum([ord(i) for i in input('Введите свой уникальный ключ шифрования.\nИли придумайте и не забывайте =>.\nЭто может быть все что угодно даже слова или придложения.\n')])  
    lib_puth = pathlib.Path('users.csv').resolve()

    # создаем файл, если он не существует
    if not os.path.exists(lib_puth):
        with open(lib_puth, 'w') as path_:
            writer = csv.writer(path_, delimiter=';') # просто создаем пустой файл csv c элементами 'login','pass','ULk'
            writer.writerow(['login','pass','ULk'])

    with lib_puth.open('r+', encoding='utf-8') as prof:

        sl = csv.DictReader(prof, delimiter=';', quotechar='"')
        exod = SES(str(UL_key), UL_key)
        for i in sl:
            if exod == i['ULk']:  # если профиль найден
                return decod(i['login'], UL_key), decod(i['pass'], UL_key)

        else:   # если профиль ненайден
            a = input('Профиль не найден.\nНеобходима регестрация?\nДля подтверждения введите [да/yes]\n').lower()
            if a  in ['yes', 'да']:
                login = input('Введи логин от профиля!\n')
                password = input('Введи пароль от профиля!\n')
                writer = csv.writer(prof, delimiter=';')
                writer.writerow([SES(str(login), UL_key), SES(str(password), UL_key), SES(str(UL_key), UL_key)])
                return login, password
            else:
                return users()

def ru_en_translate(txt):
    lang = {"А":'A', "Б":'B', "В":'V', "Г":'G', "Д":'D', "Е":'E', "Ж":'ZH', "З":'Z', "И":'I', "Й":'J', "К":'K', "Л":'L', "М":'M', "Н":'N', "О":'O', "П":'P', "Р":'R', "С":'S', "Т":'T', "У":'U', "Ф":'F', "Х":'H', "Ц":'TS', "Ч":'CH', "Ш":'SH', "Щ":'SHCH', "Ъ":'', "Ы":'Y', "Ь":'', "Э":'E', "Ю":'YA', "Я":'YA', ' ':' '}
    sl = ''
    for i in txt.upper():
        if i in lang: sl += lang[i]
        else: continue 
    return sl.lower().title()

def SES(sl, UL_key): 
    txt = list(map(lambda a: int(hex(ord(a)+UL_key), 16) ,sl))
    return ' '.join(map(str, txt))

def decod(sl, UL_key):
    txt = list(map(int, sl.split()))
    return ''.join(list(map(lambda a: chr(int(str(a-UL_key), 10)) ,txt)))

def grup(txt):
    x1 = [k for k in txt]
    #x2 = input('Введи код посещения:') # 0121301300210 **********************************************************
    for k in range(len(x1)):
        txt[x1[k]].append(x2[k])
    return txt

def CHupp1(x):
    if 'Мужчина' == x.gender: 
        if 3 == x.visits or '3' == x.visits: characteristic = f'\t{x.name} был на всех уроках миникурса. '
        elif 2 == x.visits or '2' == x.visits: characteristic = f'\t{x.name} был только на 2 уроках миникурса. '
        elif 1 == x.visits or '1' == x.visits: characteristic = f'\t{x.name} был только на 1 уроках миникурса. '
        elif 0 == x.visits or '0' == x.visits: characteristic = f'\t{x.name} не был ни на одном из урков. '
    else: 
        if 3 == x.visits or '3' == x.visits: characteristic = f'\t{x.name} была на всех уроках миникурса. '
        elif 2 == x.visits or '2' == x.visits: characteristic = f'\t{x.name} была только на 2 уроках миникурса. '
        elif 1 == x.visits or '1' == x.visits: characteristic = f'\t{x.name} была только на 1 уроках миникурса. '
        elif 0 == x.visits or '0' == x.visits: characteristic = f'\t{x.name} не присутствовала ни на одном из урков. '
    
    return characteristic

def CHupp2(x):
    '''
    Функция для создания харакиристик.
    Получает список из одного Человека:
    Пример ----> ['Волков Матвей', 'Мужчина', 3]
    '''
    import random, pathlib, csv
    import funk_assistent

    #name = x[0].split()[-1]
    os_path_files = [funk_assistent.find_file(f'nch{i}.csv') for i in range(1, 5)]
    with open(os_path_files[0], 'r', encoding='utf-8') as path_1, open(os_path_files[1], 'r', encoding='utf-8') as path_2, open(os_path_files[2], 'r',encoding='utf-8') as path_3, open(os_path_files[3], 'r',encoding='utf-8') as path_4:
        characteristic = x.feedback
        if 3 == x.visits or 2 == x.visits or '3' == x.visits or '2' == x.visits:
            for n, i in enumerate([path_1, path_2, path_4, path_3]):
                sh_l = list(map(lambda a: a[-1], csv.reader(i, delimiter=';')))[1:]
                if n == 3: characteristic += 'Что бы усваивать материал более качественно ' + random.choice(sh_l)
                elif n == 0: characteristic += 'За эти 3 дня мы изучили много нового ' + random.choice(sh_l)
                elif n == 2: characteristic += 'Касаемо комуникации ученика ' + random.choice(sh_l)
                else: characteristic += random.choice(sh_l)

            data_numder = x.data_numder 
            if data_numder != None:
                characteristic += f' Так же делюсь с свами статистикой с миникурса: Урок1 Введение в язык Python:(Первые программы: всего выполнено: {int(data_numder[0][0][0])} из {int(data_numder[0][0][1])-1}), Вывод данных: {int(data_numder[0][1][0])} из {int(data_numder[0][1][1])}, доп_задания: {int(data_numder[0][2][0])} из {int(data_numder[0][2][1])}'
                characteristic += f' Урок2 Переменные:(Турфирама автоматизация: {int(data_numder[1][0][0])} из {int(data_numder[1][0][1])}), Турфирма оптимизация: {int(data_numder[1][1][0])} из {int(data_numder[1][1][1])}, доп_задания: {int(data_numder[1][2][0])} из {int(data_numder[1][2][1])}'
                characteristic += f' Урок3 Строки:(Обратная Связь1: {int(data_numder[2][0][0])} из {int(data_numder[2][0][1])-1}), Обратная Связь2: {int(data_numder[2][1][0])} из {int(data_numder[2][1][1])}, доп_задания: {int(data_numder[2][2][0])} из {int(data_numder[2][2][1])}'

        text = ''.join(characteristic)
    return text

def replace_gender_staf(x):
    
    text = x.feedback
    if 'Девушка' == x.gender:
        text = text.replace('УЧЕНИК', x.name)
        text = text.replace(' показал ', ' показала ')
        text = text.replace(' выступил ', ' выступила ')
        text = text.replace(' продемонстрировал ', ' продемонстрировала ')
        text = text.replace(' обнаружил ', ' обнаружила ')
        text = text.replace(' проявлял ', ' проявляла ')
        text = text.replace(' обрабатывал ', ' обрабатывала ')
        text = text.replace(' способен ', ' способна ')
        text = text.replace(' использовал ', ' использовала ')
        text = text.replace(' управлял ', ' управляла ')
        text = text.replace(' научился ', ' научилась ')
        text = text.replace(' сталкнулся ', ' сталкнулась ')
        text = text.replace(' испытывал ', ' испытывала ')
        text = text.replace(' получил ', ' получила ')
        text = text.replace(' сталкивался ', ' сталкивалась ')
        text = text.replace(' справился ', ' справилась ')
        return text
    else:
        text = x.feedback
        text = text.replace('УЧЕНИК', x.name)
        return text

def creating_templates(txt):
    #txt1 = list(filter(lambda a: True if len([1 for i in a if str(i).isdigit()])!=0 else False ,txt))
    global_object_students = tuple(map(lambda a: a._replace(feedback=CHupp1(a)), txt))
    global_object_students = tuple(map(lambda a: a._replace(feedback=CHupp2(a)), global_object_students))
    global_object_students = tuple(map(lambda a: a._replace(feedback=replace_gender_staf(a)), global_object_students))
        
    return global_object_students

def remake(txt):
    for k in txt:
        if 'Девушка' in txt[k]:
            txt[k][-1] = txt[k][-1].replace('ученики', k.split()[-1])
            txt[k][-1] = txt[k][-1].replace('\n', '')
            txt[k][-1] = txt[k][-1].replace('ваня', k.split()[-1])
            txt[k][-1] = txt[k][-1].replace('ученика', '')
            txt[k][-1] = txt[k][-1].replace('ученику', 'ей')
            txt[k][-1] = txt[k][-1].replace('ученик', k.split()[-1])
            txt[k][-1] = txt[k][-1].replace('он', 'она')
            txt[k][-1] = txt[k][-1].replace('его', 'ее')
            txt[k][-1] = txt[k][-1].replace('этот', '')
            txt[k][-1] = txt[k][-1].replace('лся', 'лась')
            txt[k][-1] = txt[k][-1].replace('ым', 'ой')
            txt[k][-1] = txt[k][-1].replace('был', 'была')
            txt[k][-1] = txt[k][-1].replace('ен', 'ена')
            for j in txt[k][-1].split():
                if j[-1] == 'л':
                    c = txt[k][-1].find(j)
                    #ts = txt[k][-1][c:len(j)+1]+'а'
                    txt[k][-1] = txt[k][-1].replace(j, j+'а')

        elif 'Мужчина' in txt:
            txt[k][-1] = txt[k][-1].replace('\n', '')
            txt[k][-1] = txt[k][-1].replace('ученики', k.split()[-1])
            txt[k][-1] = txt[k][-1].replace('ваня', k.split()[-1])
            txt[k][-1] = txt[k][-1].replace('этот', '')
            txt[k][-1] = txt[k][-1].replace('ученика', '')
            txt[k][-1] = txt[k][-1].replace('ученику', 'ему')
    return txt

def pol(txt):
    a = txt.split()
    if a[0][-1] == 'а' or a[-1][-1] in ['а', "я"]: return 'Девушка'
    else: return 'Мужчина'



