from flask import Flask, render_template, jsonify, request, redirect, url_for, session, flash
import datetime
from pymongo import MongoClient, ReturnDocument
from pymongo.errors import DuplicateKeyError
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
    # Ambil query parameter dari URL
    sort_by = request.args.get('sort_by', 'price_asc')
    selected_category = request.args.get('category')
    page = int(request.args.get('page', 1))  # Default page adalah 1
    limit = 4  # Batas produk per halaman
    
    # Tentukan sorting
    if sort_by == 'price_asc':
        sort_order = [("harga", 1)]
    elif sort_by == 'price_desc':
        sort_order = [("harga", -1)]
    elif sort_by == 'rating_desc':
        sort_order = [("rating", -1)]
    elif sort_by == 'rating_asc':
        sort_order = [("rating", 1)]
    else:
        sort_order = [("harga", 1)]
    
    # Bangun query filter
    query_filter = {}
    if selected_category:
        query_filter['kategori'] = selected_category
    
    # Hitung produk yang dilewati
    skip = (page - 1) * limit

    # Ambil produk dari database dengan filter, sorting, limit, dan pagination
    produk = list(product_collection.find(query_filter).sort(sort_order).skip(skip).limit(limit))
    kategori = product_collection.distinct("kategori")

    # Hitung total produk untuk menentukan jumlah halaman
    total_produk = product_collection.count_documents(query_filter)
    total_pages = (total_produk + limit - 1) // limit  # Total halaman

    return render_template('shop.html', produk=produk, sort_by=sort_by, kategori=kategori, selected_category=selected_category, page=page, total_pages=total_pages)


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

@app.route('/profile')
def profile():
    if 'username' in session:
        customer_id = session['customer_id']  # customer_id sudah berupa string
        pelanggan = pelanggan_collection.find_one({"_id": customer_id})  # Tidak perlu ObjectId
        if pelanggan:
            return render_template('profile.html', user=pelanggan)
        else:
            flash("User not found", "danger")
            return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/edit_profile', methods=['GET', 'POST'])
def update_profile():
    if 'username' in session:
        customer_id = session['customer_id']  # ID adalah string

        if request.method == 'POST':  # Jika form dikirimkan
            updated_data = {
                "nama": request.form.get("nama"),
                "username": request.form.get("username"),
                "email": request.form.get("email"),
                "no_hp": request.form.get("no_hp"),
                "alamat": request.form.get("alamat"),
            }
            # Update data user dengan menggunakan string customer_id
            pelanggan_collection.update_one({"_id": customer_id}, {"$set": updated_data})  
            flash("Profile updated successfully!", "success")
            return redirect(url_for('profile'))  # Redirect ke halaman profil setelah update
        else:  # Jika GET, tampilkan form edit
            user = pelanggan_collection.find_one({"_id": customer_id})  # Gunakan string customer_id
            return render_template('update_profile.html', user=user)
    else:
        return redirect(url_for('login'))  # Redirect ke login jika user belum login


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
            session['customer_id'] = str(pelanggan['_id'])  
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
        alamat = request.form['alamat']

        last_pelanggan = pelanggan_collection.find_one(sort=[("_id", -1)])
        if last_pelanggan and '_id' in last_pelanggan:
            new_id = str(int(last_pelanggan['_id']) + 1)
        else:
            new_id = "1" 
            
        pelanggan_data = {
            "_id": new_id,  
            "nama": nama,
            "username": username,
            "password": password,
            "email": email,
            "no_hp": no_hp,
            "alamat": alamat,
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

       
        cart = session['cart']
        
        item_in_cart = next((item for item in cart if item['id_produk'] == id_produk), None)

        if item_in_cart:
            item_in_cart['jumlah'] += 1
        else:
            cart.append({
                'id_produk': id_produk,
                'nama_produk': produk['nama'],
                'harga': produk['harga'],
                'jumlah': 1,
                'gambar': produk['gambar']
            })
        session['cart'] = cart
        session.modified = True  
    else:
        print("Produk tidak ditemukan")

    return redirect(url_for('cart'))


@app.route('/remove_from_cart/<id_produk>', methods=['POST'])
def remove_from_cart(id_produk):
    if 'cart' in session:
        session['cart'] = [item for item in session['cart'] if item['id_produk'] != id_produk]
    
    return redirect(url_for('cart'))


# ------------------- MEMASUKKAN DATA KE PESANAN ---------------
# Mencari id untuk id pesanan baru
def get_next_order_id():
    result = pesanan_collection.aggregate([
        {
            "$addFields": { 
                "numeric_id": { "$toInt": "$_id" }
            }
        },
        { 
            "$sort": { "numeric_id": -1 }
        },
        { 
            "$limit": 1 
        }
    ])

    # Mengambil ID terbesar dan menambahkannya dengan 1
    last_order = list(result)
    if last_order:
        new_order_id = str(last_order[0]['numeric_id'] + 1)
    else:
        new_order_id = "1"  # Jika tidak ada dokumen sebelumnya, mulai dari "1"
    return new_order_id

# Memasukan pesanan ke dalam database
@app.route('/place_order', methods=['POST'])
def place_order():
    customer_id = session.get('customer_id')  
    if not customer_id:
        flash("Please log in to place an order.", "warning")
        return redirect(url_for('login'))

    delivery_address = request.form['delivery_address']
    payment_method = request.form['payment_method']

    cart_items = session.get('cart', [])
    
    if not cart_items:
        flash("Keranjang belanja kosong.", "warning")
        return redirect(url_for('cart'))

    for item in cart_items:
        product_id = item['id_produk']
        quantity = item['jumlah'] 
        
        # Mengambil ID pesanan berikutnya
        new_order_id = get_next_order_id()
        
        order_data = {
            '_id': new_order_id,
            'id_pelanggan': customer_id,
            'id_produk': product_id,
            'order_date': datetime.datetime.now().strftime('%Y-%m-%d'),
            'status': 'Pending',
            'jumlah_harga_pesanan': quantity * get_product_price(product_id),
            'alamat_pengiriman': delivery_address,
            'metode_pembayaran': payment_method
        }

        try:
            pesanan_collection.insert_one(order_data)
        except DuplicateKeyError:
            flash("Duplicate order key error", "error")
            return redirect(url_for('checkout'))

    session.pop('cart', None)  # Menghapus 'cart' dari sesi
    return redirect(url_for('thankyou'))


def get_product_price(product_id):
    product = product_collection.find_one({'_id':(product_id)})
    return product['harga'] if product else 0

if __name__ == '__main__':
    app.run(debug=True)
