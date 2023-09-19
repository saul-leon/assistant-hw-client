FROM ubuntu:20.04
ARG DEBIAN_FRONTEND=noninteractive
WORKDIR /root
RUN apt-get update -y && \
    apt-get install -y python3.8 python3.8-dev python3-pyaudio python3-pip libatlas-base-dev portaudio19-dev libpcre2-dev wget alsa-base alsa-utils pocketsphinx ffmpeg
COPY . .
RUN cd /root/install/ && \
    wget https://downloads.sourceforge.net/swig/swig-4.1.1.tar.gz && \
    tar zxvf swig-4.1.1.tar.gz && \
    cd swig-4.1.1/ && \
    ./configure --prefix=/usr && \
    make && \
    make install && \
    rm -rf swig-4.1.1* && \
    pip3 install python-config pyaudio numpy requests pynput pydub pygame pocketsphinx SpeechRecognition && \
    alias python='python3' && \
    alias pip='pip3' && \
    alias python3-config='python-config' && \
    cd /root/install/snowboy && \
    make && \
    cp _snowboydetect.so snowboydetect.py ../../src/ && \
    make clean

CMD ["python3", "main.py"] 