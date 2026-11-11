# Proyek Analisis Data: E-Commerce Public Dataset

Proyek ini merupakan tugas akhir kelas Belajar Analisis Data dengan Python. Analisis dilakukan menggunakan data transaksi dari **E-Commerce Public Dataset (Olist)** pada periode September 2016 sampai Agustus 2018, lalu hasilnya disajikan dalam bentuk dashboard interaktif menggunakan Streamlit.

## Struktur Direktori

```text
submission
├───dashboard
│   ├───main_data.csv
│   └───dashboard.py
├───data
│   ├───customers_dataset.csv
│   ├───order_items_dataset.csv
│   ├───order_payments_dataset.csv
│   ├───order_reviews_dataset.csv
│   ├───orders_dataset.csv
│   ├───product_category_name_translation.csv
│   ├───products_dataset.csv
│   └───sellers_dataset.csv
├───notebook.ipynb
├───README.md
├───requirements.txt
└───url.txt
```

## Setup Environment - Anaconda

```bash
conda create --name main-ds python=3.9
conda activate main-ds
pip install -r requirements.txt
```

## Setup Environment - Shell/Terminal

```bash
mkdir proyek_analisis_data
cd proyek_analisis_data
pipenv install
pipenv shell
pip install -r requirements.txt
```

## Run steamlit app

Jalankan perintah berikut dari direktori utama proyek (`submission`):

```bash
streamlit run dashboard/dashboard.py
```

Atau jika ingin menjalankan langsung dari dalam folder `dashboard`:

```bash
cd dashboard
streamlit run dashboard.py
```

## Pertanyaan Bisnis

1. Kategori produk apa saja yang masuk ke dalam 5 urutan tertinggi dan 5 urutan terendah berdasarkan total pendapatan pada pesanan yang berhasil dikirim, serta berapa persen sumbangan dari 5 kategori teratas tersebut terhadap total pendapatan produk selama September 2016 – Agustus 2018?
2. Seberapa besar penurunan rata-rata skor ulasan pelanggan (`review_score`) dalam satuan poin maupun persen ketika pesanan datang terlambat dibandingkan yang tepat waktu, dan negara bagian mana yang paling sering mengalami keterlambatan pengiriman selama September 2016 – Agustus 2018?

## Ringkasan Hasil Analisis

- **Pendapatan per Kategori Produk:** Sebanyak 5 kategori teratas (`health_beauty`, `watches_gifts`, `bed_bath_table`, `sports_leisure`, dan `computers_accessories`) menyumbang **40,35%** dari total pendapatan produk yang kategorinya diketahui (5,27 juta BRL dari 13,05 juta BRL). Kategori dengan pendapatan tertinggi adalah `health_beauty` sebesar **1.233.131,72 BRL** (9,45%), sedangkan yang paling rendah adalah `security_and_services` sebesar **283,29 BRL** (kurang dari 0,01%).
- **Pengaruh Keterlambatan Pengiriman terhadap Ulasan:** Pesanan yang sampai tepat waktu rata-rata mendapatkan skor ulasan **4,29 dari 5,00**. Sebaliknya, pesanan yang datang terlambat rata-rata skornya turun **2,02 poin (-47,1%)** menjadi **2,27 dari 5,00**, dan porsi ulasan buruk (skor 1–2) naik drastis dari **9,27%** menjadi **62,40%**. Untuk wilayah dengan jumlah pesanan minimal 500 transaksi, keterlambatan paling tinggi terjadi di negara bagian **MA (17,43%)**, **CE (13,76%)**, **BA (12,16%)**, dan **RJ (12,11%)**.
- **Segmentasi Pelanggan (RFM):** Dari **93.350 pelanggan unik**, sekitar **97,00%** baru pernah berbelanja satu kali. Selain itu, pelanggan di kelompok belanja *High* dan *VIP* (total belanja di atas 150 BRL) jumlahnya hanya **25,36%** dari total pelanggan, tetapi menyumbang **62,92%** dari keseluruhan pendapatan.
