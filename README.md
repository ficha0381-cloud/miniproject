# miniproject : Deteksi Tanda Tangan
Nama : Icha Febrianti
Nim : F1G124064
Kelas : A
Mata Kuliah : Pengolahan Citra Digital

**TUGAS 6 : DETEKSI TANDA TANGAN (Signature Detection)**

**Alur Pemrosesan (Pipeline)**
**1.	Region of Interest (ROI) Cropping:** Memotong area spesifik pada dokumen yang diperkirakan sebagai lokasi tanda tangan. Pemotongan dilakukan menggunakan pendekatan proporsi/persentase pada area kanan atas gambar. Area yang digunakan adalah 10%-35% dari tinggi gambar dan 65%-95% dari lebar gambar sehingga dapat menyesuaikan ukuran citra.

**2.	 Grayscale Conversion**: Mengubah citra berwarna menjadi citra keabuan (grayscale) untuk mempermudah proses pemisahan antara objek dan latar belakang. 

**3.	Thresholding (Global & Otsu): **Mengubah citra grayscale menjadi citra biner untuk memisahkan bagian foreground dari background. Global Thresholding menggunakan nilai threshold tetap sebesar 127, sedangkan Otsu menentukan nilai threshold secara otomatis berdasarkan distribusi intensitas piksel pada citra. 

**4.	Morphological Operations: **
Opening digunakan untuk membantu menghilangkan noise atau objek kecil yang tidak diperlukan. 
Closing digunakan untuk membantu menutup celah dan menghubungkan bagian foreground yang terputus.
Kedua operasi menggunakan kernel berukuran 3×3 piksel. 

**5.	Pixel Ratio Calculation: **Menghitung jumlah piksel foreground menggunakan cv2.countNonZero(), kemudian menghitung persentase piksel foreground terhadap total piksel pada area ROI. Jika rasio melebihi batas 1.5%, sistem menentukan status SIGNATURE PRESENT. Jika tidak melebihi 1.5%, sistem menentukan SIGNATURE ABSENT.

**Hasil Pengujian**
Sistem diuji menggunakan 9 citra ijazah dengan resolusi 2481×3506 piksel yang memiliki berbagai kondisi kualitas citra.
Dari hasil eksekusi program, diperoleh data sebagai berikut:
•	01_HighQuality_Enhanced: 7.41% (PRESENT) 
•	02_LowContrast: 7.50% (PRESENT) 
•	03_Blurred: 11.69% (PRESENT) 
•	04_HighNoise: 7.16% (PRESENT) 
•	05_LowResolution_Upsampled: 9.20% (PRESENT) 
•	06_Faded_Underexposed: 7.63% (PRESENT) 
•	07_ColorShift_WarmTint: 7.52% (PRESENT) 
•	08_JPEGCompression_Artifacts: 7.72% (PRESENT) 
•	09_CombinedDegradation: 8.81% (PRESENT)
Seluruh citra menghasilkan status SIGNATURE PRESENT karena nilai rasio piksel yang diperoleh berada di atas batas 1.5% yang telah ditentukan pada program.

**Analisis & Kesimpulan**
**1. Mengapa thresholding diperlukan sebelum melakukan analisis keberadaan tanda tangan?**
Thresholding diperlukan untuk mengubah citra grayscale menjadi citra biner sehingga bagian foreground dapat dipisahkan dari background. Dengan proses ini, sistem dapat menghitung jumlah piksel yang dianggap sebagai bagian dari tanda tangan secara matematis. Hasil perhitungan tersebut kemudian digunakan untuk menentukan apakah tanda tangan terdeteksi atau tidak.
**2. Apa masalah yang terjadi jika threshold terlalu tinggi atau terlalu rendah?**
•	Jika Threshold Terlalu Rendah: Sistem dapat kehilangan beberapa bagian tanda tangan yang memiliki intensitas berbeda atau kurang gelap. Akibatnya, jumlah piksel foreground menjadi lebih sedikit dan tanda tangan yang sebenarnya ada berpotensi dianggap tidak ada. 
•	Jika Threshold Terlalu Tinggi: Sistem dapat memasukkan lebih banyak bagian dari background sebagai foreground. Noise, pola pada dokumen, atau tekstur kertas dapat ikut dihitung sehingga jumlah piksel meningkat dan berpotensi menyebabkan sistem mendeteksi tanda tangan padahal sebenarnya tidak ada. 
•	Solusi yang Diterapkan: Pada program digunakan Global Thresholding dengan nilai 127 dan Otsu Thresholding yang menentukan threshold secara otomatis. Hasil Otsu kemudian diproses menggunakan operasi Opening dan Closing untuk membantu mengurangi noise dan memperbaiki hasil segmentasi sebelum dilakukan perhitungan rasio piksel. 
Berdasarkan hasil pengujian, seluruh 9 citra menghasilkan status SIGNATURE PRESENT, dengan rasio piksel antara 7.16% sampai 11.69%. Nilai tersebut berada di atas batas keputusan 1.5% yang digunakan oleh sistem.

