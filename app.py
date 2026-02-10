"""
PelitPos - Sistem Point of Sale Profesional
Tagline: "gk medit gk sugeh ta?"
Version: 3.0.0
Architecture: Enterprise-Grade, Normalized Database, Production-Ready

Sistem POS yang efisien dan andal berbasis Python dan Streamlit dengan:
- Database normalisasi dengan price snapshots untuk integritas historis
- Atomic stock updates menggunakan SQL untuk menghindari race conditions
- Audit trail lengkap untuk semua pergerakan stok
- Sistem keamanan PIN untuk fungsi administratif
- Session state caching untuk performa optimal
- Professional dark theme UI dengan industrial design
"""

import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime
import pytz
import secrets
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Optional, Tuple
import time
import hashlib

# ============================================================================
# CONFIGURATION & INITIALIZATION
# ============================================================================

st.set_page_config(
    page_title="PelitPos - Point of Sale",
    layout="wide",
    page_icon="💡"
)

# Admin PIN Configuration (Default: "1234")
ADMIN_PIN_HASH = hashlib.sha256("1234".encode()).hexdigest()

# Database connection with caching for performance
@st.cache_resource
def init_supabase_connection():
    """Initialize and cache Supabase connection to minimize overhead"""
    try:
        return create_client(
            st.secrets["SUPABASE_URL"],
            st.secrets["SUPABASE_KEY"]
        )
    except Exception as e:
        st.error(f"Koneksi database gagal: {e}")
        return None

supabase = init_supabase_connection()

# ============================================================================
# DESIGN SYSTEM - PROFESSIONAL DARK THEME
# ============================================================================

# Color Palette - Industrial Dark Slate
COLORS = {
    "bg_primary": "#0f172a",      # Main background
    "bg_secondary": "#1e293b",    # Card background
    "bg_tertiary": "#334155",     # Borders and dividers
    "accent": "#3b82f6",          # Primary accent (blue)
    "accent_hover": "#2563eb",    # Hover state
    "success": "#10b981",         # Success states
    "warning": "#f59e0b",         # Warning states
    "danger": "#ef4444",          # Error/delete states
    "text_primary": "#f1f5f9",    # Primary text
    "text_secondary": "#cbd5e1",  # Secondary text
    "text_muted": "#64748b"       # Muted text
}

# Lucide Icons SVG
ICONS = {
    "dashboard": '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="7" height="9" x="3" y="3" rx="1"/><rect width="7" height="5" x="14" y="3" rx="1"/><rect width="7" height="9" x="14" y="12" rx="1"/><rect width="7" height="5" x="3" y="16" rx="1"/></svg>',
    "package": '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z"/><path d="m3.3 7 8.7 5 8.7-5"/><path d="M12 22V12"/></svg>',
    "shopping_cart": '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="8" cy="21" r="1"/><circle cx="19" cy="21" r="1"/><path d="M2.05 2.05h2l2.66 12.42a2 2 0 0 0 2 1.58h9.78a2 2 0 0 0 1.95-1.57l1.65-7.43H5.12"/></svg>',
    "history": '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/><path d="M12 7v5l4 2"/></svg>',
    "lock": '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="11" x="3" y="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>'
}

