from flask import Flask, request, render_template, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import os
import hashlib
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Crea subcarpetas (actualizadas a plural)
for folder in ["videos", "images", "deviation_proofs"]:
    path = os.path.join(app.config['UPLOAD_FOLDER'], folder)
    os.makedirs(path, exist_ok=True)

def calculate_file_hash(file_path, hash_algorithm=Config.DEFAULT_HASH_ALGORITHM):
    hash_obj = {
        'sha256': hashlib.sha256(),
        'sha1': hashlib.sha1(),
        'md5': hashlib.md5()
    }.get(hash_algorithm.lower(), hashlib.sha256())
    
    with open(file_path, 'rb') as f:
        while chunk := f.read(8192):
            hash_obj.update(chunk)
    return hash_obj.hexdigest()

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

@app.route("/deviation_proofs")
def deviation_proofs():
    files = os.listdir(os.path.join(app.config['UPLOAD_FOLDER'], "deviation_proofs"))
    return render_template("deviation_proofs.html", files=files)

@app.route("/api/upload/check", methods=["GET"])
def check_server_duplicate():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if token != app.config['TOKEN']:
        return jsonify({"error": "Unauthorized"}), 401

    file_hash = request.args.get('hash')
    filename = request.args.get('filename')
    if not file_hash and not filename:
        return jsonify({"error": "Hash or filename parameter is required"}), 400

    folder = request.args.get('folder')
    if not folder:
        return jsonify({"error": "Folder parameter is required"}), 400

    folder_map = {
        'videos': 'videos',
        'images': 'images',
        'deviation_proofs': 'deviation_proofs'
    }

    if folder not in folder_map:
        return jsonify({"error": "Invalid folder"}), 400

    target_folder = os.path.join(app.config['UPLOAD_FOLDER'], folder_map[folder])
    hash_algorithm = request.args.get('hash_type', Config.DEFAULT_HASH_ALGORITHM).lower()
    
    if hash_algorithm not in Config.ALLOWED_HASH_ALGORITHMS:
        hash_algorithm = Config.DEFAULT_HASH_ALGORITHM

    if filename:
        safe_filename = secure_filename(filename)
        file_path = os.path.join(target_folder, safe_filename)
        if os.path.exists(file_path):
            return jsonify({
                "exists": True,
                "file": safe_filename,
                "path": f"/static/{folder_map[folder]}/{safe_filename}",
                "match_type": "filename"
            })

    if file_hash:
        for existing_file in os.listdir(target_folder):
            file_path = os.path.join(target_folder, existing_file)
            try:
                current_hash = calculate_file_hash(file_path, hash_algorithm)
                if current_hash == file_hash:
                    return jsonify({
                        "exists": True,
                        "file": existing_file,
                        "path": f"/static/{folder_map[folder]}/{existing_file}",
                        "match_type": "hash"
                    })
            except Exception as e:
                app.logger.error(f"Error checking file {existing_file}: {str(e)}")
                continue

    return jsonify({
        "exists": False,
        "hash_algorithm": hash_algorithm if file_hash else None,
        "searched_by": "filename" if filename and not file_hash else ("hash" if file_hash and not filename else "both")
    })

@app.route("/api/upload", methods=["POST"])
def upload_file():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if token != app.config['TOKEN']:
        return jsonify({"error": "Unauthorized"}), 401

    file = request.files.get('file')
    folder = request.form.get('folder')
    hash_algorithm = request.form.get('hash_algorithm', Config.DEFAULT_HASH_ALGORITHM).lower()

    if hash_algorithm not in Config.ALLOWED_HASH_ALGORITHMS:
        hash_algorithm = Config.DEFAULT_HASH_ALGORITHM

    folder_map = {
        'videos': 'videos',
        'images': 'images',
        'deviation_proofs': 'deviation_proofs'
    }

    if folder not in folder_map:
        return jsonify({"error": "Invalid folder"}), 400

    if file:
        filename = secure_filename(file.filename)
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], folder_map[folder])
        os.makedirs(save_path, exist_ok=True)
        file_path = os.path.join(save_path, filename)
        
        if os.path.exists(file_path):
            return jsonify({
                "error": "File already exists",
                "file": filename,
                "path": f"/static/{folder_map[folder]}/{filename}",
                "exists": True
            }), 409
        
        file.save(file_path)
        file_hash = calculate_file_hash(file_path, hash_algorithm)
        
        return jsonify({
            "message": f"File saved to {folder}/{filename}",
            "hash": file_hash,
            "hash_algorithm": hash_algorithm,
            "path": f"/static/{folder_map[folder]}/{filename}"
        }), 201
    else:
        return jsonify({"error": "No file provided"}), 400

@app.route('/static/<folder>/<filename>')
def uploaded_file(folder, filename):
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], folder), filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)


# from flask import Flask, request, render_template, jsonify, send_from_directory
# from werkzeug.utils import secure_filename
# import os

# app = Flask(__name__)

# STATIC_BASE = os.path.join(os.getcwd(), 'static')
# os.makedirs(STATIC_BASE, exist_ok=True)

# # Crea subcarpetas
# for folder in ["videos", "images", "deviation_proof"]:
#     path = os.path.join(STATIC_BASE, folder)
#     os.makedirs(path, exist_ok=True)

# app.config['UPLOAD_FOLDER'] = STATIC_BASE
# app.config['TOKEN'] = "cm6f0vxyt004cpl0175mingss"

# @app.route("/")
# def index():
#     return render_template("index.html")

# @app.route("/videos")
# def videos():
#     files = os.listdir(os.path.join(app.config['UPLOAD_FOLDER'], "videos"))
#     return render_template("videos.html", files=files)

# @app.route("/images")
# def images():
#     files = os.listdir(os.path.join(app.config['UPLOAD_FOLDER'], "images"))
#     return render_template("images.html", files=files)

# @app.route("/deviation_proof")
# def deviation_proof():
#     files = os.listdir(os.path.join(app.config['UPLOAD_FOLDER'], "deviation_proof"))
#     return render_template("deviation_proof.html", files=files)

# @app.route("/api/upload", methods=["POST"])
# def upload_file():
#     token = request.headers.get('Authorization', '').replace('Bearer ', '')
#     if token != app.config['TOKEN']:
#         return jsonify({"error": "Unauthorized"}), 401

#     file = request.files.get('file')
#     folder = request.form.get('folder')

#     folder_map = {
#         'video': 'videos',
#         'image': 'images',
#         'deviation_proof': 'deviation_proof'
#     }

#     if folder not in folder_map:
#         return jsonify({"error": "Invalid folder"}), 400

#     if file:
#         filename = secure_filename(file.filename)
#         save_path = os.path.join(app.config['UPLOAD_FOLDER'], folder_map[folder])
#         os.makedirs(save_path, exist_ok=True)
#         file.save(os.path.join(save_path, filename))
#         return jsonify({"message": f"File saved to {folder}/{filename}"}), 201
#     else:
#         return jsonify({"error": "No file provided"}), 400

# @app.route('/static/<folder>/<filename>')
# def uploaded_file(folder, filename):
#     return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], folder), filename)

# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=5000)
