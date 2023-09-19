# Assistant HW Client

Assistant HW client is a Python app that uses Snowboy Hotword Detection to start recording an audio when user speaks the hotword 'computer' or when user clicks Space key from keyboard. It records the audio max 12 seconds or until user stays silent. 

It creates a 1 channel, 16K rate wav file. The recorded audio will be converted to OGG using ffmpeg and will be sent as base64 encoded file to cloud. The generated OGG response audio file will be downloaded from cloud again and will be played to the user using pygame library which is 44k rate, 2 channels.

Snowboy is a customizable hotword detection engine to create hotwords like "OK Google" or "Alexa". 

## Installation

'install' folder includes the files to build the hotword detector 'Shared Object' which will be used by the snowboy-detect to extend Python codes functionality through C++ and other required build files to build the Assistant HW Client App.

libs folder includes the necessary static libraries which contains the compiled code for snowboy hotword detector that can be linked at compile-time.

Makefile need to be updated accordingly based on where we are compiling the 'Shared Object'. If you are building for arm based device, you need to comment out the line for X64 (line 44), and uncomment for ARM (line 50). If you are building for ubuntu-docker, you need to comment out the line for X64 (line 44), and uncomment for UBUNTU (line 47).

ubuntu64-libsnowboy-detect.a - for Ubuntu builds (tested with Ubuntu 20.04)

osx-libsnowboy-detect.a - for Macos builds (don't need to update Makefile)

## Raspberry build

install.sh script can be used to build the 'Shared Object' on Linux based environment including Raspberry. Makefile needs to be updated accordingly.

It will download all necessary packages and build snowboy hotword detector shared object and copy it to the src where it will be used by snowboy detector python code. It will also download all required python packages using pip.

```bash
  chmod +x install.sh
  ./install.sh
```

## Ubuntu Docker build

Docker commands can be used to build the docker image on the parent folder, Dockerfile contains all the necessary build commands. Makefile needs to be updated accordingly.

On Linux environment for Docker to access your IO devices, you need to include --device /dev/snd. For Windows and Macos, it is not possible to access IO devices using the same command. You need to use pulseaudio as described [here](https://stackoverflow.com/questions/51859636/docker-sharing-dev-snd-on-multiple-containers-leads-to-device-or-resource-bu) to make it work. 

```bash
  docker build -t assistant-hw-client .
  docker run --device /dev/snd -it assistant-hw-client
```

## MACOS build

For a Macos build for the project, first you need to install necessary packages (portaudio, swig, sox, ffmpeg) and if required python and pip.

```bash
  brew install portaudio
  brew install swig
  brew install sox  
  brew install cmu-pocketsphinx
  brew install ffpmeg 
```

You need to install required python packages as well. If required you can define an alias for pip3.

```bash
  alias pip=pip3
  pip install pygame
  pip install pydub
  pip install pynput
  pip install requests
  pip install numpy
  pip install pyaudio
```

Or you can install those package using a single command.

```bash
  cd install
  pip install -r requirements.txt
```

You need to use clang++ instead of g++ on Macos. You don't need to use the make command as there is no successfull atlas build for Macos and also because Makefile is customized for Linux based builds. 

You can run the below commands to build snowboy hotword detector. Please be sure to update below command using your python version on Macos with the correct paths.

```bash
  cd install/snowboy
  clang++ -I. -O3 -fPIC -D_GLIBCXX_USE_CXX11_ABI=0  -bundle -flat_namespace -undefined suppress snowboy-detect-swig.o \
        ./libs/osx-libsnowboy-detect.a -L/usr/local/opt/python@3.9/Frameworks/Python.framework/Versions/3.9/lib/python3.9/config-3.9-darwin -ldl -framework CoreFoundation -lm -ldl -framework Accelerate -o _snowboydetect.so 
  cp _snowboydetect.so snowboydetect.py ../../src/
  rm _snowboydetect.so
```

## Usage/Examples

You need to run below command to start the application. Please be sure to install all required libraries and also ensure that you build the snowboy hotword detector and copy necessary files to required folders.

```bash
  alias python = python3
  python main.py
```

