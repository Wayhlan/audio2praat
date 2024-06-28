import os
import numpy as np
import json
from praatio import textgrid
import inspect

import utils

def getPhonemes(split_words_targets, target_idx, word_start, word_stop, composed_word, composed_end=9999):
    split_words = []
    if split_words_targets:
        word_duration = word_stop - word_start
        if composed_word != "": 
            word_duration = word_duration / 2.0
        phonemes = split_words_targets[target_idx]

        start = word_start
        stop = start
        for i in range(len(phonemes)):
            stop = stop + word_duration * ( float(1)/float(len(phonemes)))
            if stop >= word_stop:
                stop = word_stop - 0.0001
            split_words.append((start, stop, phonemes[i]))
            start = stop
        if composed_word != "":
            split_words.append((start, composed_end, composed_word))
    return split_words

def checkFilePaths(file_path, target_words_path, target_split_words_path, target_composed_path):
    try:
        if target_split_words_path != "" and not os.path.isfile(target_split_words_path):
            print(f"{inspect.currentframe().f_code.co_name}:{inspect.currentframe().f_lineno} Failed to load input file : {target_split_words_path}")
            return -1
        if target_words_path != "" and not os.path.isfile(target_words_path):
            print(f"{inspect.currentframe().f_code.co_name}:{inspect.currentframe().f_lineno} Failed to load input file : {target_words_path}")
            return -1
        if target_composed_path != "" and not os.path.isfile(target_composed_path):
            print(f"{inspect.currentframe().f_code.co_name}:{inspect.currentframe().f_lineno} Failed to load input file : {target_composed_path}")
            return -1
        if file_path != "" and not os.path.isfile(file_path):
            print(f"{inspect.currentframe().f_code.co_name}:{inspect.currentframe().f_lineno} Failed to load input file : {file_path}")
            return -1
    except Exception as e:
        print(f"{inspect.currentframe().f_code.co_name}:{inspect.currentframe().f_lineno} Failed to load input file : \n{e}")
        return -1
    return 0

