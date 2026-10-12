# ============================================================
# TUGAS: FILTERING, NOISE REDUCTION, SHARPENING + OCR
# Memproses Citra1.png sampai Citra9.png
# ============================================================
#
# Struktur folder:
# analisis_citra/
# ├── Citra1.png
# ├── Citra2.png
# ...
# ├── Citra9.png
# └── main.py
#
# Setelah dijalankan:
# analisis_citra/
# └── hasil/
#     ├── Citra1/
#     │   ├── 01_original.png
#     │   ├── 02_mean_filter.png
#     │   ├── 03_median_filter.png
#     │   ├── 04_gaussian_filter.png
#     │   ├── 05_sharpening.png
#     │   ├── 06_perbandingan_semua_metode.png
#     │   ├── ocr_original.png
#     │   ├── ocr_mean_filter.png
#     │   ├── ocr_median_filter.png
#     │   ├── ocr_gaussian_filter.png
#     │   └── ocr_sharpening.png
#     ├── Citra2/
#     └── ... Citra9/
#     ├── hasil_ocr.txt
#     └── hasil_ocr.csv
#
# Instalasi:
#   py -m pip install opencv-python numpy pytesseract matplotlib
#
# Tesseract OCR harus terpasang terpisah di Windows.
# ============================================================

from pathlib import Path
import csv
import re
import sys

import cv2
import numpy as np
import matplotlib.pyplot as plt
import pytesseract


# =========================
# PENGATURAN
# =========================
BASE_DIR = Path(__file__).resolve().parent
INPUT_DIR = BASE_DIR
OUTPUT_DIR = BASE_DIR / "hasil"

# Semua gambar Citra1 sampai Citra9 diproses.
NOMOR_CITRA = range(1, 10)

# Ukuran kernel untuk filter.
KERNEL_MEAN = 5
KERNEL_MEDIAN = 5
KERNEL_GAUSSIAN = 5

# Sharpening: unsharp masking.
SHARPEN_AMOUNT = 1.5
SHARPEN_SIGMA = 1.0

# OCR.
OCR_PSM = 6

# Untuk ijazah Indonesia, gunakan ind+eng jika bahasa "ind" tersedia.
# Program otomatis memilih ind+eng -> ind -> eng.
TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# ROTASI:
# 0 = tidak diputar
# 90 = putar 90 derajat searah jarum jam
# 180 = terbalik
# 270 = putar 90 derajat berlawanan arah jarum jam
#
# Jika Citra1-Citra9 sudah tegak, biarkan 0.
# Jika semua foto ternyata miring 90 derajat, ubah menjadi 90 atau 270.
ROTASI = 0


# =========================
# FUNGSI BANTUAN
# =========================
def cari_file_citra(nomor):
    """Mencari CitraN dengan beberapa ekstensi umum."""
    for ext in [".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"]:
        p = INPUT_DIR / f"Citra{nomor}{ext}"
        if p.exists():
            return p

    # Jika nama file memakai variasi huruf besar/kecil.
    pola = re.compile(rf"^citra{nomor}\.(png|jpg|jpeg|bmp|tif|tiff)$", re.I)
    for p in INPUT_DIR.iterdir():
        if p.is_file() and pola.match(p.name):
            return p

    return None


def putar_gambar(img, derajat):
    if derajat == 90:
        return cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
    if derajat == 180:
        return cv2.rotate(img, cv2.ROTATE_180)
    if derajat == 270:
        return cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
    return img


def unsharp_sharpen(gray):
    blur = cv2.GaussianBlur(gray, (0, 0), SHARPEN_SIGMA)
    # Unsharp masking: original + amount*(original - blur)
    sharp = cv2.addWeighted(gray, SHARPEN_AMOUNT, blur,
                            -(SHARPEN_AMOUNT - 1.0), 0)
    return sharp


def buat_filter(gray):
    mean_img = cv2.blur(gray, (KERNEL_MEAN, KERNEL_MEAN))
    median_img = cv2.medianBlur(gray, KERNEL_MEDIAN)
    gaussian_img = cv2.GaussianBlur(
        gray, (KERNEL_GAUSSIAN, KERNEL_GAUSSIAN), 0
    )
    sharpening_img = unsharp_sharpen(gray)

    return {
        "Original": gray,
        "Mean Filter": mean_img,
        "Median Filter": median_img,
        "Gaussian Filter": gaussian_img,
        "Sharpening": sharpening_img,
    }


def siapkan_untuk_ocr(img):
    """
    Preprocessing OCR yang sama untuk semua metode agar perbandingan adil:
    1) perbesar 2x
    2) Otsu threshold
    """
    besar = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    _, binary = cv2.threshold(
        besar, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )
    return binary


