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
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import sys
import threading
import re

running = False

# Allows for all subprocesses and function to stop directly when clicking the Cross
def on_closing():
    os._exit(0)

gc.enable()

# Allows all usual console output (stdout+stderr) to be printed into the GUI window instead
class RedirectText(object):
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, string):
        pattern = r'\d+%[^\n]*'

        # Use re.findall() to find all matches in the input string
        matches = re.findall(pattern, string)
        if matches:
            # Deleting the last line to prevent the progress bar from being duplicated over and over... TODO : Find a way to print it smoothly...
            self.text_widget.delete("end-2l", "end-1l")
            self.text_widget.insert(tk.END, matches[-1] + '\n')
        else:
            self.text_widget.insert(tk.END, string)
        self.text_widget.see(tk.END)
        self.text_widget.update_idletasks()  # Force update to ensure real-time display

    def flush(self):
        pass

# Utility function to fetch target file/folder
def browse_file(var):
    filename = filedialog.askopenfilename()
    var.set(filename)

def browse_folder(var):
    foldername = filedialog.askdirectory()
    var.set(foldername)


# Tkinter GUI window definition
root = tk.Tk()
root.title("simpleTranscription")
root.geometry("800x600")
root.protocol("WM_DELETE_WINDOW", on_closing)

# Variable definition
model_var = tk.StringVar(value="tiny")
vad_var = tk.BooleanVar(value=False)
detect_disfluencies_var = tk.BooleanVar(value=False)
language_var = tk.StringVar(value="french")
output_folder_var = tk.StringVar(value="output/S5")
file_path_var = tk.StringVar(value="res/entretien.wav")
segment_length_s_var = tk.IntVar(value=40)
device_var = tk.StringVar(value="cpu")

# Defining all possible parameters to create window. TODO : Make a single list of them instead of having 'fields' + 'params'... Too much hard-coded..
fields = [
    ("Language", language_var),
    ("Output Folder", output_folder_var, browse_folder),
    ("File Path", file_path_var, browse_file),
    ("Segment Length (s)", segment_length_s_var),
    ("Device", device_var),
]

def transcribe_segment(segment, device_str, model_str, vad, detect_disfluencies, language):
    gc.collect()
    devices = torch.device(device_str)
    try:
        if os.path.isfile("models/large-v3.pt"):
            model = whisper.load_model("models/large-v3.pt", device=devices)
        else:
            print("Model not found in 'models/' folder. Trying to download/load it from cache.")
            model = whisper.load_model("small", device=devices) # try to download it
        result = whisper.transcribe(model, segment, vad=vad, detect_disfluencies=detect_disfluencies, language=language)
    except Exception as e:
        print(f"Failed to transcribe with exception : {e}")
        return None
    return result

def transcribe_from_file(file_path, device_str="cpu", output_folder="", model="", vad=False, detect_disfluencies=False, language="french", segment_length_s=40):

    segments, lengths = audio_handler.split_audio(file_path, segment_length_s)

    print("Whisper starting...")
    transcription_segments = []
    for segment in segments:
        audio = whisper.load_audio(segment)
        transcription_pt = transcribe_segment(audio, device_str, model, vad, detect_disfluencies, language)
        if transcription_pt:
            transcription_segments.append(transcription_pt)
        else:
            return None

    combined_results = {
        "segments": file_handler.adjust_segments(transcription_segments, lengths)
    }

    full_text = None
    try:
        full_text = file_handler.combine_sentences_from_json(combined_results)
    except Exception as e:
        print(f"{inspect.currentframe().f_code.co_name}:{inspect.currentframe().f_lineno} Error while creating textgrid : {e}")

    file_handler.save_output_files(output_folder, combined_results, full_text)

    return full_text


