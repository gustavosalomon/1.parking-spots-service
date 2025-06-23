from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)
CORS(app)

client = MongoClient("mongodb+srv://admin:admin123@cluster0.2owahcw.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["smart_parking"]
spots = db["parking_spots"]

@app.route("/api/parking-spots", methods=["GET"])
def get_spots():
    return jsonify(list(spots.find({}, {"_id": 0})))

@app.route("/api/parking-spots/<int:spot_id>", methods=["PUT"])
def update_spot(spot_id):
    data = request.get_json()
    current = spots.find_one({"id": spot_id})
    if not current:
        return jsonify({"error": "No encontrado"}), 404

    current.update(data)
    spots.replace_one({"id": spot_id}, current)
    return jsonify(current)

if __name__ == "__main__":
    app.run()

