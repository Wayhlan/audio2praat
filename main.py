import os
import whisper_timestamped as whisper
import numpy as np
import torch
import time
import json

import audio_handler
import file_handler


os.environ['PYTHONIOENCODING'] = 'utf-8'

current_path = os.environ.get('PATH')
# print(f"Current PATH: {current_path}")

new_path = "C:/Users/virgi/Desktop/printemps/ffmpeg/bin"

os.environ['PATH'] = new_path + os.pathsep + current_path

updated_path = os.environ.get('PATH')


def transcribe_segment(segment, model_string, vad, detect_disfluencies, language):
    devices = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    model = whisper.load_model(model_string, device=devices)
    result = whisper.transcribe(model, segment, vad=vad, detect_disfluencies=detect_disfluencies, language=language)
    return result

def transcribe_from_file(file_path, output_folder="", model_string="large", vad=False, detect_disfluencies=False, language="vietnamese", segment_length_s=60):

    start_time = np.int32(time.time())
    segments = audio_handler.split_audio(file_path, segment_length_s)

    transcription_segments = []
    for segment in segments:
        audio = whisper.load_audio(segment)
        transcription_segments.append(transcribe_segment(audio, model_string, vad, detect_disfluencies, language))

    combined_results = {
        "segments": file_handler.adjust_segments(transcription_segments, segment_length_s)
    }

    # Saving transcription textgrid
    textgrid_val, full_text = file_handler.json_to_textgrid(combined_results)
    try:
        file_handler.save_output_files(output_folder, model_string, combined_results, textgrid_val, full_text)

        end_time = np.int32(time.time())
        execution_time_min = (end_time - start_time) // 60
        execution_time_sec = (end_time - start_time) % 60
        print(f"Done transcribing\nTotal execution time : {execution_time_min}m{execution_time_sec}s")
        return textgrid_val

        # return transcription_result['text']
    except Exception as e:
        print(f"Error while transcribing from audio file '{file_path}' : {e}")


if __name__ == "__main__":
    # Choose from ["tiny", "base", "small", "medium", "large", "large-v2", "large-v3"]
    model = "large"
    # vad Voice Activity Detection -> to glue up useful audio segments
    vad = False
    # detect_disfluencies -> to try and detect non-word voice activity
    detect_disfluencies = False
    language="vietnamese"
    output_folder = "output/testing"
    file_path = "res/Minh_1.wav"
    segment_length_s=80

    try:
        torch.cuda.empty_cache()
    except Exception as e:
        print("Failed to clear GPU cache, should not be an issue")


    print(f"Starting transcription for '{file_path}' :")
    print(f"Transcribing with model : Whisper-{model}")
    files_saved = transcribe_from_file(file_path=file_path, output_folder=output_folder, model_string=model, vad=vad, detect_disfluencies=detect_disfluencies, language=language, segment_length_s=segment_length_s)

# def read_audio_from_file(file_path = "res/Minh_1.wav"):
#     # help(whisper.transcribe)
#     try:
#         if "wav" in file_path:
#             audio = AudioSegment.from_wav(file_path)
#         elif "mp3" in file_path:
#             audio = AudioSegment.from_mp3(file_path)
#         else:
#             print(f"Unsupported Audio format in file : {file_path}")
#     except Exception as e:
#         print(f"Error while reading from audio file '{file_path}' : {e}")
#     # For conversion purposes.. : 
#     # audio.export("res/output.mp3", format="mp3")
#     # audio.export("res/output.wav", format="wav")
#     return audio

# with open('LARGE_nothing_format/transcription_combined_large.json', 'r', encoding="utf-8") as file:
#     # Step 3: Load the JSON data
#     data = json.load(file)
# full_text = combine_sentences_from_json(data)

# # Saving transcription textgrid
# json_to_textgrid(data, save_path=("LARGE_nothing_format/textgrid_" + model + ".TextGrid"), text=full_text)
