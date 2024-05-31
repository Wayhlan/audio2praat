
def remove_punctuation(in_string):
    punc = '''!()-[]{};:'"\\,<>./?@#$%^&*_~'''
    for ele in in_string:
        if ele in punc:
            in_string = in_string.replace(ele, "")
    return in_string