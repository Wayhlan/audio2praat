# Requirements
Windows 10 an up  
4 Go RAM minimum  

## Usage
- Launch the .exe  
- Use the 'Browse' buttons to specify input audio file (.wav, .mp3 extension tested, could work with others)  
- Optionnaly choose an output directory (will be created if it doesn't exist)  

## Building a standalone executable from sources :
Change USERNAME with actual UserName and potentially adapt paths/python version to fit your install locations.  
```bash
pyinstaller main.py --name exeFile --add-data 'libs/ffmpeg/bin/ffmpeg.exe;libs/ffmpeg/bin' --add-data 'libs/ffmpeg/bin/ffprobe.exe;libs/ffmpeg/bin' --add-data 'libs/ffmpeg/bin/ffplay.exe;libs/ffmpeg/bin' --add-data 'C:/Users/USERNAME/.cache/whisper/small.pt;models' --add-data 'C:/Users/USERNAME/AppData/Local/Programs/Python/Python312/Lib/site-packages/whisper/assets;whisper/assets'
```

This will produce a 'dist/' folder containing :  
.  
└── dist/  
    ├── _internal/  
    │   ├── ...  
    │   ├── models/  
    │   ├── libs/  
    │   └── ...  
    └── exeFile.exe  
  
Both 'models/' and 'libs/' directories need to be moved outside of the '_internal/' directory (and 'models' directory needs to be moved inside the 'libs' dir.) to obtain a final folder :  
.  
└── dist/  
    ├── _internal/  
    ├── libs/models/  
    └── exeFile.exe  
