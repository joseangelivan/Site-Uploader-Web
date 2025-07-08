from flask import Flask, request, render_template, redirect, url_for, jsonify, send_from_directory, abort
from werkzeug.utils import secure_filename
import os
import json

app = Flask(__name__)
app.config.from_object('config.Config')

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/videos")
def videos():
    files = os.listdir(os.path.join(app.config['UPLOAD_FOLDER'], "videos"))
    return render_template("videos.html", files=files)

@app.route("/images")
def images():
    files = os.listdir(os.path.join(app.config['UPLOAD_FOLDER'], "images"))
    return render_template("images.html", files=files)

@app.route("/deviation_proof")
def deviation_proof():
    files = os.listdir(os.path.join(app.config['UPLOAD_FOLDER'], "deviation_proof"))
    return render_template("deviation_proof.html", files=files)

@app.route("/api/upload", methods=["POST"])
def upload_file():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if token != app.config['TOKEN']:
        return jsonify({"error": "Unauthorized"}), 401

    file = request.files.get('file')
    folder = request.form.get('folder')

    folder_map = {
        'video': 'videos',
        'image': 'images',
        'deviation_proof': 'deviation_proof'
    }

    if folder not in folder_map:
        return jsonify({"error": "Invalid folder"}), 400

    if file:
        filename = secure_filename(file.filename)
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], folder_map[folder])
        os.makedirs(save_path, exist_ok=True)
        file.save(os.path.join(save_path, filename))
        return jsonify({"message": f"File saved to {folder}/{filename}"}), 201
    else:
        return jsonify({"error": "No file provided"}), 400

@app.route('/static/<folder>/<filename>')
def uploaded_file(folder, filename):
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], folder), filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

