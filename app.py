from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from telegram import Bot
import os
import io
import requests
from PIL import Image
from rembg import remove

# Initialize Flask and Telegram Bot
app = Flask(__name__)
CORS(app)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
STABILITY_API_KEY = os.getenv("STABILITY_API_KEY")
bot = Bot(token=TELEGRAM_BOT_TOKEN)  # Initialize Telegram Bot

# Generate Image with Stability AI
def generate_image_with_ai(prompt):
    headers = {"Authorization": f"Bearer {STABILITY_API_KEY}"}
    data = {"prompt": prompt, "output_format": "webp"}
    
    response = requests.post(
        "https://api.stability.ai/v2beta/stable-image/generate/core",
        headers=headers,
        files={"none": ''},
        data=data
    )
    
    if response.status_code == 200:
        return response.content
    else:
        raise Exception(f"AI Error: {response.text}")

# Remove Background with rembg
def create_sticker(image_bytes):
    input_image = Image.open(io.BytesIO(image_bytes))
    output_image = remove(input_image)
    
    # Resize to 512x512 (Telegram sticker requirement)
    output_image = output_image.resize((512, 512))
    
    output_bytes = io.BytesIO()
    output_image.save(output_bytes, format="PNG")
    return output_bytes.getvalue()

# Endpoint: Generate Image
@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()
    prompt = data.get('prompt')
    chat_id = data.get('chat_id')  # From frontend
    
    if not prompt or not chat_id:
        return jsonify({"error": "Prompt and chat_id are required"}), 400
    
    try:
        image_bytes = generate_image_with_ai(prompt)
        
        # Send image to user via Telegram Bot
        bot.send_photo(
            chat_id=chat_id,
            photo=io.BytesIO(image_bytes),
            caption="Your generated image 🎨"
        )
        
        return jsonify({"status": "Image sent to Telegram!"})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint: Create Sticker
@app.route('/sticker', methods=['POST'])
def sticker():
    if 'image' not in request.files:
        return jsonify({"error": "Image is required"}), 400
    
    image = request.files['image']
    chat_id = request.form.get('chat_id')  # From frontend
    
    try:
        image_bytes = image.read()
        sticker_bytes = create_sticker(image_bytes)
        
        # Send sticker to user via Telegram Bot
        bot.send_photo(
            chat_id=chat_id,
            photo=io.BytesIO(sticker_bytes),
            caption="Your new sticker ✨"
        )
        
        return jsonify({"status": "Sticker sent to Telegram!"})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
