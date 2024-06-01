import numpy as np

def remove_punctuation(in_string):
    punc = '''!()-[]{};:'"\\,<>./?@#$%^&*_~'''
    for ele in in_string:
        if ele in punc:
            in_string = in_string.replace(ele, "")
    return in_string

def mean_amplitude(segment):
    samples = np.array(segment.get_array_of_samples())
    return np.mean(np.abs(samples))