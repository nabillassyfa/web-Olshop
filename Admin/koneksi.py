from flask import Flask, redirect, render_template, url_for, request, flash, jsonify
from pymongo import MongoClient
from bson.json_util import dumps

app = Flask(__name__)
app.secret_key = 'your_secret_key'

client = MongoClient('mongodb://localhost:27017/')
db = client['olshop']
product_collection = db['produk']
pesanan_collection = db['pesanan']
pelanggan_collection = db['pelanggan']

@app.route('/')
def index():
    sort_order = request.args.get('sort', 'asc')
    sort_direction = 1 if sort_order == 'asc' else -1
    produk = list(product_collection.find().sort("stok", sort_direction))
    
    return render_template('index.html', produk=produk, sort_order=sort_order)

@app.route('/pelanggan')
def pelanggan():
    pelanggan = list(pelanggan_collection.find())
    return render_template('pelanggan.html', pelanggan=pelanggan)


@app.route('/pesanan')
def pesanan():
    sort_order = request.args.get('sort', 'asc')
    sort_direction = 1 if sort_order == 'asc' else -1
    status_filter = request.args.get('status_filter')

    # filter tabel selesai dan proses
    filter_query = {}
    if status_filter == 'selesai':
        filter_query["status"] = "selesai"
    elif status_filter == 'non-selesai':
        filter_query["status"] = {"$ne": "selesai"}

    # beberapa agregasi
    total_orders = pesanan_collection.count_documents({})
    completed_orders = pesanan_collection.count_documents({"status": "selesai"})
    non_completed_orders = total_orders - completed_orders
    total_revenue = pesanan_collection.aggregate([
        {"$group": {"_id": None, "total_revenue": {"$sum": "$jumlah_harga_pesanan"}}}
    ])
    total_revenue = next(total_revenue, {}).get("total_revenue", 0)

    pesanan = pesanan_collection.find(filter_query).sort("jumlah_harga_pesanan", sort_direction)
    
    enriched_pesanan = []
    for order in pesanan:
        product = product_collection.find_one({"_id": order["id_produk"]})
        pelanggan = pelanggan_collection.find_one({"_id": order["id_pelanggan"]})
        
        enriched_pesanan.append({
            "_id": order["_id"],
            "status": order["status"],
            "alamat_pengiriman": order["alamat_pengiriman"],
            "metode_pembayaran": order["metode_pembayaran"],
            "jumlah_harga_pesanan": order["jumlah_harga_pesanan"],
            "product_name": product["nama"] if product else "Unknown",
            "pelanggan_name": pelanggan["nama"] if pelanggan else "Unknown",
            "order_date": order["order_date"]
        })

    return render_template('pesanan.html', pesanan=enriched_pesanan, sort_order=sort_order, status_filter=status_filter, total_orders=total_orders, completed_orders=completed_orders, non_completed_orders=non_completed_orders, total_revenue=total_revenue)



@app.route('/tambah_produk', methods=['POST'])
def tambah_produk():
    nama = request.form.get('nama')
    kategori = request.form.get('kategori')
    deskripsi = request.form.get('deskripsi')
    stok = request.form.get('stok', type=int)
    rating = request.form.get('rating', type=float)
    harga = request.form.get('harga', type=int)
    gambar = request.form.get('gambar')

    if not all([nama, kategori, stok, rating, harga]):
        flash('Semua field harus diisi!')
        return redirect(url_for('index'))

    # Cari produk dengan `_id` terbesar
    last_product = product_collection.find_one(sort=[("_id", -1)])
    if last_product and "_id" in last_product:
        # Ubah `_id` terbesar menjadi integer, tambahkan 1, dan konversi kembali ke string
        new__id = str(int(last_product["_id"]) + 1)
    else:
        new__id = "1"  # Mulai dari "1" jika belum ada produk

    # Data produk baru
    produk_baru = {
        '_id': new__id,
        'nama': nama,
        'kategori': kategori,
        'deskripsi': deskripsi,
        'stok': stok,
        'rating': rating,
        'harga': harga,
        'gambar': gambar
    }

    # Simpan produk ke database
    product_collection.insert_one(produk_baru)
    flash('Produk berhasil ditambahkan!')

    return redirect(url_for('index'))

