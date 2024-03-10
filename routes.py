import time
import uuid
from flask import Flask, jsonify, render_template
from api import validateOrder, textToSpeech, speechToText, find_latest_recording
from database import initGoods, showGoods, get_goods_by_id
import os
from flask import request
from config import PATH


app = Flask(__name__)

@app.route('/')
def yourDriveIn():
    initGoods()
    return render_template('index.html')

# retrieve audio file and save to the specified output directory, returning HTTP status code of 204
@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    output_directory = PATH  # Make sure PATH is defined to point to your intended directory
    recording_uuid = str(uuid.uuid4())
    timestamp = str(int(time.time()))
    filename = f'order_{recording_uuid}_{timestamp}.mp3'
    file_path = os.path.join(output_directory, filename)
    file.save(file_path)
    return jsonify({'recording_id': recording_uuid}), 200

# text or recording_id for an order is provided, the order is processed and displayed so the customer can confirm
@app.route('/order')
def takeOrder():
    text = request.args.get('text')
    recording_id = request.args.get('recording_id')
    
    if text:
        # Process the provided text
        order = validateOrder(text)
    elif recording_id:
        recording_path = find_latest_recording(recording_id)
        if not recording_path:
            return render_template('error.html', message="We're sorry, we couldn't find your order recording.")
        text = speechToText(recording_path)
        order = validateOrder(text)
    else:
        return render_template('error.html', message="We're sorry, we couldn't process your order. No text or recording ID was provided.")

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
@app.route('/card')
def dummyCard():
    items = []
    item1 = {
        'name': 'Chicken Nugget Burger',
        'price': 5.99,
        'description': 'Delicious Chicken Nugget Burger',
        'image_path': '../static/goods/Burger.jpg'
    }
    item2 = {
        'name': 'Coca-Cola',
        'price': 1.99,
        'description': 'Wonderfull Softdrink',
        'image_path': '../static/goods/Coke.jpg'
    }
    item3 = {
        'name': 'Chicken Nuggets',
        'price': 3.99,
        'description': 'Crunchy Chicken Nuggets',
        'image_path': '../static/goods/Nuggets.jpg'
    }
    items.append(item1)
    items.append(item2)
    items.append(item3)
    return render_template('card.html', items=items)