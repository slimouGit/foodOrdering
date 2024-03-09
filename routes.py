import time
import uuid
from flask import Flask, jsonify, render_template
from api import streaming_audio_to_text, validateOrder, textToSpeech, speechToText, find_latest_recording, obtain_highlight_events, assign_size_classes_balanced
from database import initGoods, showGoods, get_goods_by_id
import os
from flask import request
from config import PATH
from flask_socketio import SocketIO, join_room, leave_room, emit
import random
import json


app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def yourDriveIn():
    initGoods()
    items = showGoods()
    modified_items = assign_size_classes_balanced(items)
    print(f"Modified items: {modified_items}")
    return render_template('index.html', items=modified_items)

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

@socketio.on('connect')
def on_connect():
    client_uuid = str(uuid.uuid4())
    join_room(client_uuid)  # Automatically join the client into a room named after their UUID
    emit('assign_uuid', {'uuid': client_uuid}, room=client_uuid)
    # Highlight the first item by default for testing purposes
    #emit('highlight', {'typ': 'select', 'id': 1}, room=client_uuid)
    print(f'Assigned UUID {client_uuid} to client {request.sid}')

@app.route('/stream-audio', methods=['POST'])
def stream_audio():
    # UUID and audio file chunk are expected in the request
    client_uuid = request.form.get('uuid')
    audio_chunk = request.files['audio_chunk']
    highlighted_items_json = request.form.get('highlightedItems', '[]')
    highlighted_items = json.loads(highlighted_items_json)  # Parse the JSON string back into a Python list

    if not audio_chunk:
        return jsonify({"error": "No audio chunk provided"}), 400

    text = streaming_audio_to_text(audio_chunk)

    print(f'Client {client_uuid} said: {text}')

    goods = showGoods()

    events = obtain_highlight_events(text, highlighted_items, goods)

    for event in events:
        socketio.emit('highlight', event, room=client_uuid)

    # Based on the processed text, decide whether to send a select or deselect event
    # This is simplified; you'd likely have logic to map specific speech content to actions

    # if "select" in text:
    #     socketio.emit('highlight', {'typ': 'select', 'id': 'some_item_id'}, room=client_uuid)
    # elif "deselect" in text:
    #     socketio.emit('highlight', {'typ': 'deselect', 'id': 'some_item_id'}, room=client_uuid)

    return jsonify(success=True), 200