@app.route('/tambah_pelanggan', methods=['POST'])
def tambah_pelanggan():
    username = request.form.get('username')
    password = request.form.get('password')
    nama = request.form.get('nama')
    email = request.form.get('email')
    no_hp = request.form.get('no_hp')
    alamat = request.form.get('alamat')

    if not all([username, password, nama, email, no_hp, alamat]):
        flash('Semua field harus diisi!')
        return redirect(url_for('index'))

    last_customer = pelanggan_collection.find_one(sort=[("_id", -1)])
    if last_customer and "_id" in last_customer:
        # Increment the largest `_id`
        new__id = str(int(last_customer["_id"]) + 1)
    else:
        new__id = "1"  

    # New customer data
    pelanggan_baru = {
        '_id': new__id,
        'username': username,
        'password': password, 
        'nama': nama,
        'email': email,
        'no_hp': no_hp,
        'alamat': alamat
    }

    # Insert new customer into the database
    pelanggan_collection.insert_one(pelanggan_baru)
    flash('Pelanggan berhasil ditambahkan!')

    return redirect(url_for('pelanggan'))

@app.route('/hapus_produk/<produk_id>', methods=['POST'])
def hapus_produk(produk_id):
    product_collection.delete_one({'_id': produk_id})
    flash('Produk berhasil dihapus!')
    return redirect(url_for('index'))

@app.route('/hapus_pesanan/<pesanan_id>', methods=['POST'])
def hapus_pesanan(pesanan_id):
    pesanan_collection.delete_one({'_id': pesanan_id})
    flash('Pesanan berhasil dihapus!')
    return redirect(url_for('pesanan'))

@app.route('/hapus_pelanggan/<pelanggan_id>', methods=['POST'])
def hapus_pelanggan(pelanggan_id):
    pelanggan_collection.delete_one({'_id': pelanggan_id})
    flash('Pelanggan berhasil dihapus!')
    return redirect(url_for('pelanggan'))

@app.route('/update_pelanggan/<pelanggan_id>', methods=['POST'])
def update_pelanggan(pelanggan_id):
    username = request.form.get('username')
    password = request.form.get('password')
    nama = request.form.get('nama')
    email = request.form.get('email')
    no_hp = request.form.get('no_hp')
    alamat = request.form.get('alamat')

    if not all([username, password, nama, email, no_hp, alamat]):
        flash('Semua field harus diisi!')
        return redirect(url_for('pelanggan'))
    
    updated_pelanggan = {
        'username': username,
        'password': password, 
        'nama': nama,
        'email': email,
        'no_hp': no_hp,
        'alamat': alamat
    }

    pelanggan_collection.update_one({'_id': pelanggan_id}, {'$set': updated_pelanggan})
    flash('Pelanggan berhasil diperbarui!')

    return redirect(url_for('pelanggan'))

@app.route('/update_produk/<produk_id>', methods=['POST'])
def update_produk(produk_id):
    nama = request.form.get('nama')
    kategori = request.form.get('kategori')
    deskripsi = request.form.get('deskripsi')
    stok = request.form.get('stok', type=int)
    rating = request.form.get('rating', type=float)
    harga = request.form.get('harga', type=int)
    gambar = request.form.get('gambar')

    if not all([nama, kategori, stok, rating, harga]):
        flash('Semua field harus diisi!')
        return redirect(url_for('index'))

    # Data produk yang akan diperbarui
    updated_produk = {
        'nama': nama,
        'kategori': kategori,
        'deskripsi': deskripsi,
        'stok': stok,
        'rating': rating,
        'harga': harga,
        'gambar': gambar
    }

    # Update produk dalam database
    product_collection.update_one({'_id': produk_id}, {'$set': updated_produk})
    flash('Produk berhasil diperbarui!')

    return redirect(url_for('index'))

@app.route('/update_pesanan/<pesanan_id>', methods=['POST'])
def update_pesanan(pesanan_id):
    status = request.form.get('status')

    if not all([status]):
        flash('Semua field harus diisi!')
        return redirect(url_for('index'))

    # Data produk yang akan diperbarui
    updated_produk = {
        'status': status
    }

    # Update produk dalam database
    pesanan_collection.update_one({'_id': pesanan_id}, {'$set': updated_produk})
    flash('Produk selesai!')

    return redirect(url_for('pesanan'))


if __name__ == '__main__':
    app.run(debug=True)
