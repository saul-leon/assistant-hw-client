#!/bin/sh

sudo apt update
sudo apt install python3 python3-pyaudio python3-pip libatlas-base-dev portaudio19-dev

INSTALL_DIR=`pwd`
cd ~/
sudo apt install libpcre2-dev
wget https://downloads.sourceforge.net/swig/swig-4.1.1.tar.gz
tar zxvf swig-4.1.1.tar.gz
cd swig-4.1.1/
./configure --prefix=/usr
make
sudo make install
rm -rf swig-4.1.1*

cd $INSTALL_DIR/snowboy
make
cp _snowboydetect.so snowboydetect.py ../../src/
make clean

cd $INSTALL_DIR
pip3 install -r requirements.txt
