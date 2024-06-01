import os
from pydub import AudioSegment
import numpy as np
import matplotlib.pyplot as plt
import inspect

import utils

def extend_spoken_segment(array, extend_ticks, extended_tag, shortened_tag, null_tag):
    n = len(array)
    filtered_array = array.copy()
    for i in range(n - extend_ticks):
        for k in range(1, extend_ticks + 1):
            cur_val = array[i]
            next_val = array[i+1]
            if cur_val == extended_tag and (next_val == shortened_tag or next_val == null_tag):
                filtered_array[i+k] = cur_val
            if (cur_val == shortened_tag or cur_val == null_tag) and next_val == extended_tag:
                filtered_array[i] = next_val
    return filtered_array


def get_middle_points(tags, step_size_ms):
    middle_points = []
    n = len(tags)
    i = 0
    min_length = 5

    while i < n:
        if tags[i] == 0:
            start = i
            while i < n and tags[i] == 0:
                i += 1
            end = i - 1
            if (end - start) > min_length:
                middle = (start + end) // 2
                middle_points.append(middle * step_size_ms)
        i += 1

    return middle_points

def amplify_audio_below_mean(file_path, amplification_dB=16):
    window_size_ms = 200
    step_size_ms = 50
    audio = AudioSegment.from_file(file_path)

    overall_mean_amplitude = utils.mean_amplitude(audio)

    segment_tag = []
    amplitudes = []
    for start_ms in range(0, len(audio), step_size_ms):
        end_ms = start_ms + window_size_ms
        segment = audio[start_ms:end_ms]
        amp = utils.mean_amplitude(segment)
        amplitudes.append(amp)

        if amp < 100:
            segment_tag.append(0)
        elif amp < overall_mean_amplitude:
            segment_tag.append(500)
        else:
            segment_tag.append(1000)

    final_tags = extend_spoken_segment(segment_tag, 2, 1000, 500, 0)
    middle_points = get_middle_points(final_tags, step_size_ms)

    amplified_audio = audio
    for i, tag in enumerate(final_tags):
        if tag == 500:
            start_ms = i * step_size_ms
            end_ms = start_ms + window_size_ms
            segment = audio[start_ms:end_ms]
            amplified_segment = segment + amplification_dB
            amplified_audio = amplified_audio[:start_ms] + amplified_segment + amplified_audio[end_ms:]

    output_file_path = "res/tmp/amplified_audio.wav"
    amplified_audio.export(output_file_path, format="wav")
    print(f"Saving amplified audio at : {output_file_path}")

    base_samples = audio.get_array_of_samples()
    ampl_samples = amplified_audio.get_array_of_samples()
    time_axis = np.arange(len(base_samples)) / audio.frame_rate

    if len(ampl_samples) < len(base_samples):
        last_elements = base_samples[-(len(base_samples) - len(ampl_samples)):]
        ampl_samples = np.append(ampl_samples, last_elements)

    plt.figure(figsize=(15, 6))
    
    plt.plot(time_axis[::16], base_samples[::16], label='Original Audio', alpha=0.5, color='b')
    plt.plot(time_axis[::16], ampl_samples[::16], label='Amplified Audio', alpha=0.5, color='g')
    
    for point in middle_points:
        plt.axvline(x=point/1000.0, color='r', linestyle='--', label='Possible Cuts' if point == middle_points[0] else "")
        
    plt.title('Original and Amplified Audio')
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude')
    plt.legend()
    plt.grid(True)
    
    # plt.show()
    plt.savefig("res/tmp/audiomodifs.png")
    plt.close()

    return output_file_path, middle_points


def find_possible_cuts(file_path):
    window_size_ms = 200
    step_size_ms = 100
    try:
        audio = AudioSegment.from_file(file_path)
    except Exception as e:
        print(f"{inspect.currentframe().f_code.co_name}:{inspect.currentframe().f_lineno} Error loading file {file_path} : {e}")
        exit()

    segment_tag = []
    for start_ms in range(0, len(audio), step_size_ms):
        end_ms = start_ms + window_size_ms
        segment = audio[start_ms:end_ms]
        amp = utils.mean_amplitude(segment)

        if amp < 100:
            segment_tag.append(0)
        else:
            segment_tag.append(1000)

    return get_middle_points(segment_tag, step_size_ms)

def split_audio(file_path, segment_length_s, possible_cuts):
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
            if end != total_length:
                end = min(possible_cuts, key=lambda x: abs(x - float(end)))
            print(f"Spliting at  : {start/1000.0}|{end/1000.0}")
            segment = audio[start:end]
            start = end
            segment_filename = os.path.join("res/tmp", f"segment_{i}.wav")
            segment.export(segment_filename, format="wav")
            segments.append(segment_filename)
            lengths.append(len(segment)/1000.0)
            i = i + 1
        lengths.append(0)
        print("\n")
        return segments, lengths
    except Exception as e:
        print(f"Error while spliting audio : {e}")
        return None