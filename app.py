# backend/app.py
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from rembg import remove
from PIL import Image
import os
import requests
import io
import logging

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/generate', methods=['POST'])
def generate_image():
    """Generate image using Stability AI API."""
    try:
        # Get prompt from request
        data = request.json
        prompt = data.get('prompt')
        if not prompt:
            return jsonify({"error": "No prompt provided"}), 400

        logger.info(f"Generating image for prompt: {prompt}")

        # Call Stability AI API
        headers = {
            "Authorization": f"Bearer {os.getenv('STABILITY_KEY')}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "text_prompts": [{"text": prompt}],
            "cfg_scale": 7,
            "height": 512,
            "width": 512,
            "samples": 1,
            "steps": 30
        }

        response = requests.post(
            "https://api.stability.ai/v1/generation/stable-diffusion-v1-6/text-to-image",
            headers=headers,
            json=payload
        )

        if response.status_code != 200:
            logger.error(f"Stability API error: {response.text}")
            return jsonify({"error": "Image generation failed"}), 500

        # Return generated image
        image_data = response.json()['artifacts'][0]['base64']
        return send_file(
            io.BytesIO(image_data),
            mimetype='image/png',
            download_name='generated_image.png'
        )

    except Exception as e:
        logger.error(f"Generation error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/sticker', methods=['POST'])
def create_sticker():
    """Convert image to sticker by removing background."""
    try:
        # Get uploaded image
        if 'image' not in request.files:
            return jsonify({"error": "No image uploaded"}), 400
            
        image_file = request.files['image'].read()
        
        logger.info("Processing sticker conversion")

        # Remove background
        cleaned_image = remove(image_file)
        
        # Process image
        img = Image.open(io.BytesIO(cleaned_image))
        img.thumbnail((512, 512))  # Resize for Telegram sticker requirements
        
        # Save to bytes
        output = io.BytesIO()
        img.save(output, format="PNG")
        output.seek(0)
        
        return send_file(
            output,
            mimetype='image/png',
            download_name='sticker.png'
        )

    except Exception as e:
        logger.error(f"Sticker conversion error: {str(e)}")
        return jsonify({"error": "Image processing failed"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Render's PORT takes priority
    #app.run(host='0.0.0.0', port=port)  # Bind to all interfaces
