from flask import Flask, request, send_file, jsonify
from pydub import AudioSegment
import os
import zipfile
import io

app = Flask(__name__)

# Directory to store temporary audio chunks
TEMP_DIR = 'temp_chunks'

# Ensure the temp_chunks directory exists
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

@app.route('/upload', methods=['POST'])
def upload_audio():
    if 'audioFile' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400

    audio_file = request.files['audioFile']
    audio = AudioSegment.from_file(audio_file)

    # Split the audio into 30-second chunks
    chunk_length_ms = 30 * 1000  # 30 seconds in milliseconds
    chunks = [audio[i:i + chunk_length_ms] for i in range(0, len(audio), chunk_length_ms)]

    # Prepare in-memory ZIP file
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for i, chunk in enumerate(chunks):
            chunk_filename = f'chunk_{i+1}.mp3'
            chunk_path = os.path.join(TEMP_DIR, chunk_filename)
            chunk.export(chunk_path, format='mp3')
            zip_file.write(chunk_path, chunk_filename)
            os.remove(chunk_path)  # Remove chunk file after adding to zip

    zip_buffer.seek(0)  # Rewind buffer

    # Send ZIP file back to client
    return send_file(zip_buffer, mimetype='application/zip', as_attachment=True, download_name='audio_chunks.zip')

if __name__ == '__main__':
    app.run(debug=True)
