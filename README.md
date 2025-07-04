# Part Number OCR System

Sistem Part Number OCR adalah aplikasi web yang dirancang untuk menyimpan dan memvalidasi part number produk menggunakan teknologi Optical Character Recognition (OCR) dan deteksi objek. Sistem ini mendukung mode inspeksi manual dan otomatis dengan berbagai konfigurasi kamera dan item check yang dapat disesuaikan.

## Fitur Utama

### 1. Mode Inspeksi Manual
- **Upload Gambar**: Pengguna dapat mengupload gambar produk untuk dianalisis
- **Capture dari Kamera**: Mengambil gambar langsung dari kamera yang terhubung
- **Drag-and-Drop Area Selection**: Memilih area spesifik pada gambar untuk analisis OCR
- **Input Manual Part Number**: Memasukkan part number secara manual untuk validasi
- **Preview Real-time**: Melihat hasil seleksi area dan analisis secara langsung

### 2. Mode Inspeksi Otomatis
- **Deteksi Area Teks Otomatis**: Sistem secara otomatis mendeteksi area yang mengandung teks
- **Mode Berkelanjutan**: Inspeksi otomatis dengan interval waktu yang dapat diatur
- **Live Preview**: Menampilkan hasil inspeksi secara real-time
- **Statistik Real-time**: Menampilkan jumlah OK/NG dan persentase keberhasilan

### 3. Manajemen Kamera
- **Deteksi Kamera Otomatis**: Mendeteksi semua kamera yang tersedia di sistem
- **Konfigurasi Kamera**: Mengatur resolusi, brightness, contrast, zoom, dan parameter lainnya
- **Multiple Camera Support**: Mendukung penggunaan beberapa kamera secara bersamaan
- **Preview Kamera**: Melihat feed kamera secara real-time

### 4. Manajemen Produk
- **CRUD Operations**: Create, Read, Update, Delete untuk data produk
- **Part Number Validation**: Validasi format dan keunikan part number
- **Search dan Filter**: Pencarian produk berdasarkan part number atau deskripsi
- **Pagination**: Navigasi data produk dengan pagination

### 5. Item Check Configuration
- **Rule-based Validation**: Konfigurasi aturan validasi menggunakan format JSON
- **Multiple Check Types**: Mendukung berbagai jenis pemeriksaan (part number validation, visual inspection, dimension check, color check)
- **Template Rules**: Template aturan yang sudah predefined untuk kemudahan konfigurasi
- **Active/Inactive Toggle**: Mengaktifkan atau menonaktifkan item check tertentu

### 6. Riwayat Inspeksi
- **Comprehensive History**: Menyimpan semua riwayat inspeksi dengan detail lengkap
- **Filter dan Search**: Filter berdasarkan mode, status, tanggal, dan part number
- **Export Data**: Ekspor data riwayat untuk analisis lebih lanjut
- **Detailed View**: Melihat detail lengkap setiap inspeksi

## Arsitektur Sistem

### Backend (Flask)
- **Framework**: Flask dengan Python 3.11
- **Database**: SQLite dengan SQLAlchemy ORM
- **OCR Engine**: Tesseract OCR
- **Computer Vision**: OpenCV untuk pemrosesan gambar
- **API**: RESTful API dengan CORS support

### Frontend (React)
- **Framework**: React 18 dengan Vite
- **UI Library**: Tailwind CSS + shadcn/ui components
- **Icons**: Lucide React
- **Routing**: React Router DOM
- **State Management**: React Hooks

### Database Schema
- **Products**: Menyimpan data produk dan part number
- **Cameras**: Konfigurasi kamera yang tersedia
- **Inspections**: Riwayat semua inspeksi yang dilakukan
- **ItemChecks**: Aturan validasi tambahan

## Teknologi yang Digunakan

### Backend Dependencies
- Flask 2.3.3
- Flask-SQLAlchemy 3.0.5
- Flask-CORS 4.0.0
- OpenCV-Python 4.11.0
- Pytesseract 0.3.10
- Pillow 10.0.0
- NumPy 1.24.3