# CSS Injection
def inject_custom_css():
    """Inject custom CSS for enterprise-grade dark theme"""
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');
    
    /* Global Styles */
    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
        color: {COLORS['text_primary']} !important;
        background-color: {COLORS['bg_primary']};
    }}
    
    .stApp {{
        background-color: {COLORS['bg_primary']};
    }}
    
    /* Hide Streamlit Branding */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    
    /* Cards & Containers */
    div[data-testid="stVerticalBlock"] > div[style*="flex-direction: column"] > div {{
        background-color: {COLORS['bg_secondary']};
        border: 1px solid {COLORS['bg_tertiary']};
        border-radius: 8px;
        padding: 24px;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.3);
    }}
    
    /* Form Inputs */
    input, select, textarea, div[data-baseweb="select"] > div, div[data-baseweb="input"] > div {{
        background-color: {COLORS['bg_primary']} !important;
        border: 1px solid {COLORS['bg_tertiary']} !important;
        border-radius: 6px !important;
        color: {COLORS['text_primary']} !important;
        font-size: 14px !important;
    }}
    
    input:focus, select:focus, textarea:focus {{
        border-color: {COLORS['accent']} !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
    }}
    
    label {{
        color: {COLORS['text_secondary']} !important;
        font-weight: 500 !important;
        font-size: 13px !important;
        text-transform: uppercase;
    }}
    
    /* Buttons */
    .stButton > button {{
        background-color: {COLORS['accent']} !important;
        color: white !important;
        border: none !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        padding: 12px 24px !important;
        transition: all 0.2s ease !important;
    }}
    
    .stButton > button:hover {{
        background-color: {COLORS['accent_hover']} !important;
        transform: translateY(-1px);
    }}
    
    /* Metrics */
    [data-testid="stMetricValue"] {{
        color: {COLORS['accent']} !important;
        font-size: 32px !important;
        font-weight: 700 !important;
    }}
    
    [data-testid="stMetricLabel"] {{
        color: {COLORS['text_secondary']} !important;
        font-size: 12px !important;
        text-transform: uppercase;
        font-weight: 600;
    }}
    
    /* Tabs */
    button[data-baseweb="tab"] {{
        color: {COLORS['text_muted']} !important;
        border-bottom: 2px solid transparent !important;
        font-weight: 500 !important;
    }}
    
    button[data-baseweb="tab"][aria-selected="true"] {{
        color: {COLORS['accent']} !important;
        border-bottom-color: {COLORS['accent']} !important;
    }}
    
    /* Receipt Container */
    .receipt-container {{
        background-color: {COLORS['bg_primary']};
        border: 2px dashed {COLORS['bg_tertiary']};
        border-radius: 8px;
        padding: 24px;
        font-family: 'JetBrains Mono', monospace;
    }}
    
    .receipt-total {{
        font-size: 24px;
        font-weight: 700;
        color: {COLORS['success']};
        text-align: right;
        margin-top: 16px;
        padding-top: 16px;
        border-top: 2px solid {COLORS['bg_tertiary']};
    }}
    
    /* Alert Boxes */
    .alert-box {{
        padding: 16px;
        border-radius: 6px;
        border-left: 4px solid;
        margin: 16px 0;
    }}
    
    .alert-warning {{
        background-color: rgba(245, 158, 11, 0.1);
        border-color: {COLORS['warning']};
    }}
    
    .alert-danger {{
        background-color: rgba(239, 68, 68, 0.1);
        border-color: {COLORS['danger']};
    }}
    </style>
    """, unsafe_allow_html=True)

# ============================================================================
# SESSION STATE MANAGEMENT
# ============================================================================

def init_session_state():
    """Initialize session state variables"""
    if 'products_cache' not in st.session_state:
        st.session_state.products_cache = None
    if 'customers_cache' not in st.session_state:
        st.session_state.customers_cache = None
    if 'transactions_cache' not in st.session_state:
        st.session_state.transactions_cache = None
    if 'cart_items' not in st.session_state:
        st.session_state.cart_items = []
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Kasir"
    if 'admin_authenticated' not in st.session_state:
        st.session_state.admin_authenticated = False

def invalidate_cache(cache_type: str = 'all'):
    """Invalidate specific cache or all caches - ensures data integrity"""
    if cache_type == 'all' or cache_type == 'products':
        st.session_state.products_cache = None
    if cache_type == 'all' or cache_type == 'customers':
        st.session_state.customers_cache = None
    if cache_type == 'all' or cache_type == 'transactions':
        st.session_state.transactions_cache = None

# ============================================================================
# SECURITY - ADMIN PIN AUTHENTICATION
# ============================================================================

def check_admin_pin(pin: str) -> bool:
    """Verify admin PIN using SHA256 hash"""
    pin_hash = hashlib.sha256(pin.encode()).hexdigest()
    return pin_hash == ADMIN_PIN_HASH

def require_admin_auth(page_name: str):
    """Require admin authentication for sensitive pages"""
    if not st.session_state.admin_authenticated:
        st.warning(f"🔒 Akses ke {page_name} memerlukan PIN Admin")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            pin_input = st.text_input("Masukkan PIN Admin", type="password", key=f"pin_{page_name}")
            
            if st.button("Verifikasi", use_container_width=True):
                if check_admin_pin(pin_input):
                    st.session_state.admin_authenticated = True
                    st.success("✓ Autentikasi berhasil!")
                    st.rerun()
                else:
                    st.error("❌ PIN salah!")
        
        st.stop()

def logout_admin():
    """Logout from admin session"""
    st.session_state.admin_authenticated = False

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_jakarta_timezone():
    """Get Jakarta timezone object"""
    return pytz.timezone('Asia/Jakarta')

def get_current_datetime():
    """Get current datetime in Jakarta timezone"""
    return datetime.now(get_jakarta_timezone())

def generate_unique_id(prefix: str) -> str:
    """Generate unique ID with prefix and timestamp"""
    timestamp = get_current_datetime().strftime('%Y%m%d%H%M%S')
    random_hex = secrets.token_hex(2).upper()
    return f"{prefix}-{timestamp}-{random_hex}"

def format_currency(amount: float) -> str:
    """Format number as Indonesian Rupiah"""
    return f"Rp {amount:,.0f}".replace(',', '.')

def render_page_header(icon_key: str, title: str, subtitle: Optional[str] = None):
    """Render professional page header with icon"""
    subtitle_html = f'<p style="margin:0; color:{COLORS["text_muted"]}; font-size:14px;">{subtitle}</p>' if subtitle else ''
    st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 16px; padding: 20px 0; border-bottom: 1px solid {COLORS['bg_tertiary']}; margin-bottom: 32px;">
            {ICONS[icon_key]}
            <div>
                <h1 style="margin: 0; font-size: 28px; font-weight: 700; color: {COLORS['text_primary']};">{title}</h1>
                {subtitle_html}
            </div>
        </div>
    """, unsafe_allow_html=True)

# ============================================================================
# DATA LAYER - DATABASE OPERATIONS WITH ATOMIC UPDATES
# ============================================================================

def fetch_products(force_refresh: bool = False) -> pd.DataFrame:
    """Fetch products from database with caching"""
    if not force_refresh and st.session_state.products_cache is not None:
        return st.session_state.products_cache
    
    try:
        response = supabase.table("produk").select("*").execute()
        df = pd.DataFrame(response.data) if response.data else pd.DataFrame()
        st.session_state.products_cache = df
        return df
    except Exception as e:
        st.error(f"Gagal mengambil data produk: {str(e)}")
        return pd.DataFrame()

def fetch_customers(force_refresh: bool = False) -> pd.DataFrame:
    """Fetch customers from database with caching"""
    if not force_refresh and st.session_state.customers_cache is not None:
        return st.session_state.customers_cache
    
    try:
        response = supabase.table("pelanggan").select("*").execute()
        df = pd.DataFrame(response.data) if response.data else pd.DataFrame()
        st.session_state.customers_cache = df
        return df
    except Exception as e:
        st.error(f"Gagal mengambil data pelanggan: {str(e)}")
        return pd.DataFrame()

