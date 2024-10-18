import os
from pydub import AudioSegment

def split_audio(file_path, segment_length_s):
    try:
        audio = AudioSegment.from_file(file_path)
        segment_length = segment_length_s * 1000
        total_length = len(audio)

        print(f"Audio lenght : {total_length/1000.0}s")

        if not os.path.exists("res/tmp"):
            os.makedirs("res/tmp")

        segments = []
        lengths = []
        i = 0
        start = 0
        while start < total_length:
            end = min(start + segment_length, total_length)
            print(f"Segment {i}  : {start/1000.0}|{end/1000.0}")
            segment = audio[start:end]
            start = end
            segment_filename = os.path.join("res/tmp", f"segment_{i}.wav")
            segment.export(segment_filename, format="wav")
            segments.append(segment_filename)
            lengths.append(len(segment)/1000.0)
            i = i + 1
        lengths.append(0)

        return segments, lengths
    except Exception as e:
        print(f"Error while spliting audio : {e}")
        return None