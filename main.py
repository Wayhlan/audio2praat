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


def transcribe_segment(segment, model_string, vad, detect_disfluencies, language):
    devices = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    model = whisper.load_model(model_string, device=devices)
    result = whisper.transcribe(model, segment, vad=vad, detect_disfluencies=detect_disfluencies, language=language)
    return result

def transcribe_from_file(file_path, output_folder="", model_string="large", vad=False, detect_disfluencies=False, language="vietnamese", segment_length_s=60):

    start_time = np.int32(time.time())
    segments, lengths = audio_handler.split_audio(file_path, segment_length_s)

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

    end_time = np.int32(time.time())
    execution_time_min = (end_time - start_time) // 60
    execution_time_sec = (end_time - start_time) % 60
    print(f"Done transcribing\nTotal transcription time : {execution_time_min}m{execution_time_sec}s")
    return textgrid_val

if __name__ == "__main__":
    # Choose from ["tiny", "base", "small", "medium", "large", "large-v2", "large-v3"]
    model = "tiny"
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