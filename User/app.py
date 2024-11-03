from flask import Flask, render_template, jsonify, request
from pymongo import MongoClient

app = Flask(__name__, static_folder='static')

   
client = MongoClient("mongodb://localhost:27017/")
db = client["olshop"]
pelanggan_collection = db.pelanggan  # Koleksi pelanggan

@app.route('/')
def index():
    return render_template('index.html')


# Endpoint untuk menambah pelanggan
@app.route('/pelanggan', methods=['POST'])
def tambah_pelanggan():
    data = request.json
    pelanggan_data = {
        "_id": data.get("id"),
        "nama": data.get("nama"),
        "email": data.get("email"),
        "no_hp": data.get("no_hp"),
        "alamat": data.get("alamat")
    }
    pelanggan_collection.insert_one(pelanggan_data)
    return jsonify({"msg": "Pelanggan berhasil ditambahkan!"})

@app.route('/shop')
def shop():
    return render_template('shop.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/blog')
def blog():
    return render_template('blog.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/cart')
def cart():
    return render_template('cart.html')


# # Endpoint untuk menghapus pelanggan
# @app.route('/pelanggan/<id>', methods=['DELETE'])
# def hapus_pelanggan(id):
#     result = pelanggan_collection.delete_one({"_id": id})
#     if result.deleted_count > 0:
#         return jsonify({"msg": "Pelanggan berhasil dihapus!"})
#     else:
#         return jsonify({"msg": "Pelanggan tidak ditemukan!"}), 404

# # Endpoint untuk memperbarui pelanggan
# @app.route('/pelanggan/<id>', methods=['PUT'])
# def update_pelanggan(id):
#     data = request.json
#     update_data = {}

#     if "nama" in data:
#         update_data["nama"] = data["nama"]
#     if "email" in data:
#         update_data["email"] = data["email"]
#     if "no_hp" in data:
#         update_data["no_hp"] = data["no_hp"]
#     if "alamat" in data:
#         update_data["alamat"] = data["alamat"]

#     result = pelanggan_collection.update_one({"_id": id}, {"$set": update_data})
#     if result.modified_count > 0:
#         return jsonify({"msg": "Data pelanggan berhasil diperbarui!"})
#     else:
#         return jsonify({"msg": "Pelanggan tidak ditemukan atau tidak ada perubahan!"}), 404

if __name__ == '__main__':
    app.run(debug=True)
