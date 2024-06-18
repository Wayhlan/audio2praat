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
import gc
import audio_handler
import file_handler
import json

gc.enable()

def transcribe_segment(segment, device_str, model_string, vad, detect_disfluencies, language):
    gc.collect()
    devices = torch.device(device_str)
    try:
        if os.path.isfile("models/large-v3.pt"):
            model = whisper.load_model("models/large-v3.pt", device=devices)
        else:
            print("Model not found in 'models/' folder. Trying to download/load it from cache.")
            model = whisper.load_model("large", device=devices) # try to download it
        result = whisper.transcribe(model, segment, vad=vad, detect_disfluencies=detect_disfluencies, language=language)
    except Exception as e:
        print(f"Failed to transcribe with exception : {e}")
        return None
    return result

def transcribe_from_file(file_path, t_words_path, t_words_split_path, t_composed_path, t_composed_split_path, device_str="cpu", possible_cuts=[], output_folder="", model_string="large", vad=False, detect_disfluencies=False, language="vietnamese", segment_length_s=60):

    segments, lengths = audio_handler.split_audio(file_path, segment_length_s, possible_cuts)

    print("Whisper starting...")
    transcription_segments = []
    for segment in segments:
        audio = whisper.load_audio(segment)
        transcription_pt = transcribe_segment(audio, device_str, model_string, vad, detect_disfluencies, language)
        if transcription_pt:
            transcription_segments.append(transcription_pt)
        else:
            return None

    combined_results = {
        "segments": file_handler.adjust_segments(transcription_segments, lengths)
    }

    textgrid_val, full_text = None, None
    try:
        textgrid_val, full_text = file_handler.json_to_textgrid(combined_results, target_words_path=t_words_path, target_split_words_path=t_words_split_path, target_composed_path=t_composed_path, target_composed_split_path=t_composed_split_path)
    except Exception as e:
        print(f"{inspect.currentframe().f_code.co_name}:{inspect.currentframe().f_lineno} Error while creating textgrid : {e}")

    file_handler.save_output_files(output_folder, model_string, combined_results, textgrid_val, full_text)

    return textgrid_val

if __name__ == "__main__":
    model = "large"
    vad = False
    detect_disfluencies = False
    language="vi"
    output_folder = "output/test_2"
    file_path = "res/Minh_1.wav"
    segment_length_s=80
    words_path = "res/target_words.txt"
    words_split_path = "res/target_words_phonemes.txt"
    composed_path = "res/target_composed.txt"
    composed_split_path = "res/target_composed_phonemes.txt"
    device = "cpu"
    if torch.cuda.is_available():
        free_mem, global_mem = torch.cuda.mem_get_info()
        print("GPU Detected, available memory : {:2.2f}/{:2.2f} Go".format(free_mem/1000000000, global_mem/1000000000))
        if free_mem > 10000000000:
            device = "cuda:0"
            try:
                torch.cuda.empty_cache()
            except Exception as e:
                print("Failed to set CUDA parameters...")

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
    print(f"[6] Target words file path : {words_path}")
    print(f"[7] Target words splits : {words_split_path}")
    print(f"[8] Target composed words file path : {composed_path}")
    print(f"[9] Target composed words splits file path : {composed_split_path}")
    print(f"[10] Processing device : {device}")
    print(f"[11] Output folder : {output_folder}")
    
    user_command = input("Enter setting number to change (Just press Enter to skip):")
    while user_command != "":
        try:
            value = int(user_command)
            if value < 1 or value > 11:
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
            if value == 6:
                words_path = input("Target words file path = ")
            if value == 7:
                words_split_path = input("Target split words file path = ")
            if value == 8:
                composed_path = input("Target composed words file path = ")
            if value == 9:
                composed_split_path = input("Target split composed words file path = ")
            if value == 10:
                if device == "cpu":
                    print("\nNo GPU available... Or not enough memory available on it.\nIf an NVIDIA GPU is available, make sure the drivers are setup : https://developer.nvidia.com/cuda-downloads\n")
                else:
                    choice = int(input("Device to use (Enter '1' for CPU ; '2' for GPU) "))
                    if choice==1:
                        device = "cpu"
                    elif choice==2:
                        device = "cuda:0"
            if value == 11:
                output_folder = input("Output folder = ")
            user_command = input("Enter setting number to change (Just press Enter to skip):")
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
    print(f"Audio segment length : {segment_length_s}s")
    print(f"Target words file path : {words_path}")
    print(f"Target words splits : {words_split_path}")
    print(f"Target composed words file path : {composed_path}s")
    print(f"Processing device : {device}")
    print(f"Output folder : {output_folder}")
    print("###########################################")
    print(f"Transcribing with model : Whisper-{model}")
    start_time = np.int32(time.time())
    print("Pre-processing...")
    possible_cuts = audio_handler.find_possible_cuts(file_path)
    if file_handler.checkFilePaths(words_path, words_split_path, composed_path) == 0:
        files_saved = transcribe_from_file(file_path=file_path, t_words_path=words_path, t_words_split_path=words_split_path, t_composed_path=composed_path, t_composed_split_path=composed_split_path, device_str=device, possible_cuts=possible_cuts, output_folder=output_folder, model_string=model, vad=vad, detect_disfluencies=detect_disfluencies, language=language, segment_length_s=segment_length_s)
        gc.collect()
        end_time = np.int32(time.time())
        execution_time_min = (end_time - start_time) // 60
        execution_time_sec = (end_time - start_time) % 60

        if files_saved == None:
            print("Failed transcribing\n")
        else:
            print(f"Done transcribing\n")
        print(f"Total transcription time : {execution_time_min}m{execution_time_sec}s")
# words_path = "res/target_words.txt"
# words_split_path = "res/target_words_phonemes.txt"
# composed_path = "res/target_composed.txt"
# composed_split_path = "res/target_composed_phonemes.txt"
# with open("output/test_1/large_whisper_transcription.json", 'r', encoding='utf-8') as f:
#     # Load the data from the file
#     data = json.load(f)
#     # file_handler.json_to_textgrid(data, target_words_path=words_path, target_split_words_path=words_split_path, target_composed_path=composed_path)
# tg, t = file_handler.json_to_textgrid(data, target_words_path=words_path, target_split_words_path=words_split_path, target_composed_path=composed_path, target_composed_split_path=composed_split_path)
# tg.save("output/test_1/large___.TextGrid", format="short_textgrid", includeBlankSpaces=True)