def konfigurasi_tesseract():
    """Mengatur executable Tesseract jika ada."""
    calon = [
        Path(TESSERACT_PATH),
        Path(r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"),
    ]

    for p in calon:
        if p.exists():
            pytesseract.pytesseract.tesseract_cmd = str(p)
            return True

    # Coba PATH Windows.
    try:
        pytesseract.get_tesseract_version()
        return True
    except Exception:
        return False


def pilih_bahasa_ocr():
    """Pilih bahasa yang tersedia."""
    try:
        langs = pytesseract.get_languages(config="")
    except Exception:
        return "eng"

    if "ind" in langs and "eng" in langs:
        return "ind+eng"
    if "ind" in langs:
        return "ind"
    if "eng" in langs:
        return "eng"
    return "eng"


def ocr_gambar(img, lang):
    config = f"--oem 3 --psm {OCR_PSM}"
    text = pytesseract.image_to_string(img, lang=lang, config=config)
    return text.strip()


def normalisasi_teks(text):
    # Untuk perbandingan karakter: samakan spasi/baris dan huruf besar-kecil.
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n+", "\n", text)
    return text.strip().lower()


def levenshtein(a, b):
    """Edit distance tanpa library tambahan."""
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)

    if len(a) > len(b):
        a, b = b, a

    prev = list(range(len(a) + 1))

    for j, cb in enumerate(b, start=1):
        curr = [j]
        for i, ca in enumerate(a, start=1):
            insert = curr[i - 1] + 1
            delete = prev[i] + 1
            replace = prev[i - 1] + (ca != cb)
            curr.append(min(insert, delete, replace))
        prev = curr

    return prev[-1]


def hitung_akurasi(reference, prediction):
    """
    Menghitung kemiripan karakter berbasis Levenshtein.
    Tanpa ground truth, hasil dikosongkan dan TIDAK dibuat-buat.
    """
    ref = normalisasi_teks(reference)
    pred = normalisasi_teks(prediction)

    if not ref:
        return None, None

    jarak = levenshtein(ref, pred)
    karakter_benar_estimasi = max(0, len(ref) - jarak)
    akurasi = max(0.0, (1 - jarak / len(ref)) * 100)
    return karakter_benar_estimasi, akurasi


def simpan_perbandingan(nama_citra, images, path_output):
    judul = list(images.keys())

    fig, axes = plt.subplots(1, 5, figsize=(20, 7))
    fig.suptitle(
        f"{nama_citra} - Perbandingan Filtering dan Sharpening",
        fontsize=16,
        fontweight="bold"
    )

    for ax, title in zip(axes, judul):
        # cmap gray agar tampilan konsisten.
        ax.imshow(images[title], cmap="gray")
        ax.set_title(title, fontsize=11)
        ax.axis("off")

    plt.tight_layout()
    fig.savefig(path_output, dpi=200, bbox_inches="tight")
    plt.close(fig)


def simpan_perbandingan_ocr(nama_citra, images, path_output):
    judul = list(images.keys())

    fig, axes = plt.subplots(1, 5, figsize=(20, 7))
    fig.suptitle(
        f"{nama_citra} - Gambar Masukan OCR",
        fontsize=16,
        fontweight="bold"
    )

    for ax, title in zip(axes, judul):
        ax.imshow(images[title], cmap="gray")
        ax.set_title(title, fontsize=11)
        ax.axis("off")

    plt.tight_layout()
    fig.savefig(path_output, dpi=200, bbox_inches="tight")
    plt.close(fig)


