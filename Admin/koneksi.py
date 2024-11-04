from flask import Flask, redirect, render_template, url_for, request, flash, jsonify
from pymongo import MongoClient

app = Flask(__name__)
app.secret_key = 'your_secret_key'

client = MongoClient('mongodb://localhost:27017/')
db = client['olshop']
product_collection = db['produk']
pesanan_collection = db['pesanan']
pelanggan_collection = db['pelanggan']

@app.route('/')
def index():
    produk = list(product_collection.find())
    return render_template('index.html', produk=produk)

@app.route('/pesanan')
def pesanan():
    pesanan = pesanan_collection.find()
    enriched_pesanan = []

    for pesanan in pesanan:

        product = product_collection.find_one({"_id": pesanan["id_produk"]})
        product_name = product["nama"] if product else "Unknown"

        pelanggan = pelanggan_collection.find_one({"_id": pesanan['id_pelanggan']})
        pelanggan_name = pelanggan["nama"] if pelanggan else "Unknown"

        enriched_pesanan.append({
            "_id": pesanan["_id"],
            "status": pesanan["status"],
            "alamat_pengiriman": pesanan["alamat_pengiriman"],
            "metode_pembayaran": pesanan["metode_pembayaran"],
            "jumlah_harga_pesanan": pesanan["jumlah_harga_pesanan"],
            "product_name": product_name,
            "pelanggan_name": pelanggan_name,
            "order_date": pesanan["order_date"]
        })

    return render_template('pesanan.html', pesanan=enriched_pesanan)

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

@app.route('/hapus_produk/<produk_id>', methods=['POST'])
def hapus_produk(produk_id):
    product_collection.delete_one({'_id': produk_id})
    flash('Produk berhasil dihapus!')
    return redirect(url_for('index'))

@app.route('/hapus_pesanan/<pesanan_id>', methods=['POST'])
def hapus_pesanan(pesanan_id):
    pesanan_collection.delete_one({'_id': pesanan_id})
    flash('Pesanan berhasil dihapus!')
    return redirect(url_for('index'))

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
