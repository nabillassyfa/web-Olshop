from flask import Flask, render_template, jsonify, request, redirect, url_for, session, flash
from pymongo import MongoClient
import os

app = Flask(__name__, static_folder='static')

   
client = MongoClient("mongodb://localhost:27017/")
db = client["olshop"]
pelanggan_collection = db.pelanggan  # Koleksi pelanggan

app.secret_key = os.environ.get('SECRET_KEY') or os.urandom(24)

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

@app.route('/home')
def home():
    return render_template('index.html')

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

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def loginPW():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        pelanggan = pelanggan_collection.find_one({"username": username})
        
        if pelanggan and pelanggan['password'] == password:  
            session['username'] = username  
            flash("Login berhasil!", "success")
            return redirect(url_for('home'))
        else:
            flash("Username atau password salah!", "danger")
            return redirect(url_for('login'))
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def daftar():
    if request.method == 'POST':
        nama = request.form['nama']
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        no_hp = request.form['no_hp']

        # Simpan user di database
        pelanggan_data = {
            "nama": nama,
            "username": username,
            "password": password,
            "email": email,
            "no_hp": no_hp
        }
        pelanggan_collection.insert_one(pelanggan_data)
        flash("Registrasi berhasil! Silakan login.", "success")
        return redirect(url_for('login'))
    
    return render_template('register.html')

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
