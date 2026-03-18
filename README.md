# CW Oscillator
Simple program to generate tones use for CW (morse) practise and other situations

## 📦 Installation
1. Go to the [latest release page](https://github.com/mEsUsah/cwOscillator/releases/latest), and download the .exe file. 
2. Start the program. This program does not require any installation.
3. Ignore the Windows Defender "unsigned software warning".
- The program will check for new releases on startup.

## 📸 For use on Zoom (and similar solutions)
* Install [Voicemeeter Bananae Advanced mixer](https://vb-audio.com/Voicemeeter/banana.htm)
* Reboot your computer
* Set the output device in CW Oscillator to one of the virtual input devices
* Mix you microphone with the virtual input device
* Use the mixed input on the video call.

## 🖥️ CLI
The program can be started from PowerShell and CMD, with support for startup automation. Run with -h or --help option to get a full set of options.
```cmd
cwOsclillator_x.x.x.exe --help
```

## 💵 Support me!
- This is FOSS (Free and Open Source Software). I build this for fun, and mostly for my own needs. If you like it, find value in it, and would like to support me, please consider to ☕ [buy me a coffee](https://buymeacoffee.com/mesusah)! It would make my day! ❤️

## 🐛 Bugs / features found
- Please add a [issue](https://github.com/mEsUsah/cwOscillator/issues) with found bugs and feature suggestions.

## Source code installation
For running from source and developing:  
⚠️NB! Use Python 3.12  
```cmd
# Activate virtual environment
py -m venv venv
venv\Scripts\actiavate.bat

# Install dependencies
py -m pip install -r .\requirements.txt

# When needed - deactivate virtual environment
deactivate
```

## Running from source
Once installed, the program can be launched from within the virtual environment.
```cmd
py main.py
```

## Build executable from source
Once installed, the program can be built into a single executable:
```cmd
build.bat
```