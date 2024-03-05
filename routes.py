from flask import Flask, render_template
from api import validateOrder, textToSpeech, speechToText
from database import initGoods, showGoods, get_goods_by_id

app = Flask(__name__)

@app.route('/')
def yourDriveIn():
    initGoods()
    return render_template('index.html')

@app.route('/order')
def takeOrder():
    textToSpeech()
    order = speechToText()
    order = validateOrder(order)
    return render_template('order.html', order=order)

@app.route('/goods')
def showGoodsRoute():
    data = showGoods()
    print("redirecting to goods.html")
    return render_template('goods.html', data=data)

@app.route('/goods/<int:id>')
def get_goods_by_id_route(id):
    data = get_goods_by_id(id)
    if data is None:
        return "No data found for ID: " + str(id), 404
    else:
        return render_template('goods.html', data=[data])