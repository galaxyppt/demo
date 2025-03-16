# from pydub import AudioSegment
# import pyttsx3
# import tempfile
# import os

# def generate_tts_audio_with_pyttsx3(text):
#     try:
#         engine = pyttsx3.init()
#         engine.setProperty('rate', 150)  
#         engine.setProperty('volume', 1)  

#         # Select a female voice
#         voices = engine.getProperty('voices')
#         for voice in voices:
#             if "female" in voice.name.lower() or "zira" in voice.name.lower():  
#                 engine.setProperty('voice', voice.id)
#                 break

#         temp_audio_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
#         audio_path = temp_audio_file.name
#         temp_audio_file.close()

#         engine.save_to_file(text, audio_path)
#         engine.runAndWait()

#         return audio_path
#     except Exception as e:
#         print(f"Error generating TTS audio: {e}")
#         raise


# # Create 28 seconds of silence
# silence = AudioSegment.silent(duration=28000)  # 28 seconds of silence

# # Generate "Let's move to the next question" audio using pyttsx3
# message_audio_path = generate_tts_audio_with_pyttsx3("Let's move to the next question")

# # Load the generated message audio with pydub
# message = AudioSegment.from_file(message_audio_path, format="wav")

# # Combine silence and the message
# final_audio = silence + message

# # Output audio path
# output_audio_path = "output_audio.mp3"

# # Export the final audio file
# final_audio.export(output_audio_path, format="mp3")
# print(f"Audio file generated as '{output_audio_path}'")

# # Clean up the temporary TTS file
# os.remove(message_audio_path)


import speech_recognition as sr

def test_microphone(mic_index):
    recognizer = sr.Recognizer()
    
    try:
        with sr.Microphone(device_index=mic_index) as source:
            print(f"Testing microphone {mic_index}: {sr.Microphone.list_microphone_names()[mic_index]}")
            recognizer.adjust_for_ambient_noise(source, duration=2)
            print("Say something...")
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=5)
            print("Processing...")
            text = recognizer.recognize_google(audio)
            print("You said:", text)
    except sr.WaitTimeoutError:
        print("No speech detected. Try again.")
    except sr.UnknownValueError:
        print("Speech was unclear. Try again.")
    except sr.RequestError:
        print("Could not request results from Google Speech Recognition.")

# Change mic_index to 1, 5, 9, 13, or 15 and test
mic_index = 1  # Try different values from your list if this one fails
test_microphone(mic_index)



