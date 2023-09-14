#!/bin/sh


#< arecord -l
#> **** List of CAPTURE Hardware Devices ****
#> card 3: UM02 [UM02], device 0: USB Audio [USB Audio]
#>   Subdevices: 1/1
#>   Subdevice #0: subdevice #0

#< arecord -D plughw:<card number>,<device number>  --duration= <seconds> nameoffile.wav
arecord -D plughw:3,0  --duration=5 ~/record-test.wav

aplay ~/record-test.wav

rm ~/record-test.wav