# =========================
# PROGRAM UTAMA
# =========================
def main():
    print("=" * 72)
    print("FILTERING, NOISE REDUCTION, SHARPENING DAN OCR")
    print("MEMPROSES CITRA 1 SAMPAI CITRA 9")
    print("=" * 72)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Cek seluruh input sebelum mulai agar jelas jika ada file yang kurang.
    files = {}
    for n in NOMOR_CITRA:
        p = cari_file_citra(n)
        if p is not None:
            files[n] = p

    print("\nPemeriksaan input:")
    for n in NOMOR_CITRA:
        if n in files:
            print(f"  [OK] Citra{n}: {files[n].name}")
        else:
            print(f"  [GAGAL] Citra{n}: file tidak ditemukan")

    if len(files) != 9:
        print("\nERROR: Tidak ditemukan lengkap 9 gambar.")
        print("Pastikan file bernama Citra1.png sampai Citra9.png")
        print("dan berada satu folder dengan main.py.")
        sys.exit(1)

    # OCR setup
    tesseract_ok = konfigurasi_tesseract()
    if tesseract_ok:
        lang = pilih_bahasa_ocr()
        print(f"\n[OK] Tesseract siap. Bahasa OCR: {lang}")
    else:
        lang = "eng"
        print("\n[PERINGATAN] Tesseract OCR belum ditemukan.")
        print("Filtering tetap akan dijalankan.")
        print("Untuk OCR, install Tesseract lalu jalankan program lagi.")

    semua_hasil = []

    for nomor in NOMOR_CITRA:
        input_path = files[nomor]
        nama_citra = f"Citra{nomor}"
        folder = OUTPUT_DIR / nama_citra
        folder.mkdir(parents=True, exist_ok=True)

        print("\n" + "-" * 72)
        print(f"MEMPROSES {nama_citra}: {input_path.name}")
        print("-" * 72)

        img = cv2.imread(str(input_path))
        if img is None:
            print(f"[GAGAL] Gambar tidak dapat dibaca: {input_path}")
            continue

        # Koreksi rotasi sesuai pengaturan.
        img = putar_gambar(img, ROTASI)

        # Grayscale.
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        hasil_filter = buat_filter(gray)

        # Simpan semua hasil filter.
        nama_file = {
            "Original": "01_original.png",
            "Mean Filter": "02_mean_filter.png",
            "Median Filter": "03_median_filter.png",
            "Gaussian Filter": "04_gaussian_filter.png",
            "Sharpening": "05_sharpening.png",
        }

        for metode, hasil in hasil_filter.items():
            cv2.imwrite(str(folder / nama_file[metode]), hasil)

        # Gambar perbandingan visual.
        simpan_perbandingan(
            nama_citra,
            hasil_filter,
            folder / "06_perbandingan_semua_metode.png"
        )

        # OCR
        hasil_ocr_citra = {}

        for metode, hasil in hasil_filter.items():
            ocr_input = siapkan_untuk_ocr(hasil)

            cv2.imwrite(
                str(folder / f"ocr_{metode.lower().replace(' ', '_')}.png"),
                ocr_input
            )

            if tesseract_ok:
                try:
                    text = ocr_gambar(ocr_input, lang)
                except Exception as e:
                    text = f"[OCR ERROR] {e}"
            else:
                text = "[Tesseract belum terpasang]"

            hasil_ocr_citra[metode] = text

        # Perbandingan gambar yang benar-benar masuk ke OCR.
        ocr_images = {
            metode: siapkan_untuk_ocr(img_filter)
            for metode, img_filter in hasil_filter.items()
        }
        simpan_perbandingan_ocr(
            nama_citra,
            ocr_images,
            folder / "07_perbandingan_OCR.png"
        )

        # Simpan teks OCR satu citra.
        txt_path = folder / "hasil_ocr.txt"
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(f"{nama_citra}\n")
            f.write("=" * 60 + "\n\n")
            for metode, text in hasil_ocr_citra.items():
                f.write(f"===== {metode.upper()} =====\n")
                f.write(text)
                f.write("\n\n")

        # Data tabel.
        for metode, text in hasil_ocr_citra.items():
            semua_hasil.append({
                "Citra": nama_citra,
                "Metode": metode,
                "Hasil OCR": text.replace("\n", " "),
                "Karakter Benar": "",
                "Akurasi (%)": "",
            })

        print(f"[OK] Hasil disimpan di: {folder}")

    # CSV gabungan.
    csv_path = OUTPUT_DIR / "hasil_ocr.csv"
    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
        fieldnames = [
            "Citra",
            "Metode",
            "Hasil OCR",
            "Karakter Benar",
            "Akurasi (%)",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(semua_hasil)

    # Penjelasan akurasi.
    info_path = OUTPUT_DIR / "README_AKURASI.txt"
    with open(info_path, "w", encoding="utf-8") as f:
        f.write(
            "AKURASI OCR\n"
            "===========\n\n"
            "Kolom Karakter Benar dan Akurasi (%) sengaja belum diisi otomatis\n"
            "karena akurasi wajib dibandingkan dengan GROUND TRUTH/reference text.\n"
            "Jangan menggunakan hasil OCR sendiri sebagai ground truth karena akan\n"
            "membuat pengukuran tidak valid.\n\n"
            "Jika sudah memiliki teks referensi, gunakan rumus:\n"
            "Akurasi (%) = (1 - edit_distance(reference, OCR) / panjang(reference)) x 100\n"
        )

    print("\n" + "=" * 72)
    print("SEMUA CITRA 1-9 SELESAI DIPROSES")
    print("=" * 72)
    print(f"Hasil lengkap: {OUTPUT_DIR}")
    print(f"Tabel OCR:     {csv_path}")
    print("\nBuka folder hasil/Citra1 sampai hasil/Citra9.")
    print("File 06_perbandingan_semua_metode.png adalah perbandingan visual.")
    print("File 07_perbandingan_OCR.png adalah perbandingan masukan OCR.")


if __name__ == "__main__":
    main()
