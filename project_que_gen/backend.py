from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_cors import CORS
import pyttsx3
import os
import moviepy.editor as mp
import speech_recognition as sr
import tempfile
import uuid
from pydub import AudioSegment
from question_generator import process_resume
import random
import matplotlib.pyplot as plt
import time

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

CORS(app)
#new comment

# Global variables
question_generator = None
first_question_asked = False
candidate_responses = []
resume_path = None
role = None
current_question_index = 0

# Function to generate appreciation messages
def generate_appreciation():
    appreciations = [
        "Great answer!", "Well done!", "That was insightful!", 
        "Excellent response!", "You're doing great!"
    ]
    return random.choice(appreciations)

# Function to generate transition messages
def generate_transition_message():
    return "Let's move to the next question."

# Function to generate follow-up questions
def generate_follow_up_question(response):
    if "project" in response.lower():
        return "Can you tell me more about that project?"
    elif "team" in response.lower():
        return "How did you handle conflicts within your team?"
    elif "problem" in response.lower():
        return "What steps did you take to solve that problem?"
    else:
        return None

# Function to evaluate candidate responses
def evaluate_response(response):
    keywords = ["experience", "skills", "project", "team", "problem"]
    score = sum(1 for keyword in keywords if keyword in response.lower())
    return score

# Function to visualize results
def visualize_results():
    questions = [resp['question'] for resp in candidate_responses]
    scores = [resp['score'] for resp in candidate_responses]

    plt.figure(figsize=(10, 6))
    plt.bar(questions, scores, color='skyblue')
    plt.xlabel('Questions')
    plt.ylabel('Score')
    plt.title('Candidate Performance')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig('static/performance.png')  # Save the visualization
    plt.close()

# Function to generate TTS audio
def generate_tts_audio(text):
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 150)
        engine.setProperty('volume', 1)

        # Select a female voice
        voices = engine.getProperty('voices')
        for voice in voices:
            if "female" in voice.name.lower() or "zira" in voice.name.lower():
                engine.setProperty('voice', voice.id)
                break

        temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        audio_path = temp_audio.name
        temp_audio.close()

        engine.save_to_file(text, audio_path)
        engine.runAndWait()

        return audio_path
    except Exception as e:
        print(f"Error generating TTS audio: {e}")
        raise

# Function to recognize speech from the candidate
def recognize_speech():
    recognizer = sr.Recognizer()
    
    # Print available microphone devices
    print("Available microphone devices:")
    for index, name in enumerate(sr.Microphone.list_microphone_names()):
        print(f"{index}: {name}")

    # Use the default microphone (or specify a device index)
    mic_index = 1  # Change this if the default microphone is not working
    with sr.Microphone(device_index=mic_index) as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        try:
            audio = recognizer.listen(source, timeout=10)  # Increased timeout
            text = recognizer.recognize_google(audio)
            print("Recognized Speech:", text)  # Debugging
            return text
        except sr.UnknownValueError:
            print("Speech not understood")
            return "Speech not understood. Please try again."
        except sr.RequestError as e:
            print(f"Speech recognition service error: {e}")
            return f"Error: Speech recognition service unavailable ({e})"
        except Exception as e:
            print(f"Speech recognition error: {e}")
            return f"Error: {str(e)}"

# Function to create a video with TTS audio
def create_video_with_audio(question_text):
    try:
        video_clip_path = r"C:\Users\ingle\Desktop\project_que_gen\project_que_gen\sample1.mp4"

        if not os.path.exists(video_clip_path):
            raise FileNotFoundError(f"Video file not found at {video_clip_path}")

        video_clip = mp.VideoFileClip(video_clip_path)

        # Generate TTS for the question
        question_audio_path = generate_tts_audio(question_text)
        question_audio = mp.AudioFileClip(question_audio_path)

        # Generate TTS for the transition message
        transition_message = generate_transition_message()
        transition_audio_path = generate_tts_audio(transition_message)
        transition_audio = mp.AudioFileClip(transition_audio_path)

        # Combine question and transition audio
        combined_audio = mp.concatenate_audioclips([question_audio, transition_audio])

        # Trim video to match audio duration
        trimmed_video = video_clip.subclip(0, min(video_clip.duration, combined_audio.duration))
        video_with_audio = trimmed_video.set_audio(combined_audio)

        # Save the final video
        static_dir = os.path.join(app.root_path, 'static')
        os.makedirs(static_dir, exist_ok=True)
        output_video_path = os.path.join(static_dir, f"{uuid.uuid4().hex}_output_video.mp4")
        video_with_audio.write_videofile(output_video_path, codec="libx264", audio_codec="aac")

        # Clean up
        video_clip.close()
        trimmed_video.close()
        question_audio.close()
        transition_audio.close()
        os.remove(question_audio_path)
        os.remove(transition_audio_path)

        return output_video_path
    except Exception as e:
        print(f"Error during video creation: {e}")
        raise

# Route to render the main page
@app.route('/', methods=['GET'])
def run():
    return render_template('index.html')

# Route to upload resume
@app.route('/upload_resume', methods=['POST'])
def upload_resume():
    global resume_path, role, question_generator, current_question_index

    role = request.form.get('role')
    resume = request.files.get('resume')

    if not role or not resume:
        return jsonify({"error": "Missing role or resume"}), 400

    # Ensure the uploads directory exists
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    resume_path = os.path.join(app.config['UPLOAD_FOLDER'], resume.filename)
    resume.save(resume_path)

    # Process the resume and generate questions
    resume_data = process_resume(resume_path, role)
    question_generator = resume_data["questions"]
    current_question_index = 0  # Reset question index

    return jsonify({'message': 'File uploaded successfully', 'resume_path': resume_path, 'job_role': role})

# Route to process candidate responses
@app.route('/process_response', methods=['POST'])
def process_response():
    global first_question_asked, question_generator, candidate_responses, current_question_index

    # Process the candidate's response
    response_data = recognize_speech()
    print("Response Data:", response_data)

    # Evaluate the response
    score = evaluate_response(response_data)
    candidate_responses.append({
        'question': question_generator[current_question_index] if question_generator else "No question",
        'response': response_data,
        'score': score
    })

    # Generate appreciation message
    appreciation_message = generate_appreciation()

    # Generate the next question
    if not first_question_asked:
        first_question_asked = True
        next_question = "Tell me about yourself."
    else:
        if question_generator and current_question_index < len(question_generator) - 1:
            current_question_index += 1
            next_question = question_generator[current_question_index]
        else:
            # Visualize results if no more questions are available
            visualize_results()
            return jsonify({'error': "No more questions available.", 'visualization': 'static/performance.png'}), 400

    # Create video with the next question
    video_path = create_video_with_audio(next_question)
    video_filename = os.path.basename(video_path)
    response_data = {
        'next_question': next_question,
        'video_src': f"/video/{video_filename}",
        'appreciation': appreciation_message
    }
    return jsonify(response_data)

# Route to serve video files
@app.route('/video/<filename>')
def video(filename):
    video_folder = os.path.join(app.root_path, 'static')
    try:
        return send_from_directory(video_folder, filename)
    except FileNotFoundError:
        return "File not found", 404

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=False, port=5000)