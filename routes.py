import time
import uuid
from flask import Flask, jsonify, render_template
from api import validateOrder, textToSpeech, speechToText, find_latest_recording
from database import initData
from errormessage import COULD_NOT_PROCESS_ORDER, COULD_NOT_FIND_ORDER_RECORDING, \
    COULD_NOT_FIND_ORDER_RECORDING_TRY_AGAIN
from repository import showGoods, get_goods_by_id, get_item_by_synonym
import os
from flask import request
from config import PATH


app = Flask(__name__)

@app.route('/')
def yourDriveIn():
    initData()
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
        order, total_price = validateOrder(text)
    elif recording_id:
        recording_path = find_latest_recording(recording_id)
        if not recording_path:
            return render_template('error.html', message=COULD_NOT_FIND_ORDER_RECORDING)
        text = speechToText(recording_path)
        try:
            order, total_price = validateOrder(text)
        except Exception as e:

            return render_template('index.html', message=COULD_NOT_FIND_ORDER_RECORDING_TRY_AGAIN)
    else:
        return render_template('error.html', message=COULD_NOT_PROCESS_ORDER)

    return render_template('order.html', order=order, total_price=total_price)


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

@app.route('/goods/<string:name>')
def get_item_by_name_route(name):
    data = get_item_by_synonym(name)
    if data is None:
        return "No data found for ID: " + str(id), 404
    else:
        return render_template('goods.html', data=[data])