# TODO : Big and ugly.. find a way to split that...
def json_to_textgrid(transcription_result, target_words_path = "res/target_words.txt", target_split_words_path="", target_composed_path = "res/target_composed.txt", target_composed_split_path=""):
    text = combine_sentences_from_json(transcription_result)

    try:
        target_split_words = []
        target_words = []
        target_composed = []
        target_split_composed = []
        if target_split_words_path != "":
            with open(target_split_words_path, 'r', encoding='utf-8') as file:
                for line in file:
                    words = line.strip().split()
                    target_split_words.append(words)
        if target_words_path != "":
            with open(target_words_path, 'r', encoding='utf-8') as file:
                for line in file:
                    target_words.append(line.strip())
        if target_composed_path != "":
            with open(target_composed_path, 'r', encoding='utf-8') as file:
                for line in file:
                    target_composed.append(line.strip())
        if target_composed_split_path != "":
            with open(target_composed_split_path, 'r', encoding='utf-8') as file:
                for line in file:
                    target_split_composed.append(line.strip())
    except Exception as e:
        print(f"{inspect.currentframe().f_code.co_name}:{inspect.currentframe().f_lineno} Failed to load target (composed) words : \n{e}")

    sentences = []
    words = []
    t_words = []
    split_words = []
    nb_targets = 0
    if target_words:
        nb_targets = len(target_words)
        targets_counters = np.zeros(nb_targets).astype(np.int32)
        composed_targets_counters = np.zeros(nb_targets).astype(np.int32)
    print("\n")

    prev_end = 0.0
    for segment in transcription_result['segments']:
        sentence_start = max(segment['start'], prev_end)
        sentence_end = segment['end']
        sentence_text = segment['text']
        if sentence_start < sentence_end:
            sentences.append((sentence_start, sentence_end, sentence_text))
            prev_end = sentence_end
        else:
            print(f"Skipping a sentence at {sentence_start}")
        

        nb_words = len(segment['words'])
        prev_w_end = 0.0
        for idx in range(nb_words):
            word_start = segment['words'][idx]['start']
            word_end = segment['words'][idx]['end']
            word_text = segment['words'][idx]['text']
            words.append((max(word_start, prev_w_end), word_end, word_text))
            prev_w_end = word_end

            for id_target in range(nb_targets):
                if target_words[id_target].lower() == utils.remove_punctuation(word_text.lower()):
                    if idx < (nb_words-1):
                        second_part = target_composed[id_target].lower().split()[1]
                        next_word = segment['words'][idx+1]['text']
                        if second_part == utils.remove_punctuation(next_word.lower()):
                            composed_targets_counters[id_target] = composed_targets_counters[id_target] + 1
                            t_words.append((word_start, segment['words'][idx+1]['end'], (str(composed_targets_counters[id_target]) + " - " + target_composed[id_target].lower())))
                            phonemes = getPhonemes(target_split_words, id_target, word_start, word_end, target_split_composed[id_target], segment['words'][idx+1]['end'])
                            for phoneme in phonemes:
                                split_words.append(phoneme)
                            # print(f"Found {target_composed[id_target].lower()} at {word_start}s")
                            idx = idx + 1
                            continue
                    targets_counters[id_target] = targets_counters[id_target] + 1
                    t_words.append((word_start, word_end, (str(targets_counters[id_target]) + " - " + word_text.lower())))
                    phonemes = getPhonemes(target_split_words, id_target, word_start, word_end, "")
                    for phoneme in phonemes:
                        split_words.append(phoneme)
                    # print(f"Found {target_words[id_target].lower()} at {word_start}s")

    for idt in range(nb_targets):
        try:
            if targets_counters[idt] > 0:
                print(f"Found x{targets_counters[idt]} : {target_words[idt]}")
            if composed_targets_counters[idt] > 0:
                print(f"Found x{composed_targets_counters[idt]} : {target_composed[idt]}")
        except Exception as e:
            print("Failed to print found word due to encoding issues.")

    tg = textgrid.Textgrid()
    end_time = max(segment['end'] for segment in transcription_result['segments'])


    try:
        t_phon_tier = textgrid.IntervalTier('phonèmes', split_words, 0, end_time)
    except Exception as e:
        print(f"{inspect.currentframe().f_code.co_name}:{inspect.currentframe().f_lineno} Failed to create textGrid tier 'phonèmes', leaving empty.")
        print(f"{e}")
        t_phon_tier = textgrid.IntervalTier('phonèmes', [], 0, end_time)
    tg.addTier(t_phon_tier)

    try:
        t_word_tier = textgrid.IntervalTier('n°', t_words, 0, end_time)
    except Exception as e:
        print(f"{inspect.currentframe().f_code.co_name}:{inspect.currentframe().f_lineno} Failed to create textGrid tier 'n°', leaving empty.")
        print(f"{e}")
        t_word_tier = textgrid.IntervalTier('n°', [], 0, end_time)
    tg.addTier(t_word_tier)

    try:
        sentence_tier = textgrid.IntervalTier('phrases', sentences, 0, end_time)
    except Exception as e:
        print(f"{inspect.currentframe().f_code.co_name}:{inspect.currentframe().f_lineno} Failed to create textGrid tier 'phrases', leaving empty.")
        print(f"{e}")
        sentence_tier = textgrid.IntervalTier('phrases', [], 0, end_time)
    tg.addTier(sentence_tier)

    try:
        discours_tier = textgrid.IntervalTier('discours', [(0, end_time, text)], 0, end_time)
    except Exception as e:
        print(f"{inspect.currentframe().f_code.co_name}:{inspect.currentframe().f_lineno} Failed to create textGrid tier 'discours', leaving empty.")
        print(f"{e}")
        discours_tier = textgrid.IntervalTier('discours', [], 0, end_time)
    tg.addTier(discours_tier)

    return tg, text

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
            text_val = text_val + " "
    except Exception as e:
        print(f"Error while compiling text from json transcipt : {e}")
    return text_val

def save_output_files(dest_folder, tag, whisper_transcription, textgrid_val, full_text):
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)
    if dest_folder[-1] != "/":
        dest_folder = dest_folder + "/"

    transcript_path = dest_folder + tag + "_whisper_transcription.json"
    grid_path = dest_folder + tag + "_grid.TextGrid"
    text_path = dest_folder + tag + "_plain_text.txt"

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

    try:
        if textgrid_val:
            textgrid_val.save(grid_path, format="short_textgrid", includeBlankSpaces=True)
            saved_files.append(grid_path)
    except Exception as e:
        print(f"{inspect.currentframe().f_code.co_name}:{inspect.currentframe().f_lineno} Failed to save '{grid_path}' : {e}")

    return saved_files


##############################################
############### UNUSED CODE ##################
##############################################


def combine_sentences_from_whisperX(combined_result_json):
    text_val = ""
    try:
        output = combined_result_json['output']
        for segment in output['segments']:
            text_val = text_val + segment['text']
            text_val = text_val + " "
    except Exception as e:
        print(f"Error while compiling text from json transcipt : {e}")
    return text_val
