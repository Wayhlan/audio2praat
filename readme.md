# Requirements
Windows 10 an up  
4 Go RAM minimum  

## Prerequisite
- An input audio file, can be .wav, .mp3 (not tested with others)  

## Build standalone executable :
Change USERNAME with actual UserName and potentially adapt paths to fit your install locations.  
```bash
pyinstaller main.py --name exeFile --add-data 'libs/ffmpeg/bin/ffmpeg.exe;libs/ffmpeg/bin' --add-data 'C:/Users/USERNAME/.cache/whisper/small.pt;models' --add-data 'C:/Users/USERNAME/AppData/Local/Programs/Python/Python312/Lib/site-packages/whisper/assets;whisper/assets'
```

Note : Possibility to add the "--onefile" option to package everything inside the .exe ; Might be hard to debug if there is a missing lib...  
  
This will produce a 'dist/' folder containing :  
.  
└── dist/  
    ├── _internal/  
    │   ├── models/  
    │   ├── libs/  
    │   └── ...  
    └── exeFile.exe  
  
Both 'models/' and 'libs/' directories need to be moved outside of the '_internal/' directory to obtain a final folder :  
.  
└── dist/  
    ├── _internal/  
    ├── libs/models/  
    └── exeFile.exe  

## Google collabs
https://colab.research.google.com/drive/1dEhvDJuB7zvBvst_hJ4-mDInOvBXcOum?usp=sharing  
  
Note : colab outdated now...
