## Install :
Requires Python 3.10 and up.  
For Nvidia Boards : https://developer.nvidia.com/cuda-downloads  

```bash
pip install whisper-timestamped
pip install praatio
pip install auditok
pip install transformers
pip install torch
pip install pydub
```

## Update : 
```bash
pip3 install --upgrade --no-deps --force-reinstall git+https://github.com/linto-ai/whisper-timestamped
```

## Build standalone executable :
Change USERNAME with actual UserName and potentially adapt paths to fit your install locations.  
```bash
pyinstaller main.py --name audio2praat --add-data 'libs/ffmpeg/bin/ffmpeg.exe;libs/ffmpeg/bin' --add-data 'C:/Users/USERNAME/.cache/whisper/large-v3.pt;models' --add-data 'C:/Users/USERNAME/AppData/Local/Programs/Python/Python312/Lib/site-packages/whisper/assets;whisper/assets'
```
  
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