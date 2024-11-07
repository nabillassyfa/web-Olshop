## TUGAS UTS KELOMPOK 10
### Ilmu Komputer - Universitas Pendidikan Indonesia
#### Mata Kuliah : Basis Data Non-Rekasional
#### Anggota : 
##### - Legi Kuswandi
##### - Muhammad Rifky Afandi
##### - Nabilla Assyfa Ramadhani
##### - Revana Faliha Salma
<br>
<br>
Proyek ini terdiri dari dua situs web terpisah yang dirancang untuk pengguna dan admin. Situs web untuk pengguna memungkinkan pelanggan untuk berbelanja produk yang tersedia, sedangkan situs web admin digunakan oleh administrator untuk melakukan operasi CRUD (Create, Read, Update, Delete) pada data pelanggan, produk, dan pesanan.<br><br>
Sistem ini menggunakan MongoDB sebagai basis datanya dan telah mengimplementasikan berbagai fungsi database, seperti agregasi, pembatasan jumlah data (limit), pengurutan (sorting), dan penggabungan data (join). Struktur database yang digunakan adalah sebagai berikut:

#### pelanggan  
_id: "1",  
username:"rere", <br>
password:"reee",<br>
nama: "Revana Faliha Salma",  
email: "rerevana@gmail.com",  
no_hp: "081234567890",  
alamat: "Jl. Gegerkalong no 102"  
  
#### produk  
"_id": "1",  
"nama": "Kaos Polos",  
"harga": 75000,    
"kategori": "Pakaian",  
"stok": 100,  
"deskripsi": "Kaos polos nyaman dan berkualitas.",  
"rating": 4.5  
"gambar":  
  
#### pesanan  
_id: "1",  
id_pelanggan: "1",  
id_produk: "2",  
order_date: "2024-11-01",  
status: "dikirim",  
jumlah_harga_pesanan: 150000,  
alamat_pengiriman: "Jl. Raya No. 1, Bandung",  
metode_pembayaran: "Transfer Bank"  
