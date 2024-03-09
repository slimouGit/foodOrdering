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
import tempfile
from pathlib import Path
import io

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
# def speechToText(audio_file_path):
#     with open(audio_file_path, "rb") as audio_file:
#         transcript = client.audio.transcriptions.create(
#             file=audio_file,
#             model="whisper-1",
#         )
#     print(transcript.text)
#     return transcript.text
def speechToText(audio_file_path):
    print(f"Attempting to transcribe file: {audio_file_path}")
    if os.path.exists(audio_file_path):
        print(f"File exists. Size: {os.path.getsize(audio_file_path)} bytes")
    else:
        print("File does not exist.")
        return "Error: File does not exist."

    with open(audio_file_path, "rb") as audio_file:
        try:
            transcript = client.audio.transcriptions.create(
                file=audio_file,
                model="whisper-1",
            )
            print(transcript.text)
            return transcript.text
        except openai.BadRequestError as e:
            print(f"Transcription error: {str(e)}")
            return "Error during transcription."


def streaming_audio_to_text(audio_chunk):
    audio_bytes = audio_chunk.read()
    buffer = io.BytesIO(audio_bytes)
    buffer.name = 'audio.webm'
    transcript = client.audio.transcriptions.create(
        file=buffer,
        model="whisper-1",
    )
    return transcript.text

import random

def assign_size_classes_balanced(items):
    modified_items = []
    row_capacity = 3  # Assuming a 3-column grid
    row_fill = 0

    for item in items:
        mod_item = list(item)
        if row_fill == 2:  # Only 1 unit can fit
            size_class = 'grid-span-1'
            row_fill = 0  # Reset for new row
        elif row_fill == 1:  # Either 1 or 2 units can fit
            size_class = random.choice(['grid-span-1', 'grid-span-2'])
            row_fill = 0 if size_class == 'grid-span-2' else 1
        else:  # Row is empty, any size can fit
            size_class = random.choice(['grid-span-1', 'grid-span-2', 'grid-row-2'])
            row_fill += 2 if size_class in ['grid-span-2', 'grid-row-2'] else 1
        
        if row_fill >= row_capacity:  # Reset fill if row is full
            row_fill = 0

        mod_item.append(size_class)
        modified_items.append(mod_item)

    return modified_items


def obtain_highlight_events(text, highlighted_items, goods):
    """
    Send a request to OpenAI to interpret the transcribed text and obtain highlight events.
    """
    # Prepare the list of current menu items as a string
    # TODO switch to a proper data model
    # goods_list_str = ", ".join([f"id {id}: {name}" for id, name in goods])
    goods_list_str = ", ".join([f"id: {item[0]}, name: {item[1]}" for item in goods])

    highlighted_items_str = json.dumps(highlighted_items)

    print(f"Highlighting items: {highlighted_items_str}")

    print(type(goods_list_str))  # Should output: <class 'str'>
    print(type(highlighted_items_str))  # Should output: <class 'str'>
    print(goods_list_str)
    print(highlighted_items_str)

    system_prompt = f"""You are a smart assistant in a restaurant. Interpret customer orders and convert them to a json array of highlight events like [{{"id": "1", "typ": "select"}}, {{"id": "1", "typ": "deselect"}}]. Here are the current menu items we have available: [{goods_list_str}]. Currently selected items: {highlighted_items_str}. Only return the differences between the current selection and the new selection provided by the user. Never respond different than a valid json array."""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": text,
                },
            ],
            temperature=0.5,
        )

        if response and response.choices:
            json_string = response.choices[0].message.content
            print(f"Obtained highlight events: {json_string}")
            # Convert the string representation to a Python list of events
            events = json.loads(json_string)
            return events
    except Exception as e:
        print(f"An error occurred while obtaining highlight events: {str(e)}")
        return []

    return []

