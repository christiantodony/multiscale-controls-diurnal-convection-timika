# Panduan GitHub dan Zenodo untuk rilis pertama

Repository ini sudah disiapkan sebagai kandidat. Jangan unggah data AWS mentah,
credentials, atau NetCDF/GRIB besar.

## Cara yang dipilih: upload manual dari PC

Cara ini menjaga kepemilikan repository pada akun GitHub pribadi dan tidak
bergantung pada akun kampus atau masa aktif JASMIN.

1. Download paket ZIP terbaru dan ekstrak di PC.
2. Buka repository GitHub kosong.
3. Klik **uploading an existing file**.
4. Buka folder hasil ekstraksi
   `multiscale-controls-diurnal-convection-timika`.
5. Pilih **semua isi di dalam folder tersebut**, bukan folder luarnya. Pastikan
   yang dipilih mencakup `README.md`, `.gitignore`, `.github`, `src`, `scripts`,
   `data`, `docs`, `tests`, dan file konfigurasi lainnya.
6. Seret file dan folder terpilih ke kotak upload GitHub.
7. Tunggu sampai semua file selesai diproses.
8. Isi commit message: `Prepare reproducible Paper I analysis code`.
9. Klik **Commit changes**.

Jika folder luar yang diunggah, README tidak akan muncul pada halaman utama dan
seluruh isi akan berada satu tingkat terlalu dalam. Batalkan sebelum commit jika
hal itu terjadi.

## 1. Buat akun dan repository kosong

1. Masuk ke <https://github.com>.
2. Klik **New repository**.
3. Isi nama: `multiscale-controls-diurnal-convection-timika`.
4. Pilih **Public** setelah audit v1.0 selesai. Selama pemeriksaan awal, Anda
   boleh memilih **Private**.
5. Jangan tambahkan README, `.gitignore`, atau license dari halaman GitHub karena
   semuanya sudah ada di folder ini.

## 2. Pasang Git dan identitas penulis

Di terminal JASMIN:

```bash
git --version
git config --global user.name "Dony Christianto"
git config --global user.email "EMAIL-YANG-TERHUBUNG-DENGAN-GITHUB"
```

Anda dapat memakai email privat GitHub dari **Settings > Emails**.

## 3. Periksa isi sebelum commit

```bash
cd /path/to/multiscale-controls-diurnal-convection-timika
git init
git branch -M main
git status --short
```

Pemeriksaan keamanan:

```bash
find . -type f -size +20M -print
grep -RInE 'token|password|api[_-]?key|/home/users/|/gws/' \
  --exclude-dir=.git .
```

Hasil yang menyebut contoh kata `token` dalam dokumentasi perlu dibaca, tetapi
tidak otomatis berarti ada credential. Pastikan tidak ada AWS mentah, `.cdsapirc`,
SSH key, NetCDF, GRIB, atau path pribadi.

## 4. Uji lalu commit

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
pytest

git add .gitignore README.md LICENSE CITATION.cff pyproject.toml requirements.txt environment.yml
git add src scripts config data docs tests .github CONTRIBUTING.md CHANGELOG.md
git status
git diff --cached --stat
git commit -m "Prepare reproducible Paper I analysis code"
```

## 5. Hubungkan ke GitHub

Alamat repository Anda:

```bash
git remote add origin https://github.com/christiantodony/multiscale-controls-diurnal-convection-timika.git
git push -u origin main
```

GitHub tidak lagi menerima password akun untuk `git push`. Gunakan browser
sign-in, personal access token, atau SSH sesuai petunjuk GitHub/JASMIN. Jangan
simpan token di file repository.

## 6. Pemeriksaan sebelum public v1.0

Selesaikan semua kotak pada `docs/reproducibility_audit.md`. Kemudian buat tag:

```bash
git tag -a v1.0.0 -m "Code release associated with QJRMS article qj.70297"
git push origin v1.0.0
```

Di GitHub, buka **Releases > Draft a new release**, pilih tag `v1.0.0`, tulis
ringkasan dan batasan data, lalu publish.

## 7. Dapatkan DOI kode melalui Zenodo

1. Masuk ke <https://zenodo.org> dengan akun GitHub.
2. Buka integrasi GitHub dan aktifkan repository ini.
3. Buat GitHub release baru. Zenodo akan mengarsipkan release dan memberi DOI.
4. Masukkan DOI versi tersebut ke README dan `CITATION.cff` dalam commit berikutnya.
5. Gunakan DOI konsep Zenodo untuk merujuk semua versi, dan DOI versi tertentu
   saat reproduksi harus tepat.

## 8. Sitasi yang jelas

Dalam README dan artikel turunannya, bedakan:

- sitasi **paper** untuk metode dan temuan ilmiah; dan
- sitasi **software release** untuk implementasi kode yang benar-benar dipakai.

Jangan menjanjikan data AWS terbuka. Arahkan permintaan data sesuai Data
Availability Statement artikel dan izin PT Freeport Indonesia.
