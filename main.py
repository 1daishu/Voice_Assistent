from vosk import Model, KaldiRecognizer
import speech_recognition
import pyttsx3
import wave
import json
import os
import webbrowser
import requests
import wikipediaapi


class VoiceAssistant:
    name = ""
    sex = ""
    speech_language = ""
    recognition_language = ""


def setup_assistant_voice():
    voices = ttsEngine.getProperty("voices")

    if assistant.speech_language == "en":
        assistant.recognition_language = "en-US"
        if assistant.sex == "female":
            ttsEngine.setProperty("voice", voices[1].id)
        else:
            ttsEngine.setProperty("voice", voices[2].id)
    else:
        assistant.recognition_language = "ru-RU"
        ttsEngine.setProperty("voice", voices[0].id)


def play_voice_assistant_speech(text_to_speech):
    ttsEngine.say(str(text_to_speech))
    print(f"Assistant: {text_to_speech}")
    ttsEngine.runAndWait()


def record_and_recognize_audio(*args: tuple):
    with microphone:
        recognized_data = ""
        recognizer.adjust_for_ambient_noise(microphone, duration=2)

        try:
            print("Слушаю...")
            audio = recognizer.listen(microphone, 5, 5)

            with open("microphone-results.wav", "wb") as file:
                file.write(audio.get_wav_data())

        except speech_recognition.WaitTimeoutError:
            print("Проверьте работает ли микрафон? ?")
            return

        try:
            print("Анализирую")
            recognized_data = recognizer.recognize_google(audio, language="ru").lower()

        except speech_recognition.UnknownValueError:
            pass

        except speech_recognition.RequestError:
            print("Trying to use offline recognition...")
            recognized_data = use_offline_recognition()

        return recognized_data


def use_offline_recognition():
    recognized_data = ""
    try:
        if not os.path.exists("models/vosk-model-small-ru-0.4"):
            print("Please download the model from:\n"
                  "https://alphacephei.com/vosk/models and unpack as 'model' in the current folder.")
            exit(1)
        wave_audio_file = wave.open("microphone-results.wav", "rb")
        model = Model("models/vosk-model-small-ru-0.4")
        offline_recognizer = KaldiRecognizer(model, wave_audio_file.getframerate())

        data = wave_audio_file.readframes(wave_audio_file.getnframes())
        if len(data) > 0:
            if offline_recognizer.AcceptWaveform(data):
                recognized_data = offline_recognizer.Result()
                recognized_data = json.loads(recognized_data)
                recognized_data = recognized_data["text"]
    except:
        print("Sorry, speech service is unavailable. Try again later")

    return recognized_data


def search_youtube():
    search_query = " ".join(voice_input[1:])
    youtube_url = f"https://www.youtube.com/results?search_query={search_query}"
    webbrowser.open(youtube_url)
    play_voice_assistant_speech(f" Открываю YouTube с запросом {search_query}")


def search_weather(location):
    api_key = 'e5cf62e08e26429f84f194923241607'  # Replace with your WeatherAPI key
    weather_url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={location}&lang=ru"
    response = requests.get(weather_url)
    if response.status_code == 200:
        weather_data = response.json()
        temperature = weather_data['current']['temp_c']
        description = weather_data['current']['condition']['text']
        city_name = weather_data['location']['name']
        speech_text = f"Сейчас в городе {city_name} температура {temperature} градусов Цельсия, {description}"
        play_voice_assistant_speech(speech_text)
    else:
        play_voice_assistant_speech(f"Извините, не могу получить информацию о погоде в городе {location}")



def tell_me_about(query):
    user_agent = "pythonProject/1.0 (Contact: den.shubin22121@mail.ru)"
    wiki_wiki = wikipediaapi.Wikipedia(language='ru', user_agent=user_agent)
    page = wiki_wiki.page(query)
    if page.exists():
        summary = page.summary[:500]
        play_voice_assistant_speech(summary)
    else:
        play_voice_assistant_speech(f"Извините, я не нашел информации о {query} в Википедии.")



if __name__ == "__main__":
    recognizer = speech_recognition.Recognizer()
    microphone = speech_recognition.Microphone()
    ttsEngine = pyttsx3.init()
    assistant = VoiceAssistant()
    assistant.name = "Alice"
    assistant.sex = "female"
    assistant.speech_language = "ru"
    setup_assistant_voice()

    while True:
        voice_input = record_and_recognize_audio()
        os.remove("microphone-results.wav")
        print(voice_input)
        voice_input = voice_input.split(" ")
        command = voice_input[0]

        if command == "привет":
            play_voice_assistant_speech("Здравствуй")

        elif command == "найди" and len(voice_input) > 1:
            search_youtube()
        elif command == "какая" and voice_input[1] == "погода" and len(voice_input) > 2:
            location = " ".join(voice_input[2:])
            search_weather(location)
        elif command == "что" and voice_input[1] == "такое"  and len(voice_input) > 2:
            query = " ".join(voice_input[2:])
            tell_me_about(query)
