## Install :
Requires Python 3.10 and up.
For Nvidia Boards : https://developer.nvidia.com/cuda-downloads

<!-- C++ Build Tools : https://visualstudio.microsoft.com/fr/visual-cpp-build-tools/
<!-- --> With Desktop SDK for C++ --> -->

```bash
!pip install whisper-timestamped
!pip install praatio
!pip install auditok
!pip install transformers
!pip install torch
!pip install pydub
# !pip install webrtcvad pyaudioanalysis scikit-learn hmmlearn eyed3 imblearn plotly
```


## Update : 
```bash
pip3 install --upgrade --no-deps --force-reinstall git+https://github.com/linto-ai/whisper-timestamped
```


## Build
pyinstaller main.py --name audio2praat --add-data 'libs/ffmpeg/bin/ffmpeg.exe;libs/ffmpeg/bin' --add-data 'C:/Users/virgi/.cache/whisper/large-v3.pt;models' --add-data 'C:/Users/virgi/AppData/Local/Programs/Python/Python312/Lib/site-packages/whisper/assets;whisper/assets'