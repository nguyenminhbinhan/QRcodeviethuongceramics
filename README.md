# Thư Viện Mã QR Toàn Bộ Sản Phẩm Việt Hương Ceramics (https://viethuongceramics.com/)

Dự án tự động cào và sinh mã QR cho toàn bộ sản phẩm trên website Việt Hương Ceramics. Toàn bộ mã QR được tạo theo chuẩn PNG RGB 24-bit sắc nét, phân cấp folder chặt chẽ theo 2 tầng: **Thể loại lớn &rarr; Thể loại nhỏ riêng biệt &rarr; Mã QR từng sản phẩm**.

---

## 📁 Cấu Trúc Thư Mục Phân Cấp Hoàn Chỉnh

```text
QRcodeviethuongceramics/
├── Sản phẩm/                                   <-- Thư mục gốc chứa các thể loại lớn
│   ├── Gạch Nhập Khẩu Cao Cấp/
│   │   ├── Gạch Ấn Độ/                         (77 mã QR)
│   │   ├── Gạch Italy/                         (26 mã QR)
│   │   ├── Gạch Malaysia/                      (4 mã QR)
│   │   ├── Gạch Tây Ban Nha/                   (29 mã QR)
│   │   ├── Gạch Thụy Sỹ/                       (2 mã QR)
│   │   └── Gạch Trung Quốc/                    (206 mã QR)
│   ├── Thiết Bị Vệ Sinh Cao Cấp/
│   │   ├── Bồn Cầu/                            (15 mã QR)
│   │   ├── Chậu Rửa/                           (25 mã QR)
│   │   ├── Gương Treo Tường/                   (3 mã QR)
│   │   ├── Vòi Nước/                           (14 mã QR)
│   │   └── Vòi Sen Tắm/                        (20 mã QR)
│   ├── Thiết Bị Vệ Sinh Eurovinto/
│   │   ├── Bồn Cầu/                            (10 mã QR)
│   │   ├── Chậu Rửa/                           (19 mã QR)
│   │   ├── Gương Treo Tường/                   (3 mã QR)
│   │   ├── Vòi Nước/                           (14 mã QR)
│   │   └── Vòi Sen Tắm/                        (20 mã QR)
│   ├── Thiết Bị Vệ Sinh Star Thái Lan/
│   │   ├── Bồn Cầu/                            (4 mã QR)
│   │   └── Chậu Rửa/                           (6 mã QR)
│   └── Sản Phẩm Khác/
│       ├── Decorative Tiles/                   (24 mã QR)
│       ├── Flooring Tiles/                     (9 mã QR)
│       ├── Gạch Bóng Kiếng/                    (145 mã QR)
│       ├── Gạch Mờ/                            (108 mã QR)
│       ├── Gạch Mosaic/                        (2 mã QR)
│       ├── Gạch Satin/                         (1 mã QR)
│       ├── Gạch Terrazzo/                      (7 mã QR)
│       ├── Gạch Trang Trí/                     (17 mã QR)
│       ├── Gạch Vân Gỗ/                        (58 mã QR)
│       ├── Imported Tiles/                     (5 mã QR)
│       └── Wall Tiles/                         (7 mã QR)
├── index.html                                  <-- Dashboard tra cứu & xem QR trực tiếp
├── danh_sach_san_pham.csv                      <-- Bảng Excel/CSV thống kê sản phẩm
├── danh_sach_san_pham.json                     <-- Dữ liệu JSON chi tiết sản phẩm
├── generate_qrcodes_viethuong.py               <-- Script Python chạy tự động
└── README.md                                   <-- Tài liệu hướng dẫn này
```

---

## 📊 Bảng Thống Kê Chi Tiết Phân Loại

### 📂 Gạch Nhập Khẩu Cao Cấp (344 sản phẩm)
| STT | Thể Loại Con (Loại Nhỏ Riêng) | Số Lượng Sản Phẩm | Đường Dẫn Folder |
| :---: | :--- | :---: | :--- |
| 1 | **Gạch Italy** | 26 mã QR | `Sản phẩm/Gạch Nhập Khẩu Cao Cấp/Gạch Italy/` |
| 2 | **Gạch Malaysia** | 4 mã QR | `Sản phẩm/Gạch Nhập Khẩu Cao Cấp/Gạch Malaysia/` |
| 3 | **Gạch Thụy Sỹ** | 2 mã QR | `Sản phẩm/Gạch Nhập Khẩu Cao Cấp/Gạch Thụy Sỹ/` |
| 4 | **Gạch Trung Quốc** | 206 mã QR | `Sản phẩm/Gạch Nhập Khẩu Cao Cấp/Gạch Trung Quốc/` |
| 5 | **Gạch Tây Ban Nha** | 29 mã QR | `Sản phẩm/Gạch Nhập Khẩu Cao Cấp/Gạch Tây Ban Nha/` |
| 6 | **Gạch Ấn Độ** | 77 mã QR | `Sản phẩm/Gạch Nhập Khẩu Cao Cấp/Gạch Ấn Độ/` |