def whisperX_to_textgrid(transcription_result, target_words_path = "res/target_words.txt", target_composed_path = "res/target_composed.txt"):
    text = combine_sentences_from_whisperX(transcription_result)

    try:
        target_words = []
        target_composed = []
        with open(target_words_path, 'r', encoding='utf-8') as file:
            for line in file:
                target_words.append(line.strip())
        with open(target_composed_path, 'r', encoding='utf-8') as file:
            for line in file:
                target_composed.append(line.strip())
    except Exception as e:
        print(f"{inspect.currentframe().f_code.co_name}:{inspect.currentframe().f_lineno} Failed to load target (composed) words : {e}")

    sentences = []
    words = []
    t_words = []
    nb_targets = len(target_words)
    targets_counters = np.zeros(nb_targets).astype(np.int32)
    composed_targets_counters = np.zeros(nb_targets).astype(np.int32)
    print("\n")

    prev_end = 0.0
    for segment in transcription_result['output']['segments']:
        sentence_start = max(segment['start'], prev_end)
        sentence_end = segment['end']
        sentence_text = segment['text']
        if sentence_start < sentence_end:
            sentences.append((sentence_start, sentence_end, sentence_text))
            prev_end = sentence_end
        else:
            print(f"Skipping a sentence at {sentence_start}")
        

        nb_words = len(segment['words'])
        prev_w_end = 0.0
        for idx in range(nb_words):
            try:
                word_start = segment['words'][idx]['start']
                word_end = segment['words'][idx]['end']
                word_text = segment['words'][idx]['word']
                words.append((max(word_start, prev_w_end), word_end, word_text))
                prev_w_end = word_end

                for id_target in range(nb_targets):
                    if target_words[id_target].lower() == utils.remove_punctuation(word_text.lower()):
                        if idx < (nb_words-1):
                            second_part = target_composed[id_target].lower().split()[1]
                            next_word = segment['words'][idx+1]['word']
                            if second_part == utils.remove_punctuation(next_word.lower()):
                                composed_targets_counters[id_target] = composed_targets_counters[id_target] + 1
                                t_words.append((word_start, segment['words'][idx+1]['end'], (str(composed_targets_counters[id_target]) + " - " + target_composed[id_target].lower())))
                                # print(f"Found {target_composed[id_target].lower()} at {word_start}s")
                                idx = idx + 1
                                continue
                        targets_counters[id_target] = targets_counters[id_target] + 1
                        t_words.append((word_start, word_end, (str(targets_counters[id_target]) + " - " + word_text.lower())))
                        # print(f"Found {target_words[id_target].lower()} at {word_start}s")
            except Exception as e:
                continue

    for idt in range(nb_targets):
        try:
            if targets_counters[idt] > 0:
                print(f"Found x{targets_counters[idt]} : {target_words[idt]}")
            if composed_targets_counters[idt] > 0:
                print(f"Found x{composed_targets_counters[idt]} : {target_composed[idt]}")
        except Exception as e:
            print("Failed to print found word due to encoding issues.")

    tg = textgrid.Textgrid()
    end_time = max(segment['end'] for segment in transcription_result['output']['segments'])

    t_phon_tier = textgrid.IntervalTier('phonèmes', [], 0, end_time)
    tg.addTier(t_phon_tier)

    try:
        t_word_tier = textgrid.IntervalTier('n°', t_words, 0, end_time)
    except Exception as e:
        print(f"{inspect.currentframe().f_code.co_name}:{inspect.currentframe().f_lineno} Failed to create textGrid tier 'n°', leaving empty. {e}")
        t_word_tier = textgrid.IntervalTier('n°', [], 0, end_time)
    tg.addTier(t_word_tier)

    try:
        sentence_tier = textgrid.IntervalTier('phrases', sentences, 0, end_time)
    except Exception as e:
        print(f"{inspect.currentframe().f_code.co_name}:{inspect.currentframe().f_lineno} Failed to create textGrid tier 'phrases', leaving empty. {e}")
        sentence_tier = textgrid.IntervalTier('phrases', [], 0, end_time)
    tg.addTier(sentence_tier)

    try:
        discours_tier = textgrid.IntervalTier('discours', [(0, end_time, text)], 0, end_time)
    except Exception as e:
        print(f"{inspect.currentframe().f_code.co_name}:{inspect.currentframe().f_lineno} Failed to create textGrid tier 'discours', leaving empty. {e}")
        discours_tier = textgrid.IntervalTier('discours', [], 0, end_time)
    tg.addTier(discours_tier)

    return tg, text