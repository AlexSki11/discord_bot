import sqlite3
from datetime import datetime



def first_connection(db='evill_database.db'):
    connection = sqlite3.connect(db)
    cursor = connection.cursor()

    # Создаем таблицу Users
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users (
    user_id INTEGER PRIMARY KEY,
    username TEXT NOT NULL,
    global_name TEXT NOT NULL
    )
    ''')
    #Servers
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Servers (
    server_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    grade INTEGER DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES Users (user_id) ON DELETE CASCADE
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Orders (
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    server_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    status INTEGER DEFAULT 0,
    name_winner TEXT DEFAULT '',
    FOREIGN KEY (server_id) REFERENCES Servers (server_id) ON DELETE CASCADE
    )
    ''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS Auctions (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   order_id INTEGER NOT NULL,
                   user_id INTEGER NOT NULL,
                   server_id INTEGER NOT NULL,
                   grade_bet INTEGER DEFAULT 0,
                   updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                   status_order INTEGER,
                   FOREIGN KEY (user_id) REFERENCES Users (user_id) ON DELETE CASCADE,
                   FOREIGN KEY (order_id) REFERENCES Orders (order_id) ON DELETE CASCADE,
                   FOREIGN KEY (server_id) REFERENCES Servers (server_id) ON DELETE CASCADE,
                   FOREIGN KEY (status_order) REFERENCES Orders (status) ON DELETE CASCADE
                   )
                   ''')

    # Сохраняем изменения и закрываем соединение
    connection.commit()
    connection.close()

def add_user(server,user, db='evill_database.db'):
    connection = sqlite3.connect(db)
    cursor = connection.cursor()
    cursor.execute('INSERT OR IGNORE INTO Users (user_id, username) VALUES (?, ?)', ( user.id, user.name,))
    cursor.execute('INSERT INTO Servers (server_id, user_id, grade) VALUES (?, ?, ?)', (server, user.id, 0,))
    connection.commit()
    print('success')
    connection.close()

def add_user_list(list_server, list_user, db='evill_database.db'): #list_server = [(server_id, user_id)] list_user = [(user.id, user.global_name, user.name)]
    connection = sqlite3.connect(db)
    cursor = connection.cursor()
    cursor.executemany('INSERT OR IGNORE INTO Users VALUES(?,?,?)', list_user)
    cursor.executemany('INSERT OR IGNORE INTO Servers VALUES(?, ?, ?)', list_server)
    connection.commit()
    print('success')
    connection.close()


def update_user(user_id, server_id, grade, db='evill_database.db'):
    connection = sqlite3.connect(db)
    cursor = connection.cursor()
    cursor.execute('SELECT grade FROM Servers WHERE user_id = ?', (user_id,))
    grade_now = cursor.fetchone()[0]
    # Обновляем оценку пользователя "newuser"
    cursor.execute('UPDATE Servers SET grade = ? WHERE user_id = ? AND server_id = ?', (grade_now+grade, user_id, server_id))

    # Сохраняем изменения и закрываем соединение
    connection.commit()
    connection.close()

def get_grade(server,user, db='evill_database.db'):
    connection = sqlite3.connect(db)
    cursor = connection.cursor()
    cursor.execute('SELECT grade FROM Servers WHERE server_id = ? AND user_id = ?', (server, user.id))
    grade = cursor.fetchone()[0]
    connection.close()
    
    return grade if grade else 0

def add_order(server_id,name,db='evill_database.db'):
    connection = sqlite3.connect(db)
    cursor = connection.cursor()
    cursor.execute('INSERT INTO Orders (server_id, name) VALUES (?, ?)', (server_id, name,))
    id = cursor.lastrowid
    connection.commit()
    connection.close()
    
    return id



def end_order(id, server_id, db='evill_database.db'):
    connection = sqlite3.connect(db)
    cursor = connection.cursor()
    if type(id)==int:
        cursor.execute('UPDATE Orders SET status = ? WHERE order_id = ? and server_id = ? and status = 0', (1, id, server_id))

        cursor.execute('SELECT user_id, server_id, order_id FROM Auctions WHERE order_id = ? AND server_id = ? ORDER BY grade_bet DESC LIMIT 1', (id,server_id))
        user = cursor.fetchone()
        if not user:
            cursor.close()
            connection.close()
            return
        cursor.execute('UPDATE Auctions SET grade_bet = 0 WHERE user_id = ? AND server_id = ? AND order_id = ?', user)
        cursor.execute('SELECT grade_bet, user_id, server_id FROM Auctions WHERE order_id = ? AND server_id = ?', (id,server_id))
        users = cursor.fetchall()
        cursor.executemany('UPDATE Servers SET grade = grade + ? WHERE user_id = ? AND server_id = ?', users)

    else:
        connection.close()
        return 

    

    connection.commit()
    connection.close()

#Много лишних проверок
def auction(order_id, user, server_id, grade, db='evill_database.db'):
    grade_now = int(get_grade(server_id,user))
    if grade > grade_now:
        return
    
    connection = sqlite3.connect(db)
    cursor = connection.cursor()

    cursor.execute('SELECT status FROM Orders WHERE order_id = ?', (order_id,))
    status = cursor.fetchone()[0]

    if status:
        cursor.close()
        connection.close()
        return

    cursor.execute('SELECT server_id FROM Orders WHERE order_id = ?', (order_id,))
    server = cursor.fetchone()[0]

    if server != server_id:
        cursor.close()
        connection.close()
        return

    cursor.execute('UPDATE Servers SET grade = ? WHERE server_id = ? AND user_id = ?', (grade_now-grade, server_id, user.id,))
    cursor.execute('SELECT user_id FROM Auctions WHERE user_id = ? AND order_id = ?', (user.id,order_id,))
    user_be = cursor.fetchone()
    if user_be:
        cursor.execute('SELECT grade_bet FROM Auctions WHERE order_id = ? AND user_id = ?', (order_id, user.id))
        grade = cursor.fetchone()[0] + grade
        cursor.execute('UPDATE Auctions SET grade_bet = ?, updated_at = ? WHERE order_id = ? AND user_id = ?', (grade, datetime.now(), order_id, user.id))
    else:
        cursor.execute('INSERT INTO Auctions (order_id, user_id, server_id, grade_bet, status_order) SELECT ?, ?, ?, ?, status FROM Orders WHERE order_id = ?',
        (order_id, user.id, server_id, grade, order_id,))



    connection.commit()
    cursor.close()
    connection.close()
    return grade

def get_users_auctions(order_id, db='evill_database.db'):
    connection = sqlite3.connect(db)
    cursor = connection.cursor()
    cursor.execute('SELECT Users.username, Auctions.grade_bet FROM Users JOIN Auctions ON Users.user_id = Auctions.user_id WHERE Auctions.order_id = ?', 
                   (order_id,))
    list_user = cursor.fetchall()
    cursor.close()
    connection.close()
    return list_user

def who_win(order_id, db='evill_database.db'):
    connection = sqlite3.connect(db)
    cursor = connection.cursor()

    cursor.execute('SELECT user_id, grade_bet FROM Auctions WHERE order_id = ? ORDER BY grade_bet DESC, updated_at ASC LIMIT 1', (order_id,))
    user = cursor.fetchone()
    if not user:
        cursor.close()
        connection.close()
        return
    cursor.execute('SELECT username, ?, ? FROM Users WHERE user_id = ?', (user[1], user[0],user[0]))
    user = cursor.fetchone()
    username = user[0]
    cursor.execute('UPDATE Orders SET name_winner = ? WHERE order_id = ?', (username, order_id,))
    connection.commit()
    cursor.close()
    connection.close()
    return user

    


