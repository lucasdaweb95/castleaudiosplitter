import os
import logging
from flask import Flask, request, send_file
from pydub import AudioSegment
import zipfile
import io

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.DEBUG)

@app.route('/upload', methods=['POST'])
def upload_audio():
    if 'audioFile' not in request.files:
        logging.error("No audio file provided")
        return 'No audio file provided', 400

    audio_file = request.files['audioFile']

    try:
        # Check if the uploaded file is an MP4 file
        if audio_file.filename.endswith('.mp4'):
            # Save the uploaded MP4 temporarily
            audio_file.save('temp_video.mp4')
            # Use pydub with FFmpeg to extract audio
            audio = AudioSegment.from_file('temp_video.mp4', format='mp4')
        else:
            # Process other audio file types
            audio = AudioSegment.from_file(audio_file)

        # Split the audio into 30-second chunks
        chunk_length_ms = 30 * 1000  # 30 seconds in milliseconds
        chunks = [audio[i:i + chunk_length_ms] for i in range(0, len(audio), chunk_length_ms)]

        # Create a ZIP file to return the chunks
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for i, chunk in enumerate(chunks):
                chunk_filename = f'chunk_{i + 1}.mp3'  # Export as MP3
                chunk.export(chunk_filename, format='mp3')
                zip_file.write(chunk_filename)
                os.remove(chunk_filename)  # Clean up

        zip_buffer.seek(0)  # Rewind buffer
        return send_file(zip_buffer, mimetype='application/zip', as_attachment=True, download_name='audio_chunks.zip')
    
    except Exception as e:
        logging.error(f"Error processing audio: {e}")
        return 'Error processing audio', 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Default to 5000 if not set
    app.run(host='0.0.0.0', port=port)  # Bind to all available interfaces
