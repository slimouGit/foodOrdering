import openai
from flask import render_template
from openai import OpenAI
import json
from config import API_KEY, PATH
import os
import glob
from operator import itemgetter
import uuid
import time

from repository import get_items_from_db

client = OpenAI(api_key=API_KEY)


# Order is checked and available components are returned
def validateOrder(order_transcription):
    # validate order and redirect to error page if necessary
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system",
                 "content": "You are a smart assistant in a restaurant. Interpret customer orders and list the items in a json array like ['fries, 'milkshake']."},
                {"role": "user", "content": order_transcription},
            ],
            temperature=0.5,
        )

        # Accessing the response directly using Pydantic model attributes
        if response and response.choices:
            json_string = response.choices[0].message.content
            # Convert the string representation of the list to a Python list
            items = json.loads(json_string)
            itemDto = get_items_from_db(items)
            return itemDto
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
# def takeOrder():
#     textToSpeech()
#     order = speechToText()
#     order = validateOrder(order)
#     return render_template('order.html', order=order)

def find_latest_recording(uuid):
    search_pattern = os.path.join(PATH, f'order_{uuid}_*.mp3')
    recordings = glob.glob(search_pattern)
    if not recordings:
        return None
    # Extract timestamps and sort
    recordings_with_time = [(path, int(path.split('_')[-1].split('.')[0])) for path in recordings]
    latest_recording = max(recordings_with_time, key=itemgetter(1))[0]
    return latest_recording

#voice input of the customer is simulated and saved as mp3
def textToSpeech(input_text, output_directory):
    response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=input_text,
    )
    
    recording_uuid = str(uuid.uuid4())
    timestamp = str(int(time.time()))
    filename = f'order_{recording_uuid}_{timestamp}.mp3'
    file_path = os.path.join(output_directory, filename)
    
    with open(file_path, "wb") as out_file:
        out_file.write(response.read())
    
    return recording_uuid

#the customer's voice input is interpreted and converted into text
def speechToText(audio_file_path):
    with open(audio_file_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            file=audio_file,
            model="whisper-1",
        )
    print(transcript.text)
    return transcript.text