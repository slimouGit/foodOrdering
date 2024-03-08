import sqlite3

from requests import Session

class ItemDTO:
    def __init__(self, id, name, description, price, image_path):
        self.id = id
        self.name = name
        self.description = description
        self.price = price
        self.image_path = image_path
def initData():
    initGoods()
    initSynonyms()
def initSynonyms():
    conn = sqlite3.connect('goods.db')
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS synonym")
    c.execute('''CREATE TABLE synonym
                 (id INTEGER PRIMARY KEY, word text, good INTEGER,
                 FOREIGN KEY(good) REFERENCES goods(id))''')
    c.execute("INSERT INTO synonym (word, good) VALUES ('burger', 1)")
    c.execute("INSERT INTO synonym (word, good) VALUES ('hamburger', 1)")
    c.execute("INSERT INTO synonym (word, good) VALUES ('coke', 2)")
    conn.commit()
    conn.close()


def initGoods():
    conn = sqlite3.connect('goods.db')
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS goods")
    c.execute('''CREATE TABLE goods
                     (id INTEGER PRIMARY KEY, name text, description text, price real, image_path text)''')
    c.execute(
        "INSERT INTO goods (name, description, price, image_path) VALUES ('Chicken Nugget Burger', 'Delicious chicken nuggets', 35.14, '../static/Burger.jpg')")
    c.execute(
        "INSERT INTO goods (name, description, price, image_path) VALUES ('Coca-Cola', 'Wonderfull Softdrink', 5.14, '../static/Coke.jpg')")
    conn.commit()
    c.execute(
        "INSERT INTO goods (name, description, price, image_path) VALUES ('chicken nuggets', 'Crunchy Nuggets', 25.14, '../static/Nuggets.jpg')")
    conn.commit()
    c.execute('SELECT * FROM goods')
    print(c.fetchall())
    conn.close()

def showGoods():
    conn = sqlite3.connect('goods.db')
    c = conn.cursor()
    c.execute('SELECT * FROM goods')
    data = c.fetchall()
    conn.close()
    return data

def get_goods_by_id(id):
    conn = sqlite3.connect('goods.db')
    c = conn.cursor()
    c.execute('SELECT * FROM goods WHERE id=?', (id,))
    data = c.fetchone()
    conn.close()
    if data is None:
        return "No data found for ID: " + str(id), 404
    else:
        return data

def get_item_by_synonym(word):
    conn = sqlite3.connect('goods.db')
    c = conn.cursor()
    c.execute('''
        SELECT goods.* 
        FROM goods 
        JOIN synonym ON goods.id = synonym.good 
        WHERE synonym.word = ?
    ''', (word,))
    data = c.fetchone()
    conn.close()
    if data is None:
        return None
    else:
        return data

def get_items_from_db(item_names):
    dto_list = []
    # Iterate over the item names
    for name in item_names:
        # Fetch the item from the database by its name
        item = get_item_by_synonym(name)
        if item is not None:
            # Convert the item to an ItemDTO and append it to the list
            dto = ItemDTO(item[0], item[1], item[2], item[3], item[4])
            dto_list.append(dto)
    return dto_list