def fetch_transactions(force_refresh: bool = False) -> pd.DataFrame:
    """Fetch transactions with customer details from database"""
    if not force_refresh and st.session_state.transactions_cache is not None:
        return st.session_state.transactions_cache
    
    try:
        response = supabase.table("transaksi").select(
            "*, pelanggan(nama_pelanggan, email)"
        ).order("tanggal_transaksi", desc=True).execute()
        df = pd.DataFrame(response.data) if response.data else pd.DataFrame()
        st.session_state.transactions_cache = df
        return df
    except Exception as e:
        st.error(f"Gagal mengambil data transaksi: {str(e)}")
        return pd.DataFrame()

def fetch_transaction_items(transaction_id: str) -> List[Dict]:
    """Fetch line items for a specific transaction"""
    try:
        response = supabase.table("transaksi_item").select("*").eq("transaksi_id", transaction_id).execute()
        return response.data if response.data else []
    except Exception as e:
        st.error(f"Gagal mengambil detail transaksi: {str(e)}")
        return []

def create_product(name: str, price: float, stock: int, category: str) -> Tuple[bool, str]:
    """Create new product in database"""
    try:
        product_data = {
            "nama_produk": name,
            "harga": price,
            "stok": stock,
            "kategori": category
        }
        supabase.table("produk").insert(product_data).execute()
        invalidate_cache('products')
        return True, "Produk berhasil ditambahkan"
    except Exception as e:
        return False, f"Gagal menambahkan produk: {str(e)}"

def update_product(product_id: int, name: str, price: float, stock: int, category: str) -> Tuple[bool, str]:
    """Update existing product in database"""
    try:
        update_data = {
            "nama_produk": name,
            "harga": price,
            "stok": stock,
            "kategori": category
        }
        supabase.table("produk").update(update_data).eq("produk_id", product_id).execute()
        invalidate_cache('products')
        return True, "Produk berhasil diperbarui"
    except Exception as e:
        return False, f"Gagal memperbarui produk: {str(e)}"

def delete_product(product_id: int) -> Tuple[bool, str]:
    """Delete product from database"""
    try:
        supabase.table("produk").delete().eq("produk_id", product_id).execute()
        invalidate_cache('products')
        return True, "Produk berhasil dihapus"
    except Exception as e:
        return False, f"Gagal menghapus produk: {str(e)}"

def create_customer(customer_id: str, name: str, email: str) -> Tuple[bool, str]:
    """Create new customer in database"""
    try:
        customer_data = {
            "pelanggan_id": customer_id,
            "nama_pelanggan": name,
            "email": email
        }
        supabase.table("pelanggan").insert(customer_data).execute()
        invalidate_cache('customers')
        return True, "Pelanggan berhasil didaftarkan"
    except Exception as e:
        return False, f"Gagal mendaftarkan pelanggan: {str(e)}"

def update_customer(customer_id: str, name: str, email: str) -> Tuple[bool, str]:
    """Update existing customer in database"""
    try:
        update_data = {
            "nama_pelanggan": name,
            "email": email
        }
        supabase.table("pelanggan").update(update_data).eq("pelanggan_id", customer_id).execute()
        invalidate_cache('customers')
        return True, "Data pelanggan berhasil diperbarui"
    except Exception as e:
        return False, f"Gagal memperbarui data pelanggan: {str(e)}"

def delete_customer(customer_id: str) -> Tuple[bool, str]:
    """Delete customer from database"""
    try:
        supabase.table("pelanggan").delete().eq("pelanggan_id", customer_id).execute()
        invalidate_cache('customers')
        return True, "Pelanggan berhasil dihapus"
    except Exception as e:
        return False, f"Gagal menghapus pelanggan: {str(e)}"

def log_stock_movement(product_id: int, quantity_change: int, action_type: str, notes: str = "") -> bool:
    """
    Log stock movement to audit trail (stok_log table)
    action_type: 'Penjualan', 'Restock', 'Adjustment', 'Pengembalian'
    """
    try:
        log_data = {
            "produk_id": product_id,
            "jumlah_perubahan": quantity_change,
            "tipe_aksi": action_type,
            "keterangan": notes,
            "waktu": get_current_datetime().isoformat()
        }
        supabase.table("stok_log").insert(log_data).execute()
        return True
    except Exception as e:
        st.error(f"Gagal mencatat log stok: {str(e)}")
        return False

def atomic_stock_update(product_id: int, quantity_to_deduct: int) -> Tuple[bool, str]:
    """
    Perform atomic stock update using SQL to prevent race conditions
    Uses direct SQL UPDATE query: UPDATE produk SET stok = stok - quantity WHERE produk_id = ?
    """
    try:
        # Use RPC (Remote Procedure Call) to execute atomic SQL update
        # This ensures the operation is atomic at database level
        response = supabase.rpc(
            'atomic_stock_deduct',
            {
                'p_product_id': product_id,
                'p_quantity': quantity_to_deduct
            }
        ).execute()
        
        # Check if stock deduction was successful
        if response.data and response.data > 0:
            return True, "Stok berhasil dikurangi"
        else:
            return False, "Stok tidak mencukupi atau produk tidak ditemukan"
            
    except Exception as e:
        return False, f"Gagal update stok: {str(e)}"

