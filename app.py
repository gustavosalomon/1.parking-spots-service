from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Conexión a MongoDB Atlas
client = MongoClient("mongodb+srv://admin:admin123@cluster0.2owahcw.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["smart_parking"]
spots = db["parking_spots"]

# Obtener todos los lugares de estacionamiento
@app.route("/api/parking-spots", methods=["GET"])
def get_spots():
    result = []
    for s in spots.find():
        s["_id"] = str(s["_id"])  # convertir ObjectId a str o eliminarlo si preferís
        result.append(s)
    return jsonify(result)

# Actualizar un lugar de estacionamiento por ID
@app.route("/api/parking-spots/<int:spot_id>", methods=["PUT"])
def update_spot(spot_id):
    data = request.get_json()

    # Validar si existe ese lugar
    spot = spots.find_one({"id": spot_id})
    if not spot:
        return jsonify({"success": False, "error": "Espacio no encontrado"}), 404

    # Si la petición es para ocupar el lugar
    if data.get("status") == "ocupado":
        user = data.get("user")
        if not user or not user.get("dni"):
            return jsonify({"success": False, "error": "Datos de usuario incompletos"}), 400

        # Verificar si el mismo usuario ya ocupa otro lugar
        ya_ocupa = spots.find_one({
            "status": "ocupado",
            "user.dni": user["dni"],
            "id": {"$ne": spot_id}
        })
        if ya_ocupa:
            return jsonify({"success": False, "error": "El usuario ya tiene un lugar ocupado"}), 400

        # Actualizar spot
        updated = {
            "status": "ocupado",
            "user": user,
            "start_time": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            "end_time": None
        }

    # Si la petición es para liberar el lugar
    elif data.get("status") == "libre":
        updated = {
            "status": "vacío",
            "user": None,
            "start_time": None,
            "end_time": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        }

    else:
        return jsonify({"success": False, "error": "Estado inválido"}), 400

    # Actualizar en la base de datos
    spots.update_one({"id": spot_id}, {"$set": updated})
    updated_spot = spots.find_one({"id": spot_id})
    updated_spot["_id"] = str(updated_spot["_id"])  # para evitar error de serialización
    return jsonify({"success": True, "spot": updated_spot})

# Prueba rápida de conexión a MongoDB
@app.route("/test", methods=["GET"])
def test_mongo():
    count = spots.count_documents({})
    return jsonify({"ok": True, "spots_count": count})

if __name__ == "__main__":
    app.run(debug=True)