### Frontend Dependencies
- React 18.2.0
- React Router DOM 6.15.0
- Tailwind CSS 3.3.0
- Lucide React 0.263.1
- Vite 6.3.5

## Instalasi dan Setup

### Prerequisites
- Python 3.11 atau lebih baru
- Node.js 20.18.0 atau lebih baru
- Tesseract OCR engine
- Kamera USB (opsional)

### Backend Setup
```bash
# Clone repository
git clone <repository-url>
cd part-number-system

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# atau
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Install Tesseract OCR
# Ubuntu/Debian:
sudo apt update && sudo apt install tesseract-ocr

# Run server
python run_server.py
```

### Frontend Setup
```bash
cd part-number-frontend

# Install dependencies
pnpm install

# Run development server
pnpm run dev

# Build for production
pnpm run build
```

## API Endpoints

### Health Check
- `GET /api/health` - Status kesehatan sistem

### Camera Management
- `GET /api/cameras` - Daftar semua kamera
- `POST /api/cameras` - Tambah kamera baru
- `PUT /api/cameras/{id}` - Update konfigurasi kamera
- `DELETE /api/cameras/{id}` - Hapus kamera
- `GET /api/cameras/detect` - Deteksi kamera yang tersedia
- `POST /api/cameras/{id}/capture` - Capture gambar dari kamera

### Product Management
- `GET /api/products` - Daftar produk dengan pagination
- `POST /api/products` - Tambah produk baru
- `PUT /api/products/{id}` - Update produk
- `DELETE /api/products/{id}` - Hapus produk

### Inspection
- `POST /api/inspect/manual` - Inspeksi manual
- `POST /api/inspect/auto` - Inspeksi otomatis
- `POST /api/inspect/area` - Inspeksi area spesifik
- `GET /api/inspections` - Riwayat inspeksi
- `GET /api/inspections/stats` - Statistik inspeksi

### Item Check
- `GET /api/item-checks` - Daftar item check
- `POST /api/item-checks` - Tambah item check baru
- `PUT /api/item-checks/{id}` - Update item check
- `DELETE /api/item-checks/{id}` - Hapus item check
- `POST /api/item-checks/{id}/toggle` - Toggle status aktif/nonaktif

## Konfigurasi

### Environment Variables
```bash
# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key

# Database
DATABASE_URL=sqlite:///app.db

# OCR Configuration
TESSERACT_CMD=/usr/bin/tesseract
```

### Camera Configuration
Sistem mendukung konfigurasi kamera dengan parameter berikut:
- **Resolution**: Width x Height (contoh: 640x480, 1280x720)
- **Brightness**: 0-100
- **Contrast**: 0-100
- **Saturation**: 0-100
- **Zoom**: 1.0-5.0
- **Focus**: Auto/Manual

### Item Check Rules
Item check menggunakan format JSON untuk mendefinisikan aturan validasi:

#### Part Number Validation
```json
{
  "type": "part_number_validation",
  "min_length": 3,
  "max_length": 20,
  "allowed_patterns": ["^[A-Z0-9\\-_]+$"],
  "forbidden_characters": [" ", ".", ","]
}
```

#### Visual Inspection
```json
{
  "type": "visual_inspection",
  "features": [
    {
      "name": "hole_detection",
      "type": "contour",
      "min_area": 100,
      "max_area": 1000,
      "area": {"x": 100, "y": 100, "width": 200, "height": 200}
    }
  ]
}
```

#### Dimension Check
```json
{
  "type": "dimension_check",
  "min_width": 50,
  "max_width": 500,
  "min_height": 30,
  "max_height": 300
}
```

#### Color Check
```json
{
  "type": "color_check",
  "expected_colors": [
    {
      "name": "blue",
      "hsv": [120, 255, 255],
      "min_percentage": 10
    }
  ],
  "tolerance": 20,
  "area": {"x": 0, "y": 0, "width": 100, "height": 100}
}
```