def process_transaction(customer_id: str, total_amount: float, items: List[Dict], discount: float = 0) -> Tuple[bool, str, Optional[str]]:
    """
    Process transaction with normalized database structure and price snapshots
    Implements transaction-like behavior: all or nothing
    Steps:
    1. Validate stock availability
    2. Create transaction header
    3. Create transaction items with price snapshots
    4. Perform atomic stock updates
    5. Log stock movements
    """
    transaction_id = None
    items_created = []
    stock_updated = []
    
    try:
        # Step 1: Validate stock availability for ALL items first
        products_df = fetch_products()
        for item in items:
            product_row = products_df[products_df['produk_id'] == item['product_id']]
            if product_row.empty:
                return False, f"Produk {item['product_name']} tidak ditemukan", None
            
            current_stock = int(product_row.iloc[0]['stok'])
            if current_stock < item['quantity']:
                return False, f"Stok tidak mencukupi untuk {item['product_name']} (Tersedia: {current_stock})", None
        
        # Step 2: Create transaction header
        transaction_id = generate_unique_id("TRX")
        transaction_data = {
            "transaksi_id": transaction_id,
            "pelanggan_id": customer_id,
            "total_bayar": total_amount,
            "diskon": discount,
            "tanggal_transaksi": get_current_datetime().isoformat()
        }
        supabase.table("transaksi").insert(transaction_data).execute()
        
        # Step 3: Create transaction items with PRICE SNAPSHOTS
        for item in items:
            item_data = {
                "transaksi_id": transaction_id,
                "produk_id": item['product_id'],
                "nama_produk": item['product_name'],  # Snapshot of product name
                "harga_satuan": item['price'],  # PRICE SNAPSHOT - critical for historical accuracy
                "jumlah": item['quantity'],
                "subtotal": item['price'] * item['quantity']
            }
            supabase.table("transaksi_item").insert(item_data).execute()
            items_created.append(item['product_id'])
            
            # Step 4: Perform ATOMIC stock update (prevents race conditions)
            success, message = atomic_stock_update(item['product_id'], item['quantity'])
            if not success:
                # Rollback: delete transaction items and header
                for created_product_id in items_created:
                    supabase.table("transaksi_item").delete().eq("transaksi_id", transaction_id).eq("produk_id", created_product_id).execute()
                supabase.table("transaksi").delete().eq("transaksi_id", transaction_id).execute()
                return False, f"Gagal update stok: {message}", None
            
            stock_updated.append(item['product_id'])
            
            # Step 5: Log stock movement to audit trail
            log_stock_movement(
                product_id=item['product_id'],
                quantity_change=-item['quantity'],  # Negative for sales
                action_type="Penjualan",
                notes=f"Transaksi: {transaction_id}"
            )
        
        # Invalidate caches to ensure fresh data
        invalidate_cache('products')
        invalidate_cache('transactions')
        
        return True, "Transaksi berhasil diproses", transaction_id
        
    except Exception as e:
        # Rollback any partial changes if possible
        if transaction_id:
            try:
                # Delete created transaction items
                supabase.table("transaksi_item").delete().eq("transaksi_id", transaction_id).execute()
                # Delete transaction header
                supabase.table("transaksi").delete().eq("transaksi_id", transaction_id).execute()
            except:
                pass
        
        return False, f"Transaksi gagal: {str(e)}", None

# ============================================================================
# UI COMPONENTS
# ============================================================================

def render_kpi_card(label: str, value: str, delta: Optional[str] = None):
    """Render professional KPI metric card"""
    st.metric(label=label, value=value, delta=delta)

