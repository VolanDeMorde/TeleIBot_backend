from flask import Flask, request, send_file
from flask_cors import CORS
from rembg import remove
from PIL import Image
import requests
import io
import os
import base64

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

@app.route('/generate', methods=['POST'])
def generate_image():
    data = request.json
    headers = {
        "Authorization": f"Bearer {os.getenv('STABILITY_KEY')}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "text_prompts": [{"text": data['prompt']}],
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
        return {"error": "Failed to generate image"}, 500
    
    image_data = base64.b64decode(response.json()['artifacts'][0]['base64'])
    return send_file(io.BytesIO(image_data), mimetype='image/png')

@app.route('/sticker', methods=['POST'])
def make_sticker():
    image = request.files['image'].read()
    cleaned = remove(image)  # Remove background
    
    img = Image.open(io.BytesIO(cleaned)).convert("RGBA")
    img.thumbnail((512, 512))
    
    output = io.BytesIO()
    img.save(output, format="WEBP")  # Convert to WEBP for Telegram
    output.seek(0)
    
    return send_file(output, mimetype='image/webp')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
