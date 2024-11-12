from flask import Flask, render_template, request, jsonify
import speech_recognition as sr
from pydub import AudioSegment
import os
import tempfile

app = Flask(__name__)

@app.route('/')
def voice():
    return render_template('voice.html')

@app.route('/recognize', methods=['POST'])
def recognize():
    recognizer = sr.Recognizer()
    audio_file = request.files['audio']
    
    # Save the audio file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as temp_file:
        audio_file.save(temp_file.name)
        temp_wav_file = temp_file.name.replace('.webm', '.wav')

        # Convert webm to wav
        audio = AudioSegment.from_file(temp_file.name, format='webm')
        audio.export(temp_wav_file, format='wav')

    # Try to recognize the speech in the recorded audio
    with sr.AudioFile(temp_wav_file) as source:
        recognizer.adjust_for_ambient_noise(source)
        audio_content = recognizer.record(source)

    try:
        text = recognizer.recognize_google(audio_content)
        os.remove(temp_file.name)
        os.remove(temp_wav_file)
        return jsonify({"text": text})
    except sr.UnknownValueError:
        os.remove(temp_file.name)
        os.remove(temp_wav_file)
        return jsonify({"error": "Sorry, I could not understand the audio."})
    except sr.RequestError as e:
        os.remove(temp_file.name)
        os.remove(temp_wav_file)
        return jsonify({"error": f"Could not request results; {e}"})

if __name__ == '__main__':
    app.run(debug=True)
