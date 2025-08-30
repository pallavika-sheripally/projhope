import os
import io
import base64
import requests
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from dotenv import load_dotenv
import tempfile
import gtts
from io import BytesIO
import PyPDF2
from werkzeug.utils import secure_filename

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Hugging Face API setup for IBM Granite model
HFAPIKEY = os.getenv('HFAPIKEY')
HF_API_URL = "https://api-inference.huggingface.co/models/ibm-granite/granite-3.0-8b-instruct"

headers = {
    "Authorization": f"Bearer {HFAPIKEY}",
    "Content-Type": "application/json"
}

def extract_text_from_pdf(pdf_file):
    """Extract text from uploaded PDF file"""
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return None

def rewrite_text_with_tone(original_text, tone):
    """Rewrite text with specified tone using IBM Granite model"""
    
    # Define prompts for different tones
    tone_prompts = {
        "neutral": "Rewrite the following text in a neutral, factual tone while preserving all information:",
        "suspenseful": "Rewrite the following text in a suspenseful, engaging tone that builds tension:",
        "inspiring": "Rewrite the following text in an inspiring, motivational tone that uplifts the reader:"
    }
    
    prompt = f"{tone_prompts[tone]}\n\n{original_text}"
    
    try:
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 1024,
                "temperature": 0.7,
                "do_sample": True
            }
        }
        
        response = requests.post(HF_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        
        result = response.json()
        if isinstance(result, list) and len(result) > 0:
            rewritten_text = result[0].get('generated_text', '').replace(prompt, '').strip()
            return rewritten_text
        else:
            return original_text
            
    except Exception as e:
        print(f"Error in text rewriting: {e}")
        return original_text

def text_to_speech_gtts(text, voice='en-US_AllisonV3Voice'):
    """Convert text to speech using Google TTS (FREE)"""
    try:
        # Map voice selection to language parameters
        voice_map = {
            'en-US_AllisonV3Voice': {'lang': 'en', 'tld': 'com', 'slow': False},
            'en-US_LisaV3Voice': {'lang': 'en', 'tld': 'com', 'slow': False},
            'en-US_MichaelV3Voice': {'lang': 'en', 'tld': 'com', 'slow': False}
        }
        
        voice_params = voice_map.get(voice, {'lang': 'en', 'tld': 'com', 'slow': False})
        
        tts = gtts.gTTS(
            text=text, 
            lang=voice_params['lang'], 
            tld=voice_params['tld'], 
            slow=voice_params['slow']
        )
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
            tts.save(tmp_file.name)
            return tmp_file.name
            
    except Exception as e:
        print(f"Error in text-to-speech conversion: {e}")
        return None

@app.route('/api/upload-pdf', methods=['POST'])
def upload_pdf():
    """Handle PDF file upload and extract text"""
    try:
        if 'pdf' not in request.files:
            return jsonify({'error': 'No PDF file provided'}), 400
        
        pdf_file = request.files['pdf']
        
        if pdf_file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if pdf_file and pdf_file.filename.endswith('.pdf'):
            extracted_text = extract_text_from_pdf(pdf_file)
            
            if extracted_text:
                return jsonify({
                    'success': True,
                    'extracted_text': extracted_text,
                    'message': 'PDF text extracted successfully'
                })
            else:
                return jsonify({'error': 'Failed to extract text from PDF'}), 500
        else:
            return jsonify({'error': 'Invalid file format. Please upload a PDF file'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-audiobook', methods=['POST'])
def generate_audiobook():
    """Generate audiobook from text with selected tone and voice"""
    try:
        data = request.json
        text = data.get('text', '')
        tone = data.get('tone', 'neutral')
        voice = data.get('voice', 'en-US_AllisonV3Voice')
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        # Step 1: Rewrite text with selected tone
        rewritten_text = rewrite_text_with_tone(text, tone)
        
        # Step 2: Convert to speech using Google TTS
        audio_file_path = text_to_speech_gtts(rewritten_text, voice)
        
        if not audio_file_path:
            return jsonify({'error': 'Failed to generate audio'}), 500
        
        # Return both the rewritten text and audio
        return jsonify({
            'rewritten_text': rewritten_text,
            'audio_url': f'/api/audio/{os.path.basename(audio_file_path)}'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/audio/<filename>')
def get_audio(filename):
    """Serve generated audio files"""
    try:
        file_path = os.path.join(tempfile.gettempdir(), filename)
        return send_file(file_path, as_attachment=True, download_name='echoverse-audiobook.mp3')
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@app.route('/api/voices')
def get_voices():
    """Get available voices"""
    try:
        voices = [
            {'name': 'Allison (US English)', 'value': 'en-US_AllisonV3Voice'},
            {'name': 'Lisa (US English)', 'value': 'en-US_LisaV3Voice'},
            {'name': 'Michael (US English)', 'value': 'en-US_MichaelV3Voice'}
        ]
        return jsonify(voices)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)