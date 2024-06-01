import os
import numpy as np
import json
from praatio import textgrid
import inspect

import utils

VIET_TARGET_WORDS = ["pháp", "áp", "bát", "phát", "lác", "lắc", "gác", "đám", "khám", "bán", "gián", "đáng", "sáng"]
VIET_TARGET_WORDS_PRINT = ["phap", "ap", "bat", "phat", "lac", "lac", "gac", "dam", "kham", "ban", "gian", "dang", "sang"]
VIET_COMPOSED_TARGETS = ["pháp lý", "áp bức", "bát ngát", "phát giác", "lác đác", "lắc đắc", "gác bút", "đám cưới", "khám phá", "bán kết", "gián tiếp", "đáng kính", "sáng kiến"]
VIET_COMPOSED_TARGETS_PRINT = ["phap ly", "ap buc", "bat ngat", "phat giac", "lac dac", "lac dac", "gac but", "dam cuoi", "kham pha", "ban ket", "gian tiep", "dang kinh", "sang kien"]

def json_to_textgrid(transcription_result, target_words = VIET_TARGET_WORDS, target_composed = VIET_COMPOSED_TARGETS):
    text = combine_sentences_from_json(transcription_result)
    sentences = []
    words = []
    t_words = []
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
                            # print(f"Found {target_composed[id_target].lower()} at {word_start}s")
                            idx = idx + 1
                            continue
                    targets_counters[id_target] = targets_counters[id_target] + 1
                    t_words.append((word_start, word_end, (str(targets_counters[id_target]) + " - " + word_text.lower())))
                    # print(f"Found {target_words[id_target].lower()} at {word_start}s")

    for idt in range(nb_targets):
        try:
            if targets_counters[idt] > 0:
                print(f"Found x{targets_counters[idt]} : {VIET_TARGET_WORDS_PRINT[idt]}")
            if composed_targets_counters[idt] > 0:
                print(f"Found x{composed_targets_counters[idt]} : {VIET_COMPOSED_TARGETS_PRINT[idt]}")
        except Exception as e:
            print("Failed to print found word due to encoding issues.")

    tg = textgrid.Textgrid()
    end_time = max(segment['end'] for segment in transcription_result['segments'])

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
