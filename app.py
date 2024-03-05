import openai
from openai import OpenAI
import json
from urllib import response

from flask import Flask, render_template, request
import os
from config import API_KEY, PATH

client = OpenAI(api_key=API_KEY)

app = Flask(__name__)

@app.route('/')
def yourDriveIn():
    return render_template('index.html')


#Order is checked and available components are returned
def validateOrder(order_transcription):
    #validate order and redirect to error page if necessary
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a smart assistant in a restaurant. Interpret customer orders and list the items in a json array like ['fries, 'milkshake']."},
                {"role": "user", "content": order_transcription},
            ],
            temperature=0.5,
        )
        
        # Accessing the response directly using Pydantic model attributes
        if response and response.choices:
            json_string = response.choices[0].message.content
            # Convert the string representation of the list to a Python list
            items = json.loads(json_string)
            return items
        else:
            return ["Error: Unable to process the order. Please try again."]
    except openai.APIConnectionError as e:
        print("The server could not be reached")
        print(e.__cause__)  # an underlying Exception, likely raised within httpx.
        return ["Error: The server could not be reached."]
    except openai.RateLimitError as e:
        print("A 429 status code was received; we should back off a bit.")
        return ["Error: Rate limit exceeded. Please try again later."]
    except openai.APIStatusError as e:
        print("Another non-200-range status code was received")
        print(e.status_code)
        print(e.response)
        return [f"Error: An API error occurred with status code {e.status_code}."]
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        return ["Error: An unexpected error occurred."]


#Determined order is displayed for confirmation
@app.route('/order')
def takeOrder():
    # textToSpeech()
    order = speechToText()
    order = validateOrder(order)
    return render_template('order.html', order=order)

#voice input of the customer is simulated and saved as mp3
def textToSpeech():
    response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input="I would like to order a burger with nuggets and a coke.",
    )

    with open("order.mp3", "wb") as out_file:
        out_file.write(response.read())
        speechToText()

#the customer's voice input is interpreted and converted into text
def speechToText():
    audio_file = open("order.mp3", "rb")
    transcript = client.audio.transcriptions.create(
        file=audio_file,
        model="whisper-1",
    )
    print(transcript.text)
    return transcript.text
    # for word_info in transcript.words:
    #     print(word_info['word'])
    # return [word_info['word'] for word_info in transcript.words]


# retrieve audio file and save to the specified output directory, returning HTTP status code of 204
@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    output_directory = PATH
    file.save(os.path.join(output_directory, 'order.mp3'))
    return '', 204


if __name__ == '__main__':
    app.run()