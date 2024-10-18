import os
import numpy as np
import json
from praatio import textgrid
import inspect

import utils

def checkFilePaths(file_path):
    try:
        if file_path != "" and not os.path.isfile(file_path):
            print(f"{inspect.currentframe().f_code.co_name}:{inspect.currentframe().f_lineno} Failed to load input file : {file_path}")
            return -1
    except Exception as e:
        print(f"{inspect.currentframe().f_code.co_name}:{inspect.currentframe().f_lineno} Failed to load input file : \n{e}")
        return -1
    return 0

def adjust_segments(transcription_segments, lengths):
    combined_segments = []
    added_time = 0
    for i, segment in enumerate(transcription_segments):
        added_time += lengths[i-1]
        for sub_segment in segment["segments"]:
            sub_segment["id"] = f"{i}_{sub_segment['id']}"
            sub_segment["start"] += added_time
            sub_segment["end"] += added_time
            for word in sub_segment['words']:
                word["start"] += added_time
                word["end"] += added_time
            combined_segments.append(sub_segment)
    return combined_segments


def combine_sentences_from_json(combined_result_json):
    text_val = ""
    try:
        for segment in combined_result_json['segments']:
            text_val = text_val + segment['text']
            text_val = text_val + "\n"
    except Exception as e:
        print(f"Error while compiling text from json transcipt : {e}")
    return text_val

def save_output_files(dest_folder, whisper_transcription, full_text):
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)
    if dest_folder[-1] != "/":
        dest_folder = dest_folder + "/"

    transcript_path = dest_folder + "_whisper_transcription.json"
    text_path = dest_folder + "_plain_text.txt"

    saved_files = []
    try:
        with open(transcript_path, "w", encoding="utf-8") as f:
            json.dump(whisper_transcription, f, indent=2, ensure_ascii=False)
            saved_files.append(transcript_path)
    except Exception as e:
        print(f"{inspect.currentframe().f_code.co_name}:{inspect.currentframe().f_lineno} Failed to save '{transcript_path}' : {e}")

    try:
        if full_text:
            with open(text_path, "w", encoding="utf-8") as f:
                f.write(full_text)
                saved_files.append(text_path)
    except Exception as e:
        print(f"{inspect.currentframe().f_code.co_name}:{inspect.currentframe().f_lineno} Failed to save '{text_path}' : {e}")

    return saved_files