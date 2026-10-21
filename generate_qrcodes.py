#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tự động thu thập toàn bộ 794+ sản phẩm từ website Việt Hương Ceramics (https://viethuongceramics.com/)
và tạo mã QR độ phân giải cao cho từng sản phẩm, tổ chức theo cấu trúc phân cấp chặt chẽ:
  QRcodeviethuongceramics/
    └── Sản phẩm/
          └── [Thể loại lớn]/
                └── [Thể loại nhỏ riêng]/
                      └── [Tên sản phẩm].png
Tự động xuất bảng HTML xem trước tương tác cao cấp (chạy offline 100%, không bị chặn CORS).
"""

import os
import sys
import json
import csv
import html
import re
import unicodedata
import urllib.request
import qrcode
from PIL import Image

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.join(SCRIPT_DIR, "QRcodeviethuongceramics")
OUTPUT_DIR = os.path.join(PROJECT_DIR, "Sản phẩm")

API_BASE = "https://viethuongceramics.com/wp-json/wc/store/v1"

def sanitize_filename(name):
    """Làm sạch tên file để tương thích an toàn trên tất cả hệ điều hành."""
    name = unicodedata.normalize('NFC', html.unescape(name)).strip()
    name = name.replace('/', '-')
    name = name.replace('*', 'x')
    name = name.replace('×', 'x')
    name = name.replace(':', '-')
    name = name.replace('"', '')
    name = name.replace('?', '')
    name = name.replace('<', '')
    name = name.replace('>', '')
    name = name.replace('|', '-')
    name = name.replace('·', '-')
    name = re.sub(r'\s+', ' ', name)
    return name

def sanitize_category(cat_name):
    """Chuẩn hóa tên thể loại."""
    cat_name = unicodedata.normalize('NFC', html.unescape(cat_name)).strip()
    cat_name = cat_name.replace('–', '-')
    cat_name = cat_name.replace('/', '-')
    cat_name = re.sub(r'\s+', ' ', cat_name)
    return cat_name

def fetch_categories():
    """Tải toàn bộ cây danh mục từ WooCommerce Store API."""
    print("-> Đang tải danh mục từ viethuongceramics.com...")
    all_cats = []
    page = 1
    while True:
        req_url = f"{API_BASE}/products/categories?per_page=100&page={page}"
        req = urllib.request.Request(req_url, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                if not data:
                    break
                all_cats.extend(data)
                page += 1
        except Exception as e:
            break

    cat_dict = {}
    for c in all_cats:
        name = sanitize_category(c['name'])
        cat_dict[c['id']] = {
            'id': c['id'],
            'name': name,
            'slug': c['slug'],
            'parent': c['parent']
        }
    print(f"   Đã tải {len(cat_dict)} danh mục.")
    return cat_dict

def fetch_all_products():
    """Tải tất cả sản phẩm từ WooCommerce Store API."""
    print("-> Đang tải toàn bộ sản phẩm từ viethuongceramics.com...")
    products = []
    page = 1
    while True:
        req_url = f"{API_BASE}/products?per_page=100&page={page}"
        req = urllib.request.Request(req_url, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                if not data:
                    break
                products.extend(data)
                print(f"   Trang {page}: tải được {len(data)} sản phẩm (tổng: {len(products)})")
                page += 1
        except Exception as e:
            print(f"   Kết thúc tải: {e}")
            break
    print(f"-> Tổng cộng đã lấy được {len(products)} sản phẩm.")
    return products

# Cache mã QR theo URL để tối ưu tốc độ sinh ảnh
QR_CACHE = {}

def get_or_create_qr_image(url):
    """Tạo hoặc lấy từ cache ảnh mã QR RGB."""
    if url in QR_CACHE:
        return QR_CACHE[url]
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=12,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    QR_CACHE[url] = img
    return img

def generate_html_viewer(records, hierarchy_summary, project_dir):
    """Tạo giao diện web sang trọng tra cứu và quét mã QR theo phân cấp 2 tầng."""
    html_path = os.path.join(project_dir, "index.html")
    
    products_json_str = json.dumps(records, ensure_ascii=False)
    hierarchy_json_str = json.dumps(hierarchy_summary, ensure_ascii=False)

    html_content = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Việt Hương Ceramics - Thư Viện Mã QR Toàn Bộ Sản Phẩm</title>
    <meta name="description" content="Hệ thống tra cứu và quét mã QR toàn bộ {len(records)} sản phẩm gạch ốp lát và thiết bị vệ sinh Việt Hương Ceramics theo thể loại cha con.">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Playfair+Display:wght@600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-body: #0a0e17;
            --bg-card: rgba(18, 26, 43, 0.75);
            --bg-card-hover: rgba(26, 38, 64, 0.95);
            --border-color: rgba(212, 175, 55, 0.2);
            --border-hover: rgba(212, 175, 55, 0.6);
            --gold-primary: #d4af37;
            --gold-glow: #f59e0b;
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --text-muted: #64748b;
            --accent-blue: #38bdf8;
            --accent-green: #10b981;
            --glass-bg: rgba(13, 20, 36, 0.85);
            --glass-border: rgba(255, 255, 255, 0.08);
            --radius-lg: 16px;
            --radius-md: 12px;
            --radius-sm: 8px;
            --shadow-card: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
            --shadow-glow: 0 0 25px rgba(212, 175, 55, 0.25);
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
            background-color: var(--bg-body);
            color: var(--text-primary);
            line-height: 1.6;
            min-height: 100vh;
            background-image: 
                radial-gradient(circle at 10% 10%, rgba(212, 175, 55, 0.07) 0%, transparent 40%),
                radial-gradient(circle at 90% 90%, rgba(56, 189, 248, 0.07) 0%, transparent 40%),
                radial-gradient(circle at 50% 50%, rgba(15, 23, 42, 0.95) 0%, #060911 100%);
            background-attachment: fixed;
            padding-bottom: 60px;
        }}

        /* Header Bar */
        header {{
            position: sticky;
            top: 0;
            z-index: 100;
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            background: var(--glass-bg);
            border-bottom: 1px solid var(--glass-border);
            padding: 16px 24px;
        }}

        .header-inner {{
            max-width: 1400px;
            margin: 0 auto;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 20px;
            flex-wrap: wrap;
        }}

        .logo-group {{
            display: flex;
            align-items: center;
            gap: 14px;
        }}

        .logo-badge {{
            width: 44px;
            height: 44px;
            border-radius: var(--radius-md);
            background: linear-gradient(135deg, var(--gold-primary), var(--gold-glow));
            display: flex;
            align-items: center;
            justify-content: center;
            color: #0b0f19;
            font-weight: 800;
            font-size: 18px;
            box-shadow: 0 4px 15px rgba(212, 175, 55, 0.3);
        }}

        .brand-text h1 {{
            font-family: 'Playfair Display', serif;
            font-size: 22px;
            font-weight: 700;
            letter-spacing: 0.5px;
            background: linear-gradient(to right, #ffffff, var(--gold-primary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}

        .brand-text p {{
            font-size: 12px;
            color: var(--text-secondary);
            font-weight: 500;
        }}

        .stats-summary {{
            display: flex;
            align-items: center;
            gap: 12px;
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid var(--glass-border);
            padding: 8px 18px;
            border-radius: 999px;
            font-size: 13px;
        }}

        .stats-item {{
            display: flex;
            align-items: center;
            gap: 6px;
        }}

        .stats-item strong {{
            color: var(--gold-primary);
            font-size: 15px;
        }}

        .stats-divider {{
            width: 1px;
            height: 14px;
            background: var(--glass-border);
        }}

        /* Hero */
        .hero {{
            max-width: 1400px;
            margin: 30px auto 20px auto;
            padding: 0 24px;
            text-align: center;
        }}

        .hero h2 {{
            font-family: 'Playfair Display', serif;
            font-size: 32px;
            font-weight: 700;
            margin-bottom: 8px;
            background: linear-gradient(to right, #f8fafc, #d4af37, #f8fafc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}

        .hero p {{
            color: var(--text-secondary);
            font-size: 14px;
            max-width: 850px;
            margin: 0 auto;
        }}

        /* Controls Section */
        .controls-container {{
            max-width: 1400px;
            margin: 25px auto;
            padding: 0 24px;
            display: flex;
            flex-direction: column;
            gap: 14px;
        }}

        .search-box {{
            position: relative;
            width: 100%;
        }}

        .search-input {{
            width: 100%;
            background: rgba(22, 29, 49, 0.85);
            border: 1px solid var(--glass-border);
            padding: 14px 20px 14px 50px;
            border-radius: var(--radius-lg);
            color: var(--text-primary);
            font-size: 15px;
            font-family: inherit;
            outline: none;
            transition: all 0.25s ease;
        }}

        .search-input:focus {{
            border-color: var(--gold-primary);
            box-shadow: 0 0 20px rgba(212, 175, 55, 0.2);
            background: rgba(22, 29, 49, 1);
        }}

        .search-icon {{
            position: absolute;
            left: 18px;
            top: 50%;
            transform: translateY(-50%);
            color: var(--text-muted);
            pointer-events: none;
        }}

        /* 2-Tier Category Navigation */
        .filter-section {{
            display: flex;
            flex-direction: column;
            gap: 10px;
        }}

        .filter-label {{
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.8px;
            color: var(--gold-primary);
        }}

        .nav-pills {{
            display: flex;
            align-items: center;
            gap: 10px;
            overflow-x: auto;
            padding-bottom: 6px;
            scrollbar-width: thin;
            scrollbar-color: var(--gold-primary) transparent;
        }}

        .nav-pills::-webkit-scrollbar {{
            height: 4px;
        }}
        .nav-pills::-webkit-scrollbar-thumb {{
            background: var(--gold-primary);
            border-radius: 4px;
        }}

        .pill-btn {{
            white-space: nowrap;
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid var(--glass-border);
            color: var(--text-secondary);
            padding: 7px 14px;
            border-radius: 999px;
            font-size: 13px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            gap: 6px;
        }}

        .pill-btn:hover {{
            background: rgba(212, 175, 55, 0.1);
            color: var(--gold-primary);
            border-color: var(--border-color);
        }}

        .pill-btn.active {{
            background: linear-gradient(135deg, var(--gold-primary), var(--gold-glow));
            color: #0b0f19;
            font-weight: 700;
            border-color: transparent;
            box-shadow: 0 4px 15px rgba(212, 175, 55, 0.35);
        }}

        .pill-count {{
            background: rgba(0, 0, 0, 0.25);
            padding: 2px 7px;
            border-radius: 12px;
            font-size: 11px;
        }}

        .pill-btn.active .pill-count {{
            background: rgba(0, 0, 0, 0.35);
            color: #ffffff;
        }}

        /* Subcategory Pills Container */
        .sub-nav-wrapper {{
            background: rgba(18, 26, 43, 0.4);
            border: 1px solid var(--glass-border);
            border-radius: var(--radius-md);
            padding: 10px 14px;
        }}

        /* Grid */
        .products-grid {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 24px;
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 20px;
        }}

        .product-card {{
            background: var(--bg-card);
            border: 1px solid var(--glass-border);
            border-radius: var(--radius-lg);
            padding: 18px;
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
            backdrop-filter: blur(10px);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: var(--shadow-card);
            position: relative;
            overflow: hidden;
        }}

        .product-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, transparent, var(--gold-primary), transparent);
            opacity: 0;
            transition: opacity 0.3s ease;
        }}

        .product-card:hover {{
            transform: translateY(-5px);
            border-color: var(--border-hover);
            background: var(--bg-card-hover);
            box-shadow: var(--shadow-glow);
        }}

        .product-card:hover::before {{
            opacity: 1;
        }}

        .card-badges {{
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            justify-content: center;
            margin-bottom: 12px;
        }}

        .card-category {{
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.6px;
            color: var(--accent-blue);
            background: rgba(56, 189, 248, 0.1);
            padding: 3px 8px;
            border-radius: 999px;
        }}

        .card-subcategory {{
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.6px;
            color: var(--gold-primary);
            background: rgba(212, 175, 55, 0.1);
            padding: 3px 8px;
            border-radius: 999px;
        }}

        .qr-wrapper {{
            background: #ffffff;
            padding: 10px;
            border-radius: var(--radius-md);
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
            margin-bottom: 14px;
            transition: transform 0.2s ease;
            cursor: pointer;
        }}

        .qr-wrapper:hover {{
            transform: scale(1.05);
        }}

        .qr-img {{
            display: block;
            width: 160px;
            height: 160px;
            image-rendering: pixelated;
        }}

        .product-name {{
            font-size: 14px;
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 8px;
            line-height: 1.4;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
            min-height: 40px;
        }}

        .card-actions {{
            display: flex;
            align-items: center;
            gap: 8px;
            width: 100%;
            margin-top: auto;
            padding-top: 12px;
            border-top: 1px solid rgba(255, 255, 255, 0.06);
        }}

        .btn-link {{
            flex: 1;
            padding: 8px 10px;
            font-size: 12px;
            font-weight: 600;
            border-radius: var(--radius-sm);
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
            transition: all 0.2s ease;
            cursor: pointer;
            border: 1px solid var(--glass-border);
            background: rgba(255, 255, 255, 0.05);
            color: var(--text-primary);
        }}

        .btn-link:hover {{
            background: rgba(255, 255, 255, 0.12);
            border-color: rgba(255, 255, 255, 0.2);
        }}

        .btn-download {{
            background: linear-gradient(135deg, rgba(212, 175, 55, 0.2), rgba(245, 158, 11, 0.2));
            color: var(--gold-primary);
            border-color: rgba(212, 175, 55, 0.4);
        }}

        .btn-download:hover {{
            background: linear-gradient(135deg, var(--gold-primary), var(--gold-glow));
            color: #0b0f19;
            border-color: transparent;
        }}

        /* Empty State */
        .empty-state {{
            grid-column: 1 / -1;
            text-align: center;
            padding: 80px 20px;
            color: var(--text-muted);
        }}

        /* Modal Preview */
        .modal {{
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background: rgba(5, 8, 15, 0.85);
            backdrop-filter: blur(8px);
            align-items: center;
            justify-content: center;
            padding: 20px;
        }}

        .modal.active {{
            display: flex;
        }}

        .modal-box {{
            background: #111827;
            border: 1px solid var(--border-color);
            border-radius: var(--radius-lg);
            padding: 30px;
            max-width: 460px;
            width: 100%;
            text-align: center;
            position: relative;
            box-shadow: 0 20px 50px rgba(0, 0, 0, 0.7);
        }}

        .modal-close {{
            position: absolute;
            top: 14px;
            right: 14px;
            background: transparent;
            border: none;
            color: var(--text-muted);
            font-size: 24px;
            cursor: pointer;
            transition: color 0.2s;
        }}

        .modal-close:hover {{
            color: #ffffff;
        }}

        .modal-qr-img {{
            width: 250px;
            height: 250px;
            background: #ffffff;
            padding: 14px;
            border-radius: var(--radius-md);
            margin: 16px auto;
            display: block;
        }}

        .modal-title {{
            font-size: 16px;
            font-weight: 700;
            color: #ffffff;
            margin-bottom: 6px;
        }}

        .modal-url {{
            font-size: 12px;
            color: var(--gold-primary);
            word-break: break-all;
            margin-bottom: 20px;
        }}

        @media (max-width: 768px) {{
            .header-inner {{
                flex-direction: column;
                align-items: stretch;
            }}
            .stats-summary {{
                justify-content: center;
            }}
            .hero h2 {{
                font-size: 24px;
            }}
            .products-grid {{
                grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
            }}
        }}
    </style>
</head>
<body>
    <header>
        <div class="header-inner">
            <div class="logo-group">
                <div class="logo-badge">VH</div>
                <div class="brand-text">
                    <h1>VIỆT HƯƠNG CERAMICS</h1>
                    <p>Thư Viện Mã QR Toàn Bộ Sản Phẩm Gạch & Thiết Bị Vệ Sinh</p>
                </div>
            </div>

            <div class="stats-summary">
                <div class="stats-item">
                    <span>Thể loại lớn:</span>
                    <strong>{len(hierarchy_summary)}</strong>
                </div>
                <div class="stats-divider"></div>
                <div class="stats-item">
                    <span>Tổng sản phẩm:</span>
                    <strong>{len(records)}</strong>
                </div>
                <div class="stats-divider"></div>
                <div class="stats-item">
                    <span>Mã QR:</span>
                    <strong style="color: var(--accent-green)">Đầy đủ 100%</strong>
                </div>
            </div>
        </div>
    </header>

    <section class="hero">
        <h2>Thư Viện Mã QR Sản Phẩm Việt Hương Ceramics</h2>
        <p>Hệ thống cào và phân loại <strong>{len(records)} sản phẩm</strong> từ <strong>https://viethuongceramics.com/san-pham/</strong>. Được tổ chức theo phân cấp 2 tầng chặt chẽ: <strong>Thể loại lớn &rarr; Thể loại nhỏ riêng biệt &rarr; Mã QR từng sản phẩm</strong>.</p>
    </section>

    <div class="controls-container">
        <div class="search-box">
            <svg class="search-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="11" cy="11" r="8"></circle>
                <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
            </svg>
            <input type="text" id="searchInput" class="search-input" placeholder="Tìm kiếm nhanh theo tên sản phẩm, mã gạch, kích thước, thiết bị..." autocomplete="off">
        </div>

        <!-- Tầng 1: Thể loại lớn -->
        <div class="filter-section">
            <div class="filter-label">1. Thể Loại Lớn (Danh Mục Cha):</div>
            <div class="nav-pills" id="parentNav">
                <button class="pill-btn active" data-parent="ALL">
                    <span>Tất cả thể loại</span>
                    <span class="pill-count">{len(records)}</span>
                </button>
            </div>
        </div>

        <!-- Tầng 2: Thể loại nhỏ riêng -->
        <div class="filter-section sub-nav-wrapper" id="subFilterSection">
            <div class="filter-label">2. Thể Loại Nhỏ Riêng (Danh Mục Con):</div>
            <div class="nav-pills" id="childNav">
                <button class="pill-btn active" data-child="ALL">
                    <span>Tất cả danh mục con</span>
                </button>
            </div>
        </div>
    </div>

    <main class="products-grid" id="productsGrid"></main>

    <!-- Modal Xem Chi Tiết -->
    <div class="modal" id="qrModal">
        <div class="modal-box">
            <button class="modal-close" id="modalClose">&times;</button>
            <div class="card-badges" style="margin-bottom: 8px;">
                <span class="card-category" id="modalParent">Thể loại</span>
                <span class="card-subcategory" id="modalChild">Loại nhỏ</span>
            </div>
            <h3 class="modal-title" id="modalTitle">Tên sản phẩm</h3>
            <img src="" alt="Mã QR" class="modal-qr-img" id="modalQrImg">
            <p class="modal-url" id="modalUrl"></p>
            <div style="display: flex; gap: 10px; justify-content: center;">
                <a href="" target="_blank" class="btn-link" id="modalWebLink">Mở trang web</a>
                <a href="" download="" class="btn-link btn-download" id="modalDownloadLink">Tải mã QR</a>
            </div>
        </div>
    </div>

    <script>
        const PRODUCTS = {products_json_str};
        const HIERARCHY = {hierarchy_json_str};

        let currentParent = 'ALL';
        let currentChild = 'ALL';
        let searchQuery = '';

        const grid = document.getElementById('productsGrid');
        const searchInput = document.getElementById('searchInput');
        const parentNav = document.getElementById('parentNav');
        const childNav = document.getElementById('childNav');

        // Modal elements
        const modal = document.getElementById('qrModal');
        const modalClose = document.getElementById('modalClose');
        const modalParent = document.getElementById('modalParent');
        const modalChild = document.getElementById('modalChild');
        const modalTitle = document.getElementById('modalTitle');
        const modalQrImg = document.getElementById('modalQrImg');
        const modalUrl = document.getElementById('modalUrl');
        const modalWebLink = document.getElementById('modalWebLink');
        const modalDownloadLink = document.getElementById('modalDownloadLink');

        // Render Parent Category Buttons
        for (const [parentName, info] of Object.entries(HIERARCHY)) {{
            const btn = document.createElement('button');
            btn.className = 'pill-btn';
            btn.dataset.parent = parentName;
            btn.innerHTML = `<span>${{parentName}}</span><span class="pill-count">${{info.count}}</span>`;
            btn.addEventListener('click', () => {{
                document.querySelectorAll('#parentNav .pill-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                currentParent = parentName;
                currentChild = 'ALL';
                renderChildNav();
                renderProducts();
            }});
            parentNav.appendChild(btn);
        }}

        // All Parent click
        document.querySelector('#parentNav .pill-btn[data-parent="ALL"]').addEventListener('click', (e) => {{
            document.querySelectorAll('#parentNav .pill-btn').forEach(b => b.classList.remove('active'));
            e.currentTarget.classList.add('active');
            currentParent = 'ALL';
            currentChild = 'ALL';
            renderChildNav();
            renderProducts();
        }});

        function renderChildNav() {{
            childNav.innerHTML = '';
            const allBtn = document.createElement('button');
            allBtn.className = 'pill-btn' + (currentChild === 'ALL' ? ' active' : '');
            allBtn.dataset.child = 'ALL';
            allBtn.innerHTML = `<span>Tất cả danh mục con</span>`;
            allBtn.addEventListener('click', () => {{
                document.querySelectorAll('#childNav .pill-btn').forEach(b => b.classList.remove('active'));
                allBtn.classList.add('active');
                currentChild = 'ALL';
                renderProducts();
            }});
            childNav.appendChild(allBtn);

            let subcats = {{}};
            if (currentParent === 'ALL') {{
                // aggregate all subcategories
                for (const p of Object.values(HIERARCHY)) {{
                    for (const [subName, count] of Object.entries(p.children)) {{
                        subcats[subName] = (subcats[subName] || 0) + count;
                    }}
                }}
            }} else if (HIERARCHY[currentParent]) {{
                subcats = HIERARCHY[currentParent].children;
            }}

            for (const [subName, count] of Object.entries(subcats)) {{
                const btn = document.createElement('button');
                btn.className = 'pill-btn' + (currentChild === subName ? ' active' : '');
                btn.dataset.child = subName;
                btn.innerHTML = `<span>${{subName}}</span><span class="pill-count">${{count}}</span>`;
                btn.addEventListener('click', () => {{
                    document.querySelectorAll('#childNav .pill-btn').forEach(b => b.classList.remove('active'));
                    btn.classList.add('active');
                    currentChild = subName;
                    renderProducts();
                }});
                childNav.appendChild(btn);
            }}
        }}

        // Search input
        searchInput.addEventListener('input', (e) => {{
            searchQuery = e.target.value.trim().toLowerCase();
            renderProducts();
        }});

        function renderProducts() {{
            const filtered = PRODUCTS.filter(p => {{
                const matchParent = (currentParent === 'ALL' || p.parent_cat === currentParent);
                const matchChild = (currentChild === 'ALL' || p.child_cat === currentChild);
                const matchSearch = (!searchQuery || 
                    p.name.toLowerCase().includes(searchQuery) || 
                    p.parent_cat.toLowerCase().includes(searchQuery) ||
                    p.child_cat.toLowerCase().includes(searchQuery)
                );
                return matchParent && matchChild && matchSearch;
            }});

            if (filtered.length === 0) {{
                grid.innerHTML = `
                    <div class="empty-state">
                        <h3>Không tìm thấy sản phẩm phù hợp</h3>
                        <p style="margin-top: 6px; font-size: 13px;">Hãy thử tìm kiếm từ khóa khác hoặc chuyển danh mục cha / con.</p>
                    </div>
                `;
                return;
            }}

            grid.innerHTML = filtered.map(p => `
                <div class="product-card">
                    <div class="card-badges">
                        <span class="card-category">${{p.parent_cat}}</span>
                        <span class="card-subcategory">${{p.child_cat}}</span>
                    </div>
                    <div class="qr-wrapper" onclick="openModal('${{encodeURIComponent(JSON.stringify(p))}}')">
                        <img src="${{encodeURI(p.qr_relative_path)}}" alt="${{p.name}}" class="qr-img" loading="lazy">
                    </div>
                    <div class="product-name" title="${{p.name}}">${{p.name}}</div>
                    <div class="card-actions">
                        <a href="${{p.url}}" target="_blank" rel="noopener noreferrer" class="btn-link">
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path>
                                <polyline points="15 3 21 3 21 9"></polyline>
                                <line x1="10" y1="14" x2="21" y2="3"></line>
                            </svg>
                            Xem Web
                        </a>
                        <a href="${{encodeURI(p.qr_relative_path)}}" download="${{p.name}}.png" class="btn-link btn-download">
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                                <polyline points="7 10 12 15 17 10"></polyline>
                                <line x1="12" y1="15" x2="12" y2="3"></line>
                            </svg>
                            Tải QR
                        </a>
                    </div>
                </div>
            `).join('');
        }}

        window.openModal = function(encodedData) {{
            const p = JSON.parse(decodeURIComponent(encodedData));
            modalParent.innerText = p.parent_cat;
            modalChild.innerText = p.child_cat;
            modalTitle.innerText = p.name;
            modalQrImg.src = encodeURI(p.qr_relative_path);
            modalUrl.innerText = p.url;
            modalWebLink.href = p.url;
            modalDownloadLink.href = encodeURI(p.qr_relative_path);
            modalDownloadLink.download = `${{p.name}}.png`;
            modal.classList.add('active');
        }};

        modalClose.addEventListener('click', () => {{
            modal.classList.remove('active');
        }});

        modal.addEventListener('click', (e) => {{
            if (e.target === modal) {{
                modal.classList.remove('active');
            }}
        }});

        document.addEventListener('keydown', (e) => {{
            if (e.key === 'Escape' && modal.classList.contains('active')) {{
                modal.classList.remove('active');
            }}
        }});

        renderChildNav();
        renderProducts();
    </script>
</body>
</html>
"""
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"-> Đã tạo dashboard giao diện tại: {html_path}")

