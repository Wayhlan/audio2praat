import os
from pydub import AudioSegment
import numpy

def split_audio(file_path, segment_length_s):
    try:
        audio = AudioSegment.from_file(file_path)
        segment_length = segment_length_s * 1000
        total_length = len(audio)

        print(f"Audio lenght : {total_length}")

        if not os.path.exists("res/tmp"):
            os.makedirs("res/tmp")

        segments = []
        lengths = []
        i = 0
        for start in range(0, total_length, segment_length):
            end = min(start + segment_length, total_length)
            print(f"Spliting at  : {start}|{end}")
            segment = audio[start:end]
            segment_filename = os.path.join("res/tmp", f"segment_{i}.wav")
            segment.export(segment_filename, format="wav")
            segments.append(segment_filename)
            lengths.append(numpy.int32(len(segment)/1000))
            i = i + 1
        lengths.append(0)
        
        return segments, lengths
    except Exception as e:
        print(f"Error while spliting audio : {e}")
        return None