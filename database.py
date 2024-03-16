import sqlite3


def initData():
    initGoods()
    initSynonyms()
    initOrdering()
def initSynonyms():
    conn = sqlite3.connect('goods.db')
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS synonyms")
    c.execute('''CREATE TABLE synonyms
                 (id INTEGER PRIMARY KEY, word text, good INTEGER,
                 FOREIGN KEY(good) REFERENCES goods(id))''')
    c.execute("INSERT INTO synonyms (word, good) VALUES ('burger', 1)")
    c.execute("INSERT INTO synonyms (word, good) VALUES ('hamburger', 1)")
    c.execute("INSERT INTO synonyms (word, good) VALUES ('banana', 1)")
    c.execute("INSERT INTO synonyms (word, good) VALUES ('coke', 2)")
    c.execute("INSERT INTO synonyms (word, good) VALUES ('coca cola', 2)")
    c.execute("INSERT INTO synonyms (word, good) VALUES ('cola', 2)")
    c.execute("INSERT INTO synonyms (word, good) VALUES ('softdrink', 2)")
    c.execute("INSERT INTO synonyms (word, good) VALUES ('nuggets', 3)")
    c.execute("INSERT INTO synonyms (word, good) VALUES ('nugget', 3)")
    c.execute("INSERT INTO synonyms (word, good) VALUES ('crunchy chicken', 3)")
    conn.commit()
    conn.close()

def initGoods():
    conn = sqlite3.connect('goods.db')
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS goods")
    c.execute('''CREATE TABLE goods
                     (id INTEGER PRIMARY KEY, name text, description text, price real, image_path text)''')
    c.execute(
        "INSERT INTO goods (name, description, price, image_path) VALUES ('Chicken Nugget Burger', 'Delicious Chicken Nugget Burger', 35.14, '../static/goods/Burger.jpg')")
    c.execute(
        "INSERT INTO goods (name, description, price, image_path) VALUES ('Coca-Cola', 'Wonderfull Softdrink', 5.14, '../static/goods/Coke.jpg')")
    conn.commit()
    c.execute(
        "INSERT INTO goods (name, description, price, image_path) VALUES ('Chicken Nuggets', 'Crunchy Chicken Nuggets', 25.14, '../static/goods/Nuggets.jpg')")
    conn.commit()
    c.execute('SELECT * FROM goods')
    print(c.fetchall())
    conn.close()

def initOrdering():
    conn = sqlite3.connect('goods.db')
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS ordering")
    c.execute('''
        CREATE TABLE ordering
        (id INTEGER PRIMARY KEY, 
        order_id INTEGER, 
        good_id INTEGER, 
        FOREIGN KEY(good_id) REFERENCES goods(id))
    ''')
    conn.commit()
    conn.close()

def insertOrdering():
    conn = sqlite3.connect('goods.db')
    c = conn.cursor()

    c.execute("INSERT INTO ordering (order_id, good_id) VALUES (1, 2)")

    c.execute("INSERT INTO ordering (order_id, good_id) VALUES (1, 1)")
    c.execute('SELECT * FROM ordering')
    conn.close()

def get_all_goods_from_ordering():
    conn = sqlite3.connect('goods.db')
    c = conn.cursor()
    c.execute('SELECT * FROM ordering')
    data = c.fetchall()
    conn.close()
    return data