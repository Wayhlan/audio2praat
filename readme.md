# Requirements
Execution :  
12 Go RAM minimum  
(10 Go GPU on Nvidia cards only, will run on CPU otherwise)  
Build :  
Python 3.10 and up  

# Execution from pre-built folder  
1.2.0 On google drive : https://drive.google.com/file/d/1ESl6ZVZYg8lZczvpWNYtfp89EGXe34mT/view?usp=drive_link  
## Prerequisite
- An input audio file, can be .wav, .mp3 (not tested with others)  
- Target words, composed words and phonemes should be optionnal, only the sentence-level transcription will be produced if no input file is given  

### Input files format
Target words, and other input file need to be text files with a single target per line. For the phoneme file, each line contains all the target's phoneme, separated by spaces    
The input files need to have the same target counts (if 5 words, 5 phonemes (5 composed words, 5 composed phonemes)) Example :  
#### Target words
```bash
black
she
blue
clock
```
#### Target phonemes
```bash
b l a k
sh ee
b l oo
k l o k
```

### Produced output
A Praat ".textGrid" file is always produced, that file contains 4 tiers :   
- A 'discours' Tier, containing the whole transcription as text. This part is always produced.  
- A 'phrases' Tier, containing the different phrases, timestamped. This part is always produced.  
- A 'n°' Tier, containing the target words, if they were provided in an input file.  
- A 'phonèmes' Tier, containing the target phonèmes, if they were provided in an input file.  
It is possible to search for composed words as well (by adding the corresponding input files). Note : The second par of the composed word will not be split into phonemes.  
Example of composed input files :  
#### Target composed words 
```bash
black sheep
she is
```

Note : Target composed words will only be searched if their first word is present at the same line in the input target words...! (TODO : Fix that?)  
#### Target phonemes
```bash
b l a k
sh ee
```





# Installation for build + python execution :  
Python : https://www.python.org/downloads/windows/  
FFMPEG : https://ffmpeg.org
For Nvidia Boards : https://developer.nvidia.com/cuda-downloads  

```bash
pip install whisper-timestamped
pip install praatio
pip install auditok
pip install transformers
pip install torch
pip install pydub
```

## Update if necessary : 
```bash
pip3 install --upgrade --no-deps --force-reinstall git+https://github.com/linto-ai/whisper-timestamped
```

## Execution from python command line

Simply this command from any console :  
```bash
python main.py
```

## Build standalone executable :
Change USERNAME with actual UserName and potentially adapt paths to fit your install locations.  
```bash
pyinstaller main.py --name audio2praat --add-data 'libs/ffmpeg/bin/ffmpeg.exe;libs/ffmpeg/bin' --add-data 'C:/Users/USERNAME/.cache/whisper/large-v3.pt;models' --add-data 'C:/Users/USERNAME/AppData/Local/Programs/Python/Python312/Lib/site-packages/whisper/assets;whisper/assets'
```

Note : Possibility to add the "--onefile" option to package everything inside the .exe ; Might be hard to debug if there is a missing lib...  
  
This will produce a 'dist/' folder containing :  
.  
└── dist/  
    ├── _internal/  
    │   ├── models/  
    │   ├── libs/  
    │   └── ...  
    └── audio2praat.exe  
  
Both 'models/' and 'libs/' directories need to be moved outside of the '_internal/' directory to obtain a final folder :  
.  
└── dist/  
    ├── _internal/  
    ├── models/  
    ├── libs/  
    └── audio2praat.exe 

## Google collabs
https://colab.research.google.com/drive/1dEhvDJuB7zvBvst_hJ4-mDInOvBXcOum?usp=sharing  
  
Note : colab outdated now...