# Main program function, launched as a separate Thread to make it independant from GUI rendering thread (which is the main thread)
def run_program():
    params = {
        "language": language_var.get(),
        "output_folder": output_folder_var.get(),
        "file_path": file_path_var.get(),
        "segment_length_s": segment_length_s_var.get(),
        "device": device_var.get(),
    }

    print("\n###########################################")
    print(f"Starting transcription for '{params["file_path"]}' :")
    print("\n###########################################")
    print("Settings : ")
    print(f"Selected language : {params["language"]}")
    print(f"Audio file path : {params["file_path"]}")
    print(f"Audio segment length : {params["segment_length_s"]}s")
    print(f"Processing device : {params["device"]}")
    print(f"Output folder : {params["output_folder"]}")
    print("###########################################")
    print(f"Transcribing with model : Whisper-small")
    start_time = np.int32(time.time())
    if file_handler.checkFilePaths(params["file_path"]) == 0:
        print("Pre-processing...")
        extracted_text = transcribe_from_file(file_path=params["file_path"], device_str=params["device"], output_folder=params["output_folder"], model=model_var, vad=False, detect_disfluencies=False, language=params["language"], segment_length_s=params["segment_length_s"])
        gc.collect()
        end_time = np.int32(time.time())
        execution_time_min = (end_time - start_time) // 60
        execution_time_sec = (end_time - start_time) % 60

        print(f"Total transcription time : {execution_time_min}m{execution_time_sec}s")

        if extracted_text == None:
            messagebox.showinfo("Info", "Failed transcribing\n")
        else:
            messagebox.showinfo("Info", "Done transcribing\n")
    else:
        messagebox.showinfo("Info", "At least one input file couldn't be found\n")
        # Thread management
    global running
    running = False

def start_task():
    global running
    if not running:
        transcription_thread = threading.Thread(target=run_program)
        transcription_thread.start()
        running = True

if __name__ == "__main__":

    languages = ["dutch", "spanish", "korean", "italian", "german", "thai", "russian", "portuguese", "polish", "indonesian", "mandarin", "swedish", "czech", "english", "japanese", "french", "romanian", "cantonese", "turkish", "mandarin", "catalan", "hungarian", "ukrainian", "greek", "bulgarian", "arabic", "serbian", "macedonian", "cantonese", "latvian", "slovenian", "hindi", "galician", "danish", "urdu", "slovak", "hebrew", "finnish", "azerbaijani", "lithuanian", "estonian", "nynorsk", "welsh", "punjabi", "afrikaans", "persian", "basque", "vietnamese", "bengali", "nepali", "marathi", "belarusian", "kazakh", "armenian", "swahili", "tamil", "albanian"]
    devices = ["cpu"]
    if torch.cuda.is_available():
        free_mem, global_mem = torch.cuda.mem_get_info()
        if free_mem > 10000000000:
            devices.append("cuda:0")

    # Creating the GUI window option with all the parameters
    for field in fields:
        frame = tk.Frame(root)
        label = tk.Label(frame, text=field[0])
        label.pack(side="left")
        
        if field[0] == "Language":
            combobox = ttk.Combobox(frame, textvariable=field[1], values=languages, state='readonly')
            combobox.pack(side="left", fill="x", expand=True)
        elif field[0] == "Device":
            combobox = ttk.Combobox(frame, textvariable=field[1], values=devices, state='readonly')
            combobox.pack(side="left", fill="x", expand=True)
        else:
            entry = tk.Entry(frame, textvariable=field[1])
            entry.pack(side="left", fill="x", expand=True)
            if len(field) > 2:
                button = tk.Button(frame, text="Browse", command=lambda var=field[1], cmd=field[2]: cmd(var))
                button.pack(side="right")
        
        frame.pack(fill="x")

    run_button = tk.Button(root, text="Run Program", command=start_task)
    run_button.pack(pady=10)

    console_frame = tk.Frame(root)
    console_frame.pack(fill="both", expand=True)

    console_label = tk.Label(console_frame, text="Console Output")
    console_label.pack()

    console_text = tk.Text(console_frame, height=10)
    console_text.pack(fill="both", expand=True)

    # Redirect stdout to the Text widget
    sys.stdout = RedirectText(console_text)
    sys.stderr = RedirectText(console_text)

    if torch.cuda.is_available():
        free_mem, global_mem = torch.cuda.mem_get_info()
        print("GPU Detected, available memory : {:2.2f}/{:2.2f} Go".format(free_mem/1000000000, global_mem/1000000000))
        if free_mem > 4e9:
            print("GPU has enough memory.")
            try:
                torch.cuda.empty_cache()
            except Exception as e:
                print("Failed to set CUDA parameters...")
        else:
            print("GPU doesn't have enough memory.")

    root.mainloop()