## Penggunaan

### 1. Inspeksi Manual
1. Buka halaman "Inspeksi Manual"
2. Pilih sumber gambar (upload file atau capture dari kamera)
3. Jika menggunakan kamera, pilih kamera yang diinginkan
4. Setelah gambar dimuat, gunakan mouse untuk drag-and-drop area yang ingin dianalisis
5. Klik "Analisis OCR" untuk melakukan ekstraksi teks otomatis
6. Atau masukkan part number secara manual dan klik "Simpan Manual"
7. Sistem akan menampilkan hasil validasi dan status OK/NG

### 2. Inspeksi Otomatis
1. Buka halaman "Inspeksi Otomatis"
2. Pilih kamera yang akan digunakan
3. Atur pengaturan mode berkelanjutan jika diperlukan
4. Klik "Start Inspeksi" untuk memulai inspeksi otomatis
5. Sistem akan secara otomatis mendeteksi area teks dan melakukan validasi
6. Monitor statistik real-time dan hasil inspeksi

### 3. Konfigurasi Kamera
1. Buka halaman "Konfigurasi Kamera"
2. Klik "Deteksi Kamera" untuk mencari kamera yang tersedia
3. Tambah kamera baru dengan mengisi form konfigurasi
4. Atur parameter kamera sesuai kebutuhan
5. Test kamera dengan fitur preview

### 4. Manajemen Produk
1. Buka halaman "Manajemen Produk"
2. Klik "Tambah Produk" untuk menambah produk baru
3. Isi part number dan deskripsi produk
4. Gunakan fitur search untuk mencari produk tertentu
5. Edit atau hapus produk sesuai kebutuhan

### 5. Konfigurasi Item Check
1. Buka halaman "Item Check"
2. Klik "Tambah Item Check" untuk membuat aturan baru
3. Pilih template aturan atau buat custom rule dalam format JSON
4. Atur status aktif/nonaktif sesuai kebutuhan
5. Test aturan dengan endpoint testing

## Troubleshooting

### Common Issues

#### 1. Kamera Tidak Terdeteksi
- Pastikan kamera terhubung dengan benar
- Periksa permission akses kamera
- Restart aplikasi jika diperlukan

#### 2. OCR Tidak Akurat
- Pastikan gambar memiliki kualitas yang baik
- Atur pencahayaan yang optimal
- Gunakan resolusi kamera yang tinggi
- Pilih area deteksi yang tepat

#### 3. Database Error
- Periksa koneksi database
- Pastikan file database memiliki permission yang benar
- Restart server jika diperlukan

#### 4. Performance Issues
- Kurangi resolusi kamera jika tidak diperlukan
- Atur interval inspeksi otomatis yang lebih besar
- Bersihkan riwayat inspeksi lama secara berkala

### Logs dan Monitoring
- Server logs tersedia di console output
- Health check endpoint: `/api/health`
- Monitor statistik inspeksi di dashboard
- Gunakan browser developer tools untuk debugging frontend

## Pengembangan Lanjutan

### Roadmap
1. **Integrasi PLC**: Komunikasi dengan sistem PLC untuk otomasi industri
2. **Machine Learning**: Implementasi model ML untuk deteksi objek yang lebih akurat
3. **Multi-language OCR**: Dukungan untuk berbagai bahasa
4. **Cloud Storage**: Integrasi dengan cloud storage untuk backup data
5. **Mobile App**: Aplikasi mobile untuk inspeksi remote
6. **Advanced Analytics**: Dashboard analytics yang lebih komprehensif

### Contributing
1. Fork repository
2. Buat feature branch
3. Commit changes
4. Push ke branch
5. Create Pull Request

## License
MIT License - lihat file LICENSE untuk detail lengkap.

## Support
Untuk bantuan teknis atau pertanyaan, silakan hubungi tim development atau buat issue di repository GitHub.

---

**Developed by Manus AI**  
Version: 1.0.0  
Last Updated: July 2025

