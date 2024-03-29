import sqlite3

from dto.itemDTO import ItemDTO


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
        JOIN synonyms ON goods.id = synonyms.good 
        WHERE synonyms.word = ?
    ''', (word,))
    data = c.fetchone()
    conn.close()
    if data is None:
        return None
    else:
        return data

def get_items_by_names(item_names):
    dto_list = []
    for item_name in item_names:
        item = get_item_by_synonym(item_name.lower())
        if item is not None:
            dto = ItemDTO(item[0], item[1], item[2], item[3], item[4])
            dto_list.append(dto)
    return dto_list

