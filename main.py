import os
current_path = os.environ.get('PATH')
ffmpeg_path = os.path.join(os.getcwd(), r"libs/ffmpeg/bin")
os.environ['PATH'] = ffmpeg_path + os.pathsep + current_path
os.environ['PYTHONIOENCODING'] = 'utf-8'
import whisper_timestamped as whisper
import numpy as np
import torch
import time
import inspect
import audio_handler
import file_handler

import json
import shutil

def transcribe_segment(segment, model_string, vad, detect_disfluencies, language):
    devices = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    model = whisper.load_model("models/large-v3.pt", device=devices)
    result = whisper.transcribe(model, segment, vad=vad, detect_disfluencies=detect_disfluencies, language=language)
    return result

def transcribe_from_file(file_path, possible_cuts=[], output_folder="", model_string="large", vad=False, detect_disfluencies=False, language="vietnamese", segment_length_s=60):

    segments, lengths = audio_handler.split_audio(file_path, segment_length_s, possible_cuts)

    print("Whisper starting...")
    transcription_segments = []
    for segment in segments:
        audio = whisper.load_audio(segment)
        transcription_segments.append(transcribe_segment(audio, model_string, vad, detect_disfluencies, language))

    combined_results = {
        "segments": file_handler.adjust_segments(transcription_segments, lengths)
    }

    textgrid_val, full_text = None, None
    try:
        textgrid_val, full_text = file_handler.json_to_textgrid(combined_results)
    except Exception as e:
        print(f"{inspect.currentframe().f_code.co_name}:{inspect.currentframe().f_lineno} Error while creating textgrid : {e}")

    file_handler.save_output_files(output_folder, model_string, combined_results, textgrid_val, full_text)

    return textgrid_val

if __name__ == "__main__":
    # Choose from ["tiny", "base", "small", "medium", "large", "large-v2", "large-v3"]
    model = "large"
    # vad Voice Activity Detection -> to glue up useful audio segments
    vad = False
    # detect_disfluencies -> to try and detect non-word voice activity
    detect_disfluencies = False
    language="vietnamese"
    output_folder = "output/tes_0"
    file_path = "res/Minh_1.wav"
    segment_length_s=80

    try:
        torch.cuda.empty_cache()
    except Exception as e:
        print("Failed to clear GPU cache, should not be an issue")

    # if torch.cuda.is_available() :
    #     torch.cuda.set_per_process_memory_fraction(0.90)

    # start_time = np.int32(time.time())
    # amplified_audio_path, possible_cuts = audio_handler.amplify_audio_below_mean(file_path)
    # end_time = np.int32(time.time())
    # execution_time_s = (end_time - start_time)
    # print(f"Preprocessing time : {execution_time_s}s")

    print("\nCurrent settings :")
    print(f"[1] Voice Activity Detection (VAD) : {vad}")
    print(f"[2] Disfluencies detection : {detect_disfluencies}")
    print(f"[3] Selected language : {language}")
    print(f"[4] Audio file path : {file_path}")
    print(f"[5] Audio segment length : {segment_length_s}s")
    user_command = input("Enter setting number to change (Just press Enter to skip):")
    while user_command != "":
        try:
            value = int(user_command)
            if value < 1 or value > 5:
                user_command = input("Please give an integer within range :")
            if value == 1:
                vad = bool(input("VAD = (Enter '0' for False ; '1' for True)"))
            if value == 2:
                detect_disfluencies = bool(input("Disfluencies detection = (Enter '0' for False ; '1' for True)"))
            if value == 3:
                language = input("Laguage = ")
            if value == 4:
                file_path = input("File path = ")
            if value == 5:
                segment_length_s = int(input("Segment length (seconds) = "))
            user_command = input("Anything else ? (Just press Enter to skip):")
        except Exception as e:
            print("User input not usable...")
            exit()

    print("\n###########################################")
    print(f"Starting transcription for '{file_path}' :")
    print("\n###########################################")
    print("Settings : ")
    print(f"Voice Activity Detection (VAD) : {vad}")
    print(f"Disfluencies detection : {detect_disfluencies}")
    print(f"Selected language : {language}")
    print(f"Audio file path : {file_path}")
    print(f"Audio segment length : {segment_length_s} s")
    print("###########################################")
    print(f"Transcribing with model : Whisper-{model}")
    if not torch.cuda.is_available():
        print("Transcribing using CPU... This might take a while.\nIf an NVIDIA GPU is available, make sure the drivers are setup : https://developer.nvidia.com/cuda-downloads\n")
    start_time = np.int32(time.time())
    print("Pre-processing...")
    possible_cuts = audio_handler.find_possible_cuts(file_path)
    files_saved = transcribe_from_file(file_path=file_path, possible_cuts=possible_cuts, output_folder=output_folder, model_string=model, vad=vad, detect_disfluencies=detect_disfluencies, language=language, segment_length_s=segment_length_s)

    end_time = np.int32(time.time())
    execution_time_min = (end_time - start_time) // 60
    execution_time_sec = (end_time - start_time) % 60
    print(f"Done transcribing\nTotal transcription time : {execution_time_min}m{execution_time_sec}s")

    # with open("output/testing_no_ampl/small_whisper_transcription.json", 'r', encoding='utf-8') as f:
    #     # Load the data from the file
    #     data = json.load(f)
    # tg, t = file_handler.json_to_textgrid(data)
    # tg.save("output/testing_no_ampl/small___.TextGrid", format="short_textgrid", includeBlankSpaces=True)