### 📂 Sản Phẩm Khác (383 sản phẩm)
| STT | Thể Loại Con (Loại Nhỏ Riêng) | Số Lượng Sản Phẩm | Đường Dẫn Folder |
| :---: | :--- | :---: | :--- |
| 1 | **Decorative Tiles** | 24 mã QR | `Sản phẩm/Sản Phẩm Khác/Decorative Tiles/` |
| 2 | **Flooring Tiles** | 9 mã QR | `Sản phẩm/Sản Phẩm Khác/Flooring Tiles/` |
| 3 | **Gạch Bóng Kiếng** | 145 mã QR | `Sản phẩm/Sản Phẩm Khác/Gạch Bóng Kiếng/` |
| 4 | **Gạch Mosaic** | 2 mã QR | `Sản phẩm/Sản Phẩm Khác/Gạch Mosaic/` |
| 5 | **Gạch Mờ** | 108 mã QR | `Sản phẩm/Sản Phẩm Khác/Gạch Mờ/` |
| 6 | **Gạch Satin** | 1 mã QR | `Sản phẩm/Sản Phẩm Khác/Gạch Satin/` |
| 7 | **Gạch Terrazzo** | 7 mã QR | `Sản phẩm/Sản Phẩm Khác/Gạch Terrazzo/` |
| 8 | **Gạch Trang Trí** | 17 mã QR | `Sản phẩm/Sản Phẩm Khác/Gạch Trang Trí/` |
| 9 | **Gạch Vân Gỗ** | 58 mã QR | `Sản phẩm/Sản Phẩm Khác/Gạch Vân Gỗ/` |
| 10 | **Imported Tiles** | 5 mã QR | `Sản phẩm/Sản Phẩm Khác/Imported Tiles/` |
| 11 | **Wall Tiles** | 7 mã QR | `Sản phẩm/Sản Phẩm Khác/Wall Tiles/` |

### 📂 Thiết Bị Vệ Sinh Eurovinto (66 sản phẩm)
| STT | Thể Loại Con (Loại Nhỏ Riêng) | Số Lượng Sản Phẩm | Đường Dẫn Folder |
| :---: | :--- | :---: | :--- |
| 1 | **Bồn Cầu** | 10 mã QR | `Sản phẩm/Thiết Bị Vệ Sinh Eurovinto/Bồn Cầu/` |
| 2 | **Chậu Rửa** | 19 mã QR | `Sản phẩm/Thiết Bị Vệ Sinh Eurovinto/Chậu Rửa/` |
| 3 | **Gương Treo Tường** | 3 mã QR | `Sản phẩm/Thiết Bị Vệ Sinh Eurovinto/Gương Treo Tường/` |
| 4 | **Vòi Nước** | 14 mã QR | `Sản phẩm/Thiết Bị Vệ Sinh Eurovinto/Vòi Nước/` |
| 5 | **Vòi Sen Tắm** | 20 mã QR | `Sản phẩm/Thiết Bị Vệ Sinh Eurovinto/Vòi Sen Tắm/` |

### 📂 Thiết Bị Vệ Sinh Nhập Khẩu (77 sản phẩm)
| STT | Thể Loại Con (Loại Nhỏ Riêng) | Số Lượng Sản Phẩm | Đường Dẫn Folder |
| :---: | :--- | :---: | :--- |
| 1 | **Bồn Cầu** | 15 mã QR | `Sản phẩm/Thiết Bị Vệ Sinh Nhập Khẩu/Bồn Cầu/` |
| 2 | **Chậu Rửa** | 25 mã QR | `Sản phẩm/Thiết Bị Vệ Sinh Nhập Khẩu/Chậu Rửa/` |
| 3 | **Gương Treo Tường** | 3 mã QR | `Sản phẩm/Thiết Bị Vệ Sinh Nhập Khẩu/Gương Treo Tường/` |
| 4 | **Vòi Nước** | 14 mã QR | `Sản phẩm/Thiết Bị Vệ Sinh Nhập Khẩu/Vòi Nước/` |
| 5 | **Vòi Sen Tắm** | 20 mã QR | `Sản phẩm/Thiết Bị Vệ Sinh Nhập Khẩu/Vòi Sen Tắm/` |

### 📂 Thiết Bị Vệ Sinh Star Thái Lan (10 sản phẩm)
| STT | Thể Loại Con (Loại Nhỏ Riêng) | Số Lượng Sản Phẩm | Đường Dẫn Folder |
| :---: | :--- | :---: | :--- |
| 1 | **Bồn Cầu** | 4 mã QR | `Sản phẩm/Thiết Bị Vệ Sinh Star Thái Lan/Bồn Cầu/` |
| 2 | **Chậu Rửa** | 6 mã QR | `Sản phẩm/Thiết Bị Vệ Sinh Star Thái Lan/Chậu Rửa/` |


---

## 🚀 Hướng Dẫn Sử Dụng

1. **Xem trực tiếp mã QR trong thư mục:**
   - Mở thư mục `QRcodeviethuongceramics/Sản phẩm/`.
   - Chọn thể loại lớn mong muốn, sau đó vào thể loại nhỏ riêng.
   - Mỗi file ảnh `.png` là mã QR độ nét cao trỏ đúng đến link bài viết của sản phẩm đó trên website viethuongceramics.com.
   - Dễ dàng chèn vào catalogue, slide thuyết trình, in nhãn dán showroom hoặc gửi khách hàng.

2. **Sử dụng Dashboard Web (`index.html`):**
   - Click đúp mở file `index.html` trên bất kỳ trình duyệt nào (chạy offline 100%, không cần kết nối mạng).
   - Lọc nhanh 2 tầng: Chọn Thể loại lớn &rarr; Chọn Thể loại con.
   - Tìm kiếm trực tiếp theo tên, mã gạch hoặc loại thiết bị.
   - Quét mã QR ngay trên màn hình hoặc click tải file ảnh về máy.

3. **Cập nhật dữ liệu mới khi website thêm sản phẩm:**
   - Chạy lệnh:
     ```bash
     python3 generate_qrcodes_viethuong.py
     ```