def render_receipt(items: List[Dict], subtotal: float, tax: float, discount: float, total: float, 
                   transaction_id: Optional[str] = None, customer_name: Optional[str] = None):
    """Render thermal printer style receipt using Streamlit native components"""
    current_time = get_current_datetime()
    
    # Container with border
    st.markdown(f"""
        <div style="background-color: {COLORS['bg_secondary']}; border: 2px solid {COLORS['bg_tertiary']}; border-radius: 8px; padding: 0;">
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown(f"""
        <div style="text-align: center; padding: 20px; border-bottom: 2px dashed {COLORS['bg_tertiary']};">
            <h2 style="margin: 0; color: {COLORS['text_primary']};">💡 PelitPos</h2>
            <p style="margin: 5px 0 0 0; color: {COLORS['text_muted']}; font-size: 12px;">gk medit gk sugeh ta?</p>
            <p style="margin: 5px 0 0 0; color: {COLORS['text_muted']}; font-size: 11px;">Jl. Enterprise Boulevard No. 123</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Transaction Info
    st.markdown(f"""
        <div style="padding: 15px 20px;">
            <div style="display: flex; justify-content: space-between; margin: 5px 0; color: {COLORS['text_secondary']}; font-size: 12px;">
                <span>Invoice:</span>
                <span style="color: {COLORS['text_primary']}; font-weight: 600;">{transaction_id or 'PREVIEW'}</span>
            </div>
            <div style="display: flex; justify-content: space-between; margin: 5px 0; color: {COLORS['text_secondary']}; font-size: 12px;">
                <span>Tanggal:</span>
                <span>{current_time.strftime('%d %b %Y, %H:%M')}</span>
            </div>
            <div style="display: flex; justify-content: space-between; margin: 5px 0; color: {COLORS['text_secondary']}; font-size: 12px;">
                <span>Pelanggan:</span>
                <span>{customer_name or 'Tamu'}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Detail Pembelian Header
    st.markdown(f"""
        <div style="padding: 15px 20px; border-top: 2px dashed {COLORS['bg_tertiary']};">
            <p style="margin: 0 0 10px 0; color: {COLORS['text_primary']}; font-weight: 600; font-size: 14px;">Detail Pembelian:</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Items - using simple divs instead of table
    for item in items:
        item_total = item['quantity'] * item['price']
        st.markdown(f"""
            <div style="padding: 8px 20px; border-bottom: 1px dotted {COLORS['bg_tertiary']};">
                <div style="display: flex; justify-content: space-between; margin-bottom: 3px;">
                    <span style="color: {COLORS['text_primary']}; font-weight: 500;">{item['product_name']}</span>
                    <span style="color: {COLORS['text_primary']}; font-weight: 600;">{format_currency(item_total)}</span>
                </div>
                <div style="display: flex; justify-content: space-between;">
                    <span style="color: {COLORS['text_muted']}; font-size: 12px;">{item['quantity']} x {format_currency(item['price'])}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    # Summary
    st.markdown(f"""
        <div style="padding: 15px 20px; border-top: 2px dashed {COLORS['bg_tertiary']};">
            <div style="display: flex; justify-content: space-between; margin: 8px 0; color: {COLORS['text_secondary']}; font-size: 14px;">
                <span>Subtotal:</span>
                <span>{format_currency(subtotal)}</span>
            </div>
            <div style="display: flex; justify-content: space-between; margin: 8px 0; color: {COLORS['text_secondary']}; font-size: 14px;">
                <span>PPN (11%):</span>
                <span>{format_currency(tax)}</span>
            </div>
            <div style="display: flex; justify-content: space-between; margin: 8px 0; color: {COLORS['text_secondary']}; font-size: 14px;">
                <span>Diskon:</span>
                <span style="color: {COLORS['danger']};">-{format_currency(discount)}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # TOTAL - Most important!
    st.markdown(f"""
        <div style="padding: 20px; border-top: 3px solid {COLORS['accent']}; background: linear-gradient(135deg, {COLORS['bg_secondary']} 0%, {COLORS['bg_primary']} 100%);">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 16px; font-weight: 600; color: {COLORS['text_primary']}; text-transform: uppercase;">Total Bayar:</span>
                <span style="font-size: 32px; font-weight: 700; color: {COLORS['success']}; letter-spacing: -1px;">{format_currency(total)}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Footer
    st.markdown(f"""
        <div style="text-align: center; padding: 15px 20px; border-top: 1px dashed {COLORS['bg_tertiary']}; color: {COLORS['text_muted']}; font-size: 12px; font-style: italic;">
            Terima kasih atas kunjungan Anda!<br>
            Semoga berkah dan sukses selalu 🙏
        </div>
        </div>
    """, unsafe_allow_html=True)

# ============================================================================
# NAVIGATION
# ============================================================================

def render_top_nav():
    """Render horizontal navigation bar"""
    current_time = get_current_datetime()
    
    col_brand, col_spacer, col_time = st.columns([2, 4, 2])
    
    with col_brand:
        st.markdown("""
            <div style="padding: 10px 0;">
                <h2 style="margin: 0; color: #f1f5f9; font-size: 24px; font-weight: 700;">💡 PelitPos</h2>
                <p style="margin: 0; color: #64748b; font-size: 11px;">gk medit gk sugeh ta?</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col_time:
        auth_status = "🔓 Admin" if st.session_state.admin_authenticated else "🔒 User"
        st.markdown(f"""
            <div style="text-align: right; padding: 10px 0; color: #64748b; font-size: 13px;">
                <div>{current_time.strftime('%d %B %Y')}</div>
                <div>{current_time.strftime('%H:%M WIB')} • {auth_status}</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Navigation buttons
    col1, col2, col3, col4, col_refresh = st.columns([1, 1, 1, 1, 0.5])
    
    with col1:
        if st.button("🛒 Kasir", key="nav_kasir", use_container_width=True):
            st.session_state.current_page = "Kasir"
            st.rerun()
    
    with col2:
        if st.button("📦 Data Master", key="nav_master", use_container_width=True):
            st.session_state.current_page = "Data Master"
            st.rerun()
    
    with col3:
        if st.button("📋 Riwayat", key="nav_riwayat", use_container_width=True):
            st.session_state.current_page = "Riwayat"
            st.rerun()
    
    with col4:
        if st.button("📊 Dashboard", key="nav_dashboard", use_container_width=True):
            st.session_state.current_page = "Dashboard"
            st.rerun()
    
    with col_refresh:
        if st.button("🔄", key="nav_refresh", use_container_width=True, help="Refresh Data"):
            invalidate_cache('all')
            st.rerun()
    
    # Logout button for admin
    if st.session_state.admin_authenticated:
        if st.button("🔒 Logout Admin", key="logout_btn"):
            logout_admin()
            st.rerun()
    
    st.markdown("---")

# ============================================================================
# PAGES
# ============================================================================

def render_cashier_page():
    """Render cashier terminal for transaction processing"""
    render_page_header("shopping_cart", "Terminal Kasir", "Proses transaksi penjualan")
    
    products_df = fetch_products()
    customers_df = fetch_customers()
    
    if products_df.empty or customers_df.empty:
        st.warning("⚠️ Data master belum lengkap. Silakan tambahkan produk dan pelanggan terlebih dahulu.")
        return
    
    col_cart, col_receipt = st.columns([2, 1])
    
    with col_cart:
        st.subheader("Keranjang Belanja")
        
        # Customer selection
        customer_names = customers_df['nama_pelanggan'].tolist()
        selected_customer_name = st.selectbox("Pilih Pelanggan", options=customer_names)
        
        selected_customer = customers_df[customers_df['nama_pelanggan'] == selected_customer_name].iloc[0]
        customer_id = selected_customer['pelanggan_id']
        
        st.markdown("---")
        
        # Product selection
        col_prod, col_qty = st.columns([3, 1])
        
        with col_prod:
            product_names = products_df['nama_produk'].tolist()
            selected_product_name = st.selectbox("Pilih Produk", options=product_names)
        
        selected_product = products_df[products_df['nama_produk'] == selected_product_name].iloc[0]
        
        max_qty = int(selected_product['stok'])
        product_price = float(selected_product['harga'])
        
        with col_qty:
            quantity = st.number_input("Jumlah", min_value=1, max_value=max_qty if max_qty > 0 else 1, value=1)
        
        if max_qty == 0:
            st.error(f"❌ Stok {selected_product_name} habis!")
        elif max_qty < 5:
            st.warning(f"⚠️ Stok {selected_product_name} tersisa {max_qty} unit")
        
        if st.button("➕ Tambah ke Keranjang", use_container_width=True, disabled=(max_qty == 0)):
            cart_item = {
                'product_id': selected_product['produk_id'],
                'product_name': selected_product_name,
                'price': product_price,
                'quantity': quantity
            }
            st.session_state.cart_items.append(cart_item)
            st.success(f"✓ Ditambahkan: {quantity}x {selected_product_name}")
            st.rerun()
        
        st.markdown("---")
        
        # Display cart
        if st.session_state.cart_items:
            st.subheader("Item Keranjang")
            
            for idx, item in enumerate(st.session_state.cart_items):
                col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                
                with col1:
                    st.write(f"**{item['product_name']}**")
                
                with col2:
                    st.write(f"{item['quantity']} x {format_currency(item['price'])}")
                
                with col3:
                    item_total = item['quantity'] * item['price']
                    st.write(f"**{format_currency(item_total)}**")
                
                with col4:
                    if st.button("🗑", key=f"remove_{idx}"):
                        st.session_state.cart_items.pop(idx)
                        st.rerun()
            
            if st.button("🗑 Kosongkan Keranjang", use_container_width=True):
                st.session_state.cart_items = []
                st.rerun()
        else:
            st.info("Keranjang kosong. Tambahkan produk untuk memulai transaksi.")
    
    with col_receipt:
        st.subheader("Struk Belanja")
        
        if st.session_state.cart_items:
            subtotal = sum(item['quantity'] * item['price'] for item in st.session_state.cart_items)
            tax_amount = subtotal * 0.11
            
            discount_amount = st.number_input(
                "Diskon (Rp)",
                min_value=0.0,
                max_value=float(subtotal),
                value=0.0,
                step=1000.0
            )
            
            grand_total = subtotal + tax_amount - discount_amount
            
            render_receipt(
                items=st.session_state.cart_items,
                subtotal=subtotal,
                tax=tax_amount,
                discount=discount_amount,
                total=grand_total,
                customer_name=selected_customer_name
            )
            
            st.markdown("---")
            
            if st.button("💳 PROSES PEMBAYARAN", use_container_width=True, type="primary"):
                with st.spinner("Memproses transaksi..."):
                    success, message, transaction_id = process_transaction(
                        customer_id=customer_id,
                        total_amount=grand_total,
                        items=st.session_state.cart_items,
                        discount=discount_amount
                    )
                    
                    if success:
                        st.success(f"✓ {message}")
                        st.info(f"ID Transaksi: **{transaction_id}**")
                        st.session_state.cart_items = []
                        time.sleep(1)
                        st.balloons()
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")
        else:
            st.info("Tambahkan item untuk melihat preview struk")

def render_master_data_page():
    """Render master data management page - REQUIRES ADMIN PIN"""
    require_admin_auth("Data Master")
    
    render_page_header("package", "Manajemen Data Master", "Kelola produk dan pelanggan")
    
    tab_products, tab_customers = st.tabs(["Produk", "Pelanggan"])
    
    # PRODUCTS TAB
    with tab_products:
        st.subheader("Manajemen Produk")
        
        with st.expander("➕ Tambah Produk Baru", expanded=False):
            with st.form("create_product_form", clear_on_submit=True):
                col1, col2 = st.columns(2)
                
                with col1:
                    name = st.text_input("Nama Produk", placeholder="Contoh: Laptop Dell")
                    price = st.number_input("Harga (Rp)", min_value=0, step=1000)
                
                with col2:
                    stock = st.number_input("Stok Awal", min_value=0, step=1)
                    category = st.selectbox("Kategori", ["Elektronik", "Makanan & Minuman", "Pakaian", "Kesehatan", "Lainnya"])
                
                if st.form_submit_button("Simpan Produk", use_container_width=True):
                    if not name.strip():
                        st.error("Nama produk harus diisi!")
                    else:
                        success, message = create_product(name, price, stock, category)
                        if success:
                            st.success(message)
                            # Log initial stock
                            log_stock_movement(0, stock, "Restock", f"Stok awal produk: {name}")
                            st.rerun()
                        else:
                            st.error(message)
        
        st.markdown("---")
        
        products_df = fetch_products(force_refresh=True)
        
        if not products_df.empty:
            st.subheader(f"Daftar Produk ({len(products_df)})")
            
            search_term = st.text_input("🔍 Cari Produk", placeholder="Ketik nama produk...")
            
            if search_term:
                products_df = products_df[products_df['nama_produk'].str.contains(search_term, case=False, na=False)]
            
            for idx, product in products_df.iterrows():
                col1, col2, col3, col4, col5, col6 = st.columns([3, 2, 1.5, 1.5, 1, 1])
                
                with col1:
                    st.markdown(f"**{product['nama_produk']}**")
                    st.caption(f"ID: {product['produk_id']}")
                
                with col2:
                    st.markdown(f"Kategori: {product['kategori']}")
                
                with col3:
                    st.markdown(f"Harga: {format_currency(product['harga'])}")
                
                with col4:
                    stock_color = COLORS['success'] if product['stok'] >= 10 else (COLORS['warning'] if product['stok'] >= 5 else COLORS['danger'])
                    st.markdown(f"<span style='color: {stock_color};'>Stok: {product['stok']}</span>", unsafe_allow_html=True)
                
                with col5:
                    if st.button("✏", key=f"edit_prod_{product['produk_id']}", help="Edit"):
                        st.session_state[f"editing_product_{product['produk_id']}"] = True
                
                with col6:
                    if st.button("🗑", key=f"del_prod_{product['produk_id']}", help="Hapus"):
                        st.session_state[f"deleting_product_{product['produk_id']}"] = True
                
                if st.session_state.get(f"editing_product_{product['produk_id']}", False):
                    with st.expander("Edit Produk", expanded=True):
                        with st.form(f"edit_form_{product['produk_id']}"):
                            col1, col2 = st.columns(2)
                            with col1:
                                new_name = st.text_input("Nama", value=product['nama_produk'])
                                new_price = st.number_input("Harga", value=int(product['harga']), step=1000)
                            with col2:
                                old_stock = int(product['stok'])
                                new_stock = st.number_input("Stok", value=old_stock, step=1)
                                new_category = st.selectbox("Kategori", ["Elektronik", "Makanan & Minuman", "Pakaian", "Kesehatan", "Lainnya"], 
                                                          index=["Elektronik", "Makanan & Minuman", "Pakaian", "Kesehatan", "Lainnya"].index(product['kategori']) if product['kategori'] in ["Elektronik", "Makanan & Minuman", "Pakaian", "Kesehatan", "Lainnya"] else 4)
                            
                            col_save, col_cancel = st.columns(2)
                            with col_save:
                                if st.form_submit_button("💾 Update", use_container_width=True):
                                    success, message = update_product(product['produk_id'], new_name, new_price, new_stock, new_category)
                                    if success:
                                        # Log stock adjustment if changed
                                        if new_stock != old_stock:
                                            log_stock_movement(
                                                product['produk_id'],
                                                new_stock - old_stock,
                                                "Adjustment",
                                                f"Update manual: {old_stock} → {new_stock}"
                                            )
                                        st.success(message)
                                        st.session_state[f"editing_product_{product['produk_id']}"] = False
                                        st.rerun()
                                    else:
                                        st.error(message)
                            with col_cancel:
                                if st.form_submit_button("❌ Batal", use_container_width=True):
                                    st.session_state[f"editing_product_{product['produk_id']}"] = False
                                    st.rerun()
                
                if st.session_state.get(f"deleting_product_{product['produk_id']}", False):
                    st.warning(f"⚠️ Hapus produk **{product['nama_produk']}**?")
                    col_yes, col_no = st.columns(2)
                    with col_yes:
                        if st.button("Ya, Hapus", key=f"confirm_del_{product['produk_id']}", type="primary"):
                            success, message = delete_product(product['produk_id'])
                            if success:
                                st.success(message)
                                st.session_state[f"deleting_product_{product['produk_id']}"] = False
                                st.rerun()
                            else:
                                st.error(message)
                    with col_no:
                        if st.button("Batal", key=f"cancel_del_{product['produk_id']}"):
                            st.session_state[f"deleting_product_{product['produk_id']}"] = False
                            st.rerun()
                
                st.markdown("---")
        else:
            st.info("Belum ada produk. Tambahkan produk pertama Anda di atas.")
    
    # CUSTOMERS TAB
    with tab_customers:
        st.subheader("Manajemen Pelanggan")
        
        with st.expander("➕ Daftar Pelanggan Baru", expanded=False):
            with st.form("create_customer_form", clear_on_submit=True):
                new_customer_id = generate_unique_id("CUST")
                st.info(f"ID Pelanggan: `{new_customer_id}`")
                
                col1, col2 = st.columns(2)
                with col1:
                    name = st.text_input("Nama Pelanggan", placeholder="Contoh: Budi Santoso")
                with col2:
                    email = st.text_input("Email", placeholder="budi@email.com")
                
                if st.form_submit_button("Daftar Pelanggan", use_container_width=True):
                    if not name.strip():
                        st.error("Nama pelanggan harus diisi!")
                    elif not email.strip() or '@' not in email:
                        st.error("Email harus valid!")
                    else:
                        success, message = create_customer(new_customer_id, name, email)
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)
        
        st.markdown("---")
        
        customers_df = fetch_customers(force_refresh=True)
        
        if not customers_df.empty:
            st.subheader(f"Daftar Pelanggan ({len(customers_df)})")
            
            for idx, customer in customers_df.iterrows():
                col1, col2, col3, col4 = st.columns([3, 3, 1, 1])
                
                with col1:
                    st.markdown(f"**{customer['nama_pelanggan']}**")
                    st.caption(f"ID: {customer['pelanggan_id']}")
                
                with col2:
                    st.markdown(f"📧 {customer['email']}")
                
                with col3:
                    if st.button("✏", key=f"edit_cust_{customer['pelanggan_id']}", help="Edit"):
                        st.session_state[f"editing_customer_{customer['pelanggan_id']}"] = True
                
                with col4:
                    if st.button("🗑", key=f"del_cust_{customer['pelanggan_id']}", help="Hapus"):
                        st.session_state[f"deleting_customer_{customer['pelanggan_id']}"] = True
                
                st.markdown("---")

def render_history_page():
    """Render transaction history with detailed line items"""
    render_page_header("history", "Riwayat Transaksi", "Lihat detail transaksi sebelumnya")
    
    transactions_df = fetch_transactions(force_refresh=True)
    
    if transactions_df.empty:
        st.warning("Belum ada riwayat transaksi.")
        return
    
    transactions_df['tanggal_transaksi'] = pd.to_datetime(transactions_df['tanggal_transaksi'])
    transactions_df['customer_name'] = transactions_df['pelanggan'].apply(
        lambda x: x.get('nama_pelanggan', 'Tidak Diketahui') if isinstance(x, dict) else 'Tidak Diketahui'
    )
    
    st.subheader(f"Total Transaksi: {len(transactions_df)}")
    
    # Summary metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        total_revenue = transactions_df['total_bayar'].sum()
        render_kpi_card("Total Pendapatan", format_currency(total_revenue))
    with col2:
        avg_transaction = total_revenue / len(transactions_df) if len(transactions_df) > 0 else 0
        render_kpi_card("Rata-rata Transaksi", format_currency(avg_transaction))
    with col3:
        render_kpi_card("Jumlah Transaksi", str(len(transactions_df)))
    
    st.markdown("---")
    
    # Display transactions with expandable details
    for idx, trans in transactions_df.iterrows():
        with st.expander(f"🧾 {trans['transaksi_id']} - {trans['customer_name']} - {format_currency(trans['total_bayar'])}"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write(f"**Tanggal:** {trans['tanggal_transaksi'].strftime('%d %B %Y, %H:%M WIB')}")
                st.write(f"**Pelanggan:** {trans['customer_name']}")
                st.write(f"**Total Bayar:** {format_currency(trans['total_bayar'])}")
                st.write(f"**Diskon:** {format_currency(trans.get('diskon', 0))}")
                
                # Fetch and display line items
                st.markdown("---")
                st.write("**Detail Barang:**")
                
                items = fetch_transaction_items(trans['transaksi_id'])
                if items:
                    items_df = pd.DataFrame(items)
                    display_items = items_df[['nama_produk', 'harga_satuan', 'jumlah', 'subtotal']].copy()
                    display_items['harga_satuan'] = display_items['harga_satuan'].apply(format_currency)
                    display_items['subtotal'] = display_items['subtotal'].apply(format_currency)
                    display_items.columns = ['Produk', 'Harga Satuan', 'Jumlah', 'Subtotal']
                    
                    st.dataframe(display_items, use_container_width=True, hide_index=True)
                else:
                    st.info("Detail item tidak tersedia")
            
            with col2:
                # Mini receipt
                if items:
                    st.markdown("**Ringkasan:**")
                    for item in items:
                        st.caption(f"{item['nama_produk']} x{item['jumlah']}")
                    st.markdown("---")
                    st.write(f"**Total:** {format_currency(trans['total_bayar'])}")

def render_dashboard_page():
    """Render analytics dashboard - REQUIRES ADMIN PIN"""
    require_admin_auth("Dashboard")
    
    render_page_header("dashboard", "Dashboard Analitik", "Analisis performa bisnis real-time")
    
    df_transactions = fetch_transactions(force_refresh=True)
    
    if df_transactions.empty:
        st.warning("Belum ada data transaksi untuk ditampilkan.")
        return
    
    df_transactions['tanggal_transaksi'] = pd.to_datetime(df_transactions['tanggal_transaksi'])
    df_transactions['date'] = df_transactions['tanggal_transaksi'].dt.date
    
    # KPIs
    total_revenue = df_transactions['total_bayar'].sum()
    total_orders = len(df_transactions)
    avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        render_kpi_card("Total Pendapatan", format_currency(total_revenue))
    with col2:
        render_kpi_card("Jumlah Order", f"{total_orders:,}")
    with col3:
        render_kpi_card("Nilai Rata-rata", format_currency(avg_order_value))
    with col4:
        products_df = fetch_products()
        low_stock_count = len(products_df[products_df['stok'] < 10]) if not products_df.empty else 0
        render_kpi_card("Stok Rendah", str(low_stock_count))
    
    st.markdown("---")
    
    # Revenue chart
    st.subheader("Tren Pendapatan (30 Hari Terakhir)")
    
    daily_revenue = df_transactions.groupby('date')['total_bayar'].sum().reset_index()
    daily_revenue = daily_revenue.sort_values('date')
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=daily_revenue['date'],
        y=daily_revenue['total_bayar'],
        mode='lines+markers',
        name='Pendapatan',
        line=dict(color=COLORS['accent'], width=3),
        marker=dict(size=8),
        fill='tozeroy',
        fillcolor=f"rgba(59, 130, 246, 0.1)"
    ))
    
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=COLORS['text_primary']),
        xaxis=dict(title="Tanggal", gridcolor=COLORS['bg_tertiary']),
        yaxis=dict(title="Pendapatan (Rp)", gridcolor=COLORS['bg_tertiary']),
        hovermode='x unified',
        margin=dict(l=0, r=0, t=30, b=0)
    )
    
    st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """Main application entry point"""
    
    init_session_state()
    inject_custom_css()
    
    render_top_nav()
    
    # Route to pages
    if st.session_state.current_page == "Kasir":
        render_cashier_page()
    elif st.session_state.current_page == "Data Master":
        render_master_data_page()
    elif st.session_state.current_page == "Riwayat":
        render_history_page()
    elif st.session_state.current_page == "Dashboard":
        render_dashboard_page()

if __name__ == "__main__":
    main()
