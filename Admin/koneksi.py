from flask import Flask, redirect, render_template, url_for, request, flash, jsonify
from pymongo import MongoClient

app = Flask(__name__)
app.secret_key = 'your_secret_key'

client = MongoClient('mongodb://localhost:27017/')
db = client['olshop']
product_collection = db['produk']

@app.route('/')
def index():
    produk = list(product_collection.find())
    return render_template('index.html', produk=produk)

@app.route('/pesanan')
def pesanan():
    return render_template('pesanan.html')

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

if __name__ == '__main__':
    app.run(debug=True)
