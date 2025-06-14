# app.py
from flask import Flask, jsonify
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Test route to make sure the server is running
@app.route('/api/status', methods=['GET'])
def status():
    return jsonify({"status": "OK", "message": "MaPoGo Tutor backend is running!"})

if __name__ == '__main__':
    app.run(debug=True)