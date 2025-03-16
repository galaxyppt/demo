from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_cors import CORS
import pyttsx3
import os
import moviepy.editor as mp
import tempfile
import uuid
from pydub import AudioSegment
from question_generator import process_resume

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

CORS(app)

question_generator = None
first_question_asked = False

# Function to generate TTS audio
def generate_tts_audio(question_text):
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 150)
        engine.setProperty('volume', 1)

        temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        audio_path = temp_audio.name
        temp_audio.close()

        engine.save_to_file(question_text, audio_path)
        engine.runAndWait()

        audio = AudioSegment.from_file(audio_path, format="wav")

        return audio_path
    except Exception as e:
        print(f"Error generating TTS audio: {e}")
        raise

# Function to create a video with TTS audio
def create_video_with_audio(question_text):
    try:
        video_clip_path = r"C:/Users/ingle/Desktop/my-interview-project/my-interview-project/sample1.mp4"

        if not os.path.exists(video_clip_path):
            raise FileNotFoundError(f"Video file not found at {video_clip_path}")

        video_clip = mp.VideoFileClip(video_clip_path)
        audio_file = generate_tts_audio(question_text)
        audio_clip = mp.AudioFileClip(audio_file)
        trimmed_video = video_clip.subclip(0, min(video_clip.duration, audio_clip.duration))
        video_with_audio = trimmed_video.set_audio(audio_clip)

        static_dir = os.path.join(app.root_path, 'static')
        os.makedirs(static_dir, exist_ok=True)

        output_video_path = os.path.join(static_dir, f"{uuid.uuid4().hex}_output_video.mp4")
        video_with_audio.write_videofile(output_video_path, codec="libx264", audio_codec="aac")

        video_clip.close()
        trimmed_video.close()
        audio_clip.close()
        os.remove(audio_file)

        return output_video_path
    except Exception as e:
        print(f"Error during video creation: {e}")
        raise

@app.route('/', methods=['GET'])
def run():
    return render_template('index.html')

@app.route('/upload_resume', methods=['POST'])
def upload_resume():
    global resume_path, role
    role = request.form.get('role')
    resume = request.files.get('resume')

    if not role or not resume:
        return jsonify({"error": "Missing role or resume"}), 400

    resume_path = os.path.join(app.config['UPLOAD_FOLDER'], resume.filename)
    resume.save(resume_path)
    return jsonify({'message': 'File uploaded successfully', 'resume_path': resume_path, 'job_role': role})

@app.route('/process_response', methods=['POST'])
def process_response():
    global first_question_asked, question_generator

    resume_pdf_path = resume_path #r"C:/Users/shrut/OneDrive/Desktop/my-interview-project/uploads/resume.pdf"
    job_role = role  # You can modify this dynamically based on user input

    if not question_generator:
        resume_data = process_resume(resume_pdf_path, job_role)
        question_generator = resume_data["questions"]

    data = request.json
    response_text = data.get('response', '')

    if not first_question_asked:
        first_question_asked = True
        next_question = "Tell me about yourself."
    else:
        if question_generator:
            next_question = question_generator.pop(0)
        else:
            return jsonify({'error': "No more questions available."}), 400

    try:
        video_path = create_video_with_audio(next_question)
        video_filename = os.path.basename(video_path)
        response_data = {'next_question': next_question, 'video_src': f"/video/{video_filename}"}
        
        print("Response Data:", response_data)  # Debugging
        return jsonify(response_data)
    except Exception as e:
        print("Error:", str(e))  # Log errors
        return jsonify({'error': str(e)}), 500



@app.route('/video/<filename>')
def video(filename):
    video_folder = os.path.join(app.root_path, 'static')
    try:
        return send_from_directory(video_folder, filename)
    except FileNotFoundError:
        return "File not found", 404

if __name__ == '__main__':
    app.run(debug=False, port=5000)
