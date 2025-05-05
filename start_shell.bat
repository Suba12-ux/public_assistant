@echo off
REM Активация виртуального окружения
call venv\Scripts\activate

REM Установка зависимостей
pip install -r requirements.txt

REM Запуск вашего скрипта Python
python assistant_1_2.py

REM Запуск вашего файла os_group.txt
start notepad os_group.txt
