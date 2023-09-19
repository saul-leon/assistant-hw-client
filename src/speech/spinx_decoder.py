import speech_recognition as sr

def speech_to_text_offline(wav_file):
    text = ""
    r = sr.Recognizer()
    with sr.AudioFile(wav_file) as source:
        audio = r.record(source)  # read the entire audio file

    # recognize speech using Sphinx
    try:
        text = r.recognize_sphinx(audio)        
    except sr.UnknownValueError:
        print("Sphinx could not understand audio")
    except sr.RequestError as e:
        print("Sphinx error; {0}".format(e))
    
    print("Sphinx thinks you said " + text)
    return text