from flask import Flask, render_template, jsonify, request, redirect, url_for, session, flash
import datetime
from pymongo import MongoClient
import os

app = Flask(__name__, static_folder='static')

   
client = MongoClient("mongodb://localhost:27017/")
db = client["olshop"]

#-------------------------------------------------------------------------------
pelanggan_collection = db.pelanggan  # Koleksi pelanggan
product_collection = db['produk'] # koleksi produk
pesanan_collection = db.pesanan  # Koleksi pesanan
app.secret_key = os.environ.get('SECRET_KEY') or os.urandom(24)

#-------------------------------------------------------------------------------
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/shop')
def shop():
    produk = list(product_collection.find())
    return render_template('shop.html', produk=produk)

@app.route('/home')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/thankyou')
def thankyou():
    return render_template('thankyou.html')

@app.route('/cart')
def cart():
    if 'username' not in session:
        flash("Silakan login terlebih dahulu untuk melihat chart Anda.", "warning")
        return redirect(url_for('login'))
    return render_template('cart.html') 


@app.route('/checkout')
def checkout():
    customer_id = session.get('customer_id')
    cart = session.get('cart', [])  

    pelanggan = pelanggan_collection.find_one({"_id": customer_id}) 
    if pelanggan is None:
        flash("Data pelanggan tidak ditemukan!", "danger")
        return redirect(url_for('home'))  

    order_details = []  
    subtotal = 0  

    for item in cart:
        product = product_collection.find_one({"_id": item['id_produk']})  
        if product: 
            product_name = product['nama']  
            quantity = item['jumlah']  
            total_price = product['harga'] * quantity  
            
            order_details.append({
                'product_id': product['_id'],    # ID produk
                'product_name': product_name,    # Nama produk
                'quantity': quantity,             # Kuantitas
                'total_price': total_price        # Total harga
            })

            subtotal += total_price  

    return render_template('checkout.html', customer=pelanggan, order_details=order_details, subtotal=subtotal)


#---------------------   LOGIN REGISTER  ---------------------------------------
@app.route('/login', methods=['GET', 'POST'])
def loginPW():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        pelanggan = pelanggan_collection.find_one({"username": username})
        
        if pelanggan and pelanggan['password'] == password: 
            session['username'] = username  
            session['customer_id'] = pelanggan['_id']  
           
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

#------------ PELANGGAN --------------------------------------------
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


# Endpoint untuk menghapus pelanggan
@app.route('/pelanggan/<id>', methods=['DELETE'])
def hapus_pelanggan(id):
    result = pelanggan_collection.delete_one({"_id": id})
    if result.deleted_count > 0:
        return jsonify({"msg": "Pelanggan berhasil dihapus!"})
    else:
        return jsonify({"msg": "Pelanggan tidak ditemukan!"}), 404

# Endpoint untuk memperbarui pelanggan
@app.route('/pelanggan/<id>', methods=['PUT'])
def update_pelanggan(id):
    data = request.json
    update_data = {}

    if "nama" in data:
        update_data["nama"] = data["nama"]
    if "email" in data:
        update_data["email"] = data["email"]
    if "no_hp" in data:
        update_data["no_hp"] = data["no_hp"]
    if "alamat" in data:
        update_data["alamat"] = data["alamat"]

    result = pelanggan_collection.update_one({"_id": id}, {"$set": update_data})
    if result.modified_count > 0:
        return jsonify({"msg": "Data pelanggan berhasil diperbarui!"})
    else:
        return jsonify({"msg": "Pelanggan tidak ditemukan atau tidak ada perubahan!"}), 404

#-------------------------------------- PESANAN --------------------------
@app.route('/pesanan')
def pesanan():
    customer_id = session.get('customer_id') 

    if not customer_id:
        flash("Please log in to view your order history.", "warning")
        return redirect(url_for('login'))

    pipeline = [
        {
            '$match': {'id_pelanggan': customer_id}  
        },
        {
            '$lookup': {
                'from': 'produk',  
                'localField': 'id_produk', 
                'foreignField': '_id', 
                'as': 'product_info' 
            }
        },
        {
            '$unwind': {
                'path': '$product_info',  
                'preserveNullAndEmptyArrays': True  
            }
        }
    ]

    orders = list(pesanan_collection.aggregate(pipeline))  
    
    for order in orders:
        if 'product_info' in order and order['product_info']:
            order['product_name'] = order['product_info'].get('nama')  
            order['product_price'] = order['product_info'].get('harga')  
        else:
            order['product_name'] = 'Produk tidak ditemukan' 
            order['product_price'] = 0 

    return render_template('order_history.html', orders=orders)

#---------- TAMBAHKAN KE KERANNJANG -------------
@app.route('/add_to_cart/<id_produk>', methods=['POST'])
def add_to_cart(id_produk):
    id_produk = str(id_produk)
    produk = product_collection.find_one({'_id': id_produk})  

    if produk:
        if 'cart' not in session:
            session['cart'] = []
        
        item_in_cart = next((item for item in session['cart'] if item['id_produk'] == id_produk), None)
        
        if item_in_cart:
            item_in_cart['jumlah'] += 1
        else:
            session['cart'].append({
                'id_produk': id_produk,
                'nama_produk': produk['nama'],  
                'harga': produk['harga'],
                'jumlah': 1,
                'gambar': produk['gambar']  
            })
    else:
        print("Produk tidak ditemukan")

    return redirect(url_for('cart'))


@app.route('/remove_from_cart/<id_produk>', methods=['POST'])
def remove_from_cart(id_produk):
    if 'cart' in session:
        session['cart'] = [item for item in session['cart'] if item['id_produk'] != id_produk]
    
    return redirect(url_for('cart'))


# ------------------- MEMASUKKAN DATA KE PESANAN ---------------
@app.route('/place_order', methods=['POST'])
def place_order():
    customer_id = session.get('customer_id')  
    if not customer_id:
        flash("Please log in to place an order.", "warning")
        return redirect(url_for('login'))

    # Ambil data dari formulir
    product_id = request.form['product_id']
    quantity = int(request.form['quantity'])
    delivery_address = request.form['delivery_address']
    payment_method = request.form['payment_method']

    # Buat data pesanan
    order_data = {
        'id_pelanggan': customer_id,
        'id_produk': product_id,
        'order_date': datetime.datetime.now().strftime('%Y-%m-%d'),  
        'status': 'Pending', 
        'jumlah_harga_pesanan': quantity * get_product_price(product_id),  
        'alamat_pengiriman': delivery_address,
        'metode_pembayaran': payment_method
    }

    pesanan_collection.insert_one(order_data)

    return redirect(url_for('thankyou'))

def get_product_price(product_id):
    product = product_collection.find_one({'_id':(product_id)})
    return product['harga'] if product else 0

if __name__ == '__main__':
    app.run(debug=True)
