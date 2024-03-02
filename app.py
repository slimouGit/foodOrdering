from openai import OpenAI
from flask import Flask
from config import API_KEY

client = OpenAI(api_key=API_KEY)

app = Flask(__name__)

@app.route('/')
def yourDriveIn():
    return 'Welcome to drive in!'

@app.route('/order')
def takeOrder():
    textToSpeech()
    return 'Your order please!'

def textToSpeech():
    response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input="Burger Coke",
    )

    with open("order.mp3", "wb") as out_file:
        out_file.write(response.read())
        speechToText()

def speechToText():
    audio_file = open("order.mp3", "rb")
    transcript = client.audio.transcriptions.create(
        file=audio_file,
        model="whisper-1",
        response_format="verbose_json",
        timestamp_granularities=["word"]
    )
    print(transcript.words)
    for word_info in transcript.words:
        print(word_info['word'])

if __name__ == '__main__':
    app.run()