def generate_readme(records, hierarchy_summary, project_dir):
    """Tạo file README chi tiết hướng dẫn và thống kê phân cấp."""
    readme_path = os.path.join(project_dir, "README.md")
    
    table_rows = []
    for parent_name, info in sorted(hierarchy_summary.items()):
        table_rows.append(f"### 📂 {parent_name} ({info['count']} sản phẩm)")
        table_rows.append("| STT | Thể Loại Con (Loại Nhỏ Riêng) | Số Lượng Sản Phẩm | Đường Dẫn Folder |")
        table_rows.append("| :---: | :--- | :---: | :--- |")
        for idx, (child_name, c_count) in enumerate(sorted(info['children'].items()), 1):
            table_rows.append(f"| {idx} | **{child_name}** | {c_count} mã QR | `Sản phẩm/{parent_name}/{child_name}/` |")
        table_rows.append("")

    table_content = "\n".join(table_rows)

    readme_content = f"""# Thư Viện Mã QR Toàn Bộ Sản Phẩm Việt Hương Ceramics (https://viethuongceramics.com/)

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

{table_content}

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
"""
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    print(f"-> Đã tạo tài liệu README tại: {readme_path}")

def main():
    cat_dict = fetch_categories()
    products = fetch_all_products()
    if not products:
        print("Lỗi: Không lấy được sản phẩm từ website viethuongceramics.com!")
        sys.exit(1)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    records = []
    hierarchy_summary = {}

    print("\n-> Bắt đầu xử lý phân cấp và tạo mã QR...")

    total_qr_files = 0
    seen_filenames = set()

    for idx, p in enumerate(products, 1):
        p_name = sanitize_filename(p['name'])
        p_url = p['permalink']
        p_slug = p.get('slug', '')
        p_id = p.get('id', '')
        img_url = p['images'][0]['src'] if p.get('images') and len(p['images']) > 0 else ""

        cats = p.get('categories', [])
        c_ids = [c['id'] for c in cats]

        # Kiểm tra Eurovinto / Star
        is_eurovinto = any(c['slug'] == 'thiet-bi-ve-sinh-eurovinto' for c in cats)
        is_star = any(c['slug'] == 'thiet-bi-ve-sinh-star-thai-lan-da-nang' for c in cats)

        child_cats = [cat_dict[cid] for cid in c_ids if cid in cat_dict and cat_dict[cid]['parent'] != 0]

        assigned_folders = set()

        # 1. Các nhánh cha - con chuẩn
        for cc in child_cats:
            p_id_cat = cc['parent']
            p_info = cat_dict.get(p_id_cat)
            if p_info:
                assigned_folders.add((p_info['name'], cc['name']))

        # 2. Nhánh Thiết Bị Vệ Sinh Eurovinto
        if is_eurovinto:
            euro_sub = [cc['name'] for cc in child_cats if cc['parent'] == 641]
            if euro_sub:
                for es in euro_sub:
                    assigned_folders.add(('Thiết Bị Vệ Sinh Eurovinto', es))
            else:
                assigned_folders.add(('Thiết Bị Vệ Sinh Eurovinto', 'Khác'))

        # 3. Nhánh Thiết Bị Vệ Sinh Star Thái Lan
        if is_star:
            star_sub = [cc['name'] for cc in child_cats if cc['parent'] == 641]
            if star_sub:
                for ss in star_sub:
                    assigned_folders.add(('Thiết Bị Vệ Sinh Star Thái Lan', ss))
            else:
                assigned_folders.add(('Thiết Bị Vệ Sinh Star Thái Lan', 'Khác'))

        # Fallback nếu không khớp nhánh con
        if not assigned_folders:
            root_names = [cat_dict[cid]['name'] for cid in c_ids if cid in cat_dict and cat_dict[cid]['parent'] == 0]
            for rn in root_names:
                assigned_folders.add((rn, 'Khác'))

        # Lấy ảnh QR
        qr_img = get_or_create_qr_image(p_url)

        # Lưu ảnh QR vào từng folder tương ứng
        for parent_name, child_name in assigned_folders:
            subfolder = os.path.join(OUTPUT_DIR, parent_name, child_name)
            os.makedirs(subfolder, exist_ok=True)

            # Tên file ảnh
            file_key = (parent_name, child_name, p_name)
            if file_key in seen_filenames:
                qr_filename = f"{p_name} - {p_slug}.png"
            else:
                qr_filename = f"{p_name}.png"
            seen_filenames.add(file_key)

            qr_filepath = os.path.join(subfolder, qr_filename)
            qr_img.save(qr_filepath, "PNG")
            total_qr_files += 1

            # Thống kê
            if parent_name not in hierarchy_summary:
                hierarchy_summary[parent_name] = {'count': 0, 'children': {}}
            hierarchy_summary[parent_name]['children'][child_name] = hierarchy_summary[parent_name]['children'].get(child_name, 0) + 1

            rel_path = os.path.relpath(qr_filepath, PROJECT_DIR)

            records.append({
                "stt": idx,
                "id": p_id,
                "parent_cat": parent_name,
                "child_cat": child_name,
                "name": p_name,
                "slug": p_slug,
                "url": p_url,
                "qr_relative_path": rel_path,
                "image_url": img_url
            })

        if idx % 100 == 0 or idx == len(products):
            print(f"   [{idx}/{len(products)}] Đang tạo mã QR cho sản phẩm: {p_name[:35]}...")

    # Cập nhật tổng count cho mỗi parent
    for parent_name in hierarchy_summary:
        hierarchy_summary[parent_name]['count'] = sum(hierarchy_summary[parent_name]['children'].values())

    # Lưu file JSON
    json_path = os.path.join(PROJECT_DIR, "danh_sach_san_pham.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(records, f, ensure_ascii=False, indent=2)
    print(f"\n-> Đã lưu dữ liệu JSON vào: {json_path}")

    # Lưu file CSV
    csv_path = os.path.join(PROJECT_DIR, "danh_sach_san_pham.csv")
    with open(csv_path, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["STT", "ID", "Thể loại lớn", "Thể loại nhỏ riêng", "Tên sản phẩm", "Đường dẫn Website", "Đường dẫn File QR", "Ảnh"])
        for r in records:
            writer.writerow([r["stt"], r["id"], r["parent_cat"], r["child_cat"], r["name"], r["url"], r["qr_relative_path"], r["image_url"]])
    print(f"-> Đã lưu bảng thống kê CSV vào: {csv_path}")

    # Tạo giao diện dashboard HTML
    generate_html_viewer(records, hierarchy_summary, PROJECT_DIR)

    # Tạo tài liệu README
    generate_readme(records, hierarchy_summary, PROJECT_DIR)

    # Tạo liên kết tượng trưng (symlink) tại thư mục cha nếu khả thi
    try:
        parent_tool_dir = os.path.dirname(SCRIPT_DIR)
        parent_symlink = os.path.join(parent_tool_dir, "QRcodeviethuongceramics")
        if not os.path.exists(parent_symlink):
            os.symlink(PROJECT_DIR, parent_symlink)
            print(f"-> Đã tạo lối tắt truy cập nhanh tại: {parent_symlink}")
    except Exception as e:
        pass

    print("\n" + "="*60)
    print("HOÀN THÀNH TẠO MÃ QR VÀ CẤU TRÚC PHÂN CẤP CHO VIỆT HƯƠNG CERAMICS:")
    print("="*60)
    for parent_name, info in sorted(hierarchy_summary.items()):
        print(f"📁 {parent_name}/ (Tổng: {info['count']} mã QR)")
        for child_name, c_count in sorted(info['children'].items()):
            print(f"   └── 📂 {child_name}/: {c_count} mã QR")
    print("-" * 60)
    print(f"Tổng số file mã QR đã tạo: {total_qr_files}")
    print(f"Thư mục lưu trữ chính: {PROJECT_DIR}")
    print("="*60)

if __name__ == "__main__":
    main()
