# уставновить нужно в комадной строке
# pip install snscrape
# pip install sqlite3
# pip install openpyxl

import json
import sqlite3
import subprocess

from openpyxl.workbook import Workbook

# количество постов
# item = 100
item = input('Введите количество постов')

# парсит данные
cmd_str = f"snscrape --max-results {item} --jsonl telegram-channel nastolka_n1 > ss.txt"
subprocess.run(cmd_str, shell=True)

# подключение к бд
con = sqlite3.connect("db.db")
cursor = con.cursor()


# добавление данных
def execute_query(con, query):
    cursor = con.cursor()
    try:
        cursor.execute(query)
        con.commit()
        print("Query executed successfully")
    except Exception as e:
        print(f"The error '{e}' occurred")


# создание таблиц
def table(con):
    create_table = """
    CREATE TABLE IF NOT EXISTS total (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      nomber TEXT NOT NULL, 
      date TEXT NOT NULL, 
      time TEXT NOT NULL, 
      liga TEXT NOT NULL, 
      team_1 TEXT NOT NULL, 
      other TEXT NOT NULL, 
      team_2 TEXT NOT NULL, 
      itm TEXT NOT NULL, 
      kf TEXT NOT NULL, 
      set_1 TEXT NOT NULL, 
      set_2 TEXT NOT NULL,  
      win TEXT NOT NULL 
    );
    """
    try:
        execute_query(con, create_table)
    except Exception as e:
        print(e)


# добавление данных
def insert_db(cursor, datas):
    cursor.execute(
        "INSERT INTO total (nomber, date, time, liga, team_1, other, team_2, itm, kf, set_1, set_2, win)  VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        datas)
    con.commit()


# проверка существования таблицы
table(con)

# основной окд
with open('ss.txt') as datas:
    for i,data in enumerate(datas):  # проходит по списку
        index = json.loads(data)

        # дата
        date = index['date'].split(('T', 1)[0])[0]

        # время
        date_time = index['date'].split('T', 1)[1]
        time = date_time[:str(date_time).find('+')]

        content = str(index['content'])
        print(content)
        try:
            if content.find('🏓Сигнал') >= 0:  # даляем не нужные посты
                # номер
                nomber = content[:content.find('Настольный')].replace('🏓Сигнал ', '')

                # лига
                liga_1 = content[content.find('Настольный теннис. '):].replace('Настольный теннис. ', '')
                liga = liga_1[:liga_1.find("Время матча:")]

                # команды
                text2 = content[content.find('скоро начнется...'):].replace('скоро начнется...', '')
                commands = text2[:text2.find('Ставка:')]
                team_1 = commands[:commands.find('(')]
                team_2 = str(commands[commands.find(')'):].replace("(Рос)", ""))[4:]

                #ИТМ
                itm_text = content[content.find("ИТМ"):]
                itm = itm_text[:itm_text.find('кф')].replace(' ', '')

                #кф
                kf_text = content[content.find("кф"):]
                kf = kf_text[:kf_text.find('Как ставить?')].replace('кф', '').replace(' ', '')

                #сет
                set_text = content[content.find("ЧИТАЙ ЗАКРЕП!!!"):]
                win = set_text[:set_text.find('(')].replace("ЧИТАЙ ЗАКРЕП!!!", "")
                if win.find("❌") >= 0:
                    win = ' 0 сет'
                else:
                    win = win[1:]
                set_1 = set_text[set_text.find('('):set_text.find(')')].replace('(', '')
                set_2_text = set_text[set_text.find('('):]
                set_2 = set_2_text[set_2_text.find(')'):].replace(")", "").replace("(", "").replace(" ", "")

                other = "-"

                if not set_1 == '': #если не пустое то записывает
                    cursor.execute("SELECT * FROM total WHERE nomber = ?", (nomber,))
                    if cursor.fetchone() is None:
                        datas = (nomber, date, time, liga, team_1, other, team_2, itm, kf, set_1, set_2, win)
                        insert_db(cursor, datas)
                        print(f"{i}-{item} Успешно добавлено {nomber}")
        except:
            pass


#вытаскивает данные из бд в excel
wb = Workbook()
ws = wb.active
ws.title = "Worksheet Title"

SQL_QUERY = "select * from total"
conn = sqlite3.connect('db.db')
c = conn.cursor()
c.execute(SQL_QUERY)
row = c.fetchall()
column_list = []


for column_name in c.description:
    column_list.append(column_name[0])
ws.append(column_list)

for result in row:
    ws.append(list(result))

wb.save("total.xlsx")
