"""
PelitPos Enterprise Edition v4.0
Tagline: "gk medit gk sugeh ta?"

Enterprise Features:
- Auto-print receipt functionality
- PPN 11% permanently stored in database
- Professional sidebar navigation
- Enterprise UI/UX with visual hierarchy
- Print-friendly CSS
- Reprint receipts from history
- Instant customer registration
"""

import streamlit as st
import streamlit.components.v1 as components
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
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="PelitPos Enterprise",
    layout="wide",
    page_icon="💡",
    initial_sidebar_state="expanded"
)

# Admin PIN (Default: "1234")
ADMIN_PIN_HASH = hashlib.sha256("1234".encode()).hexdigest()

@st.cache_resource
def init_supabase_connection():
    try:
        return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None

supabase = init_supabase_connection()

# ============================================================================
# DESIGN SYSTEM
# ============================================================================

COLORS = {
    "bg_primary": "#0f172a",
    "bg_secondary": "#1e293b",
    "bg_tertiary": "#334155",
    "bg_hover": "#475569",
    "accent": "#3b82f6",
    "accent_hover": "#2563eb",
    "success": "#10b981",
    "warning": "#f59e0b",
    "danger": "#ef4444",
    "text_primary": "#f1f5f9",
    "text_secondary": "#cbd5e1",
    "text_muted": "#64748b",
    "border": "#334155"
}

def inject_enterprise_css():
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {{
        font-family: 'Inter', -apple-system, sans-serif;
        color: {COLORS['text_primary']};
        background: {COLORS['bg_primary']};
    }}
    
    .stApp {{ max-width: 1400px; margin: 0 auto; }}
    
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    
    /* Sidebar Navigation */
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {COLORS['bg_secondary']} 0%, {COLORS['bg_primary']} 100%);
        border-right: 1px solid {COLORS['border']};
    }}
    
    /* Typography */
    h1 {{ font-size: 32px; font-weight: 700; letter-spacing: -0.5px; color: {COLORS['text_primary']}; }}
    h2 {{ font-size: 24px; font-weight: 600; color: {COLORS['text_primary']}; }}
    h3 {{ font-size: 18px; font-weight: 600; color: {COLORS['text_secondary']}; }}
    h4 {{ font-size: 16px; font-weight: 500; text-transform: uppercase; }}
    
    /* Cards */
    .card-elevated {{
        background: linear-gradient(135deg, {COLORS['bg_secondary']} 0%, {COLORS['bg_primary']} 100%);
        border: 1px solid rgba(255,255,255,0.05);
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        transition: all 0.3s;
    }}
    
    .card-elevated:hover {{
        box-shadow: 0 10px 15px rgba(0,0,0,0.4);
        transform: translateY(-2px);
    }}
    
    /* Button Hierarchy */
    .stButton > button[kind="primary"] {{
        background: linear-gradient(135deg, {COLORS['accent']} 0%, {COLORS['accent_hover']} 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 12px 28px !important;
        box-shadow: 0 4px 6px rgba(59,130,246,0.4) !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }}
    
    .stButton > button[kind="primary"]:hover {{
        background: linear-gradient(135deg, {COLORS['accent_hover']} 0%, #1d4ed8 100%) !important;
        box-shadow: 0 10px 15px rgba(59,130,246,0.5) !important;
        transform: translateY(-2px) !important;
    }}
    
    .stButton > button {{
        background: {COLORS['bg_tertiary']} !important;
        color: {COLORS['text_primary']} !important;
        border: 1px solid {COLORS['border']} !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        padding: 10px 20px !important;
    }}
    
    .stButton > button:hover {{
        background: {COLORS['bg_hover']} !important;
        border-color: {COLORS['accent']} !important;
    }}
    
    /* Forms */
    input, select, textarea {{
        background: {COLORS['bg_tertiary']} !important;
        border: 1px solid {COLORS['border']} !important;
        border-radius: 8px !important;
        color: {COLORS['text_primary']} !important;
    }}
    
    input:focus, select:focus {{
        border-color: {COLORS['accent']} !important;
        box-shadow: 0 0 0 3px rgba(59,130,246,0.15) !important;
    }}
    
    /* Tables */
    thead tr {{ background: {COLORS['bg_tertiary']}; position: sticky; top: 0; }}
    thead th {{ 
        padding: 12px; 
        text-transform: uppercase; 
        font-size: 11px; 
        font-weight: 600;
        color: {COLORS['text_muted']};
    }}
    tbody tr:nth-child(even) {{ background: rgba(255,255,255,0.02); }}
    tbody tr:hover {{ background: rgba(59,130,246,0.08); }}
    tbody td {{ padding: 12px; border-bottom: 1px solid {COLORS['border']}; }}
    
    /* Metrics */
    [data-testid="stMetricValue"] {{ 
        color: {COLORS['accent']}; 
        font-size: 36px; 
        font-weight: 700; 
    }}
    
    /* Receipt */
    .receipt-container {{
        background: {COLORS['bg_secondary']};
        border: 2px solid {COLORS['border']};
        border-radius: 12px;
        padding: 28px;
        font-family: 'Courier New', monospace;
    }}
    
    .receipt-total {{
        font-size: 28px;
        font-weight: 700;
        color: {COLORS['success']};
        text-align: right;
        margin-top: 20px;
        padding-top: 20px;
        border-top: 3px solid {COLORS['accent']};
    }}
    
    /* Print Styles */
    @media print {{
        body * {{ visibility: hidden; }}
        .receipt-container, .receipt-container * {{ visibility: visible; }}
        .receipt-container {{
            position: absolute;
            left: 0;
            top: 0;
            width: 80mm;
            background: white;
            color: black;
        }}
        .stButton {{ display: none; }}
    }}
    
    /* Sidebar Nav */
    .nav-item {{
        padding: 12px 16px;
        margin: 4px 0;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.2s;
        color: {COLORS['text_secondary']};
        font-weight: 500;
    }}
    
    .nav-item:hover {{
        background: rgba(59,130,246,0.1);
        color: {COLORS['accent']};
    }}
    
    .nav-item.active {{
        background: linear-gradient(90deg, rgba(59,130,246,0.2), rgba(59,130,246,0.05));
        color: {COLORS['accent']};
        border-left: 3px solid {COLORS['accent']};
        font-weight: 600;
    }}
    </style>
    """, unsafe_allow_html=True)

# ============================================================================
# SESSION STATE
# ============================================================================

def init_session_state():
    defaults = {
        'products_cache': None,
        'customers_cache': None,
        'transactions_cache': None,
        'cart_items': [],
        'current_page': 'Kasir',
        'admin_authenticated': False,
        'last_transaction_id': None
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def invalidate_cache(cache_type='all'):
    caches = ['products', 'customers', 'transactions']
    for cache in caches:
        if cache_type == 'all' or cache_type == cache:
            st.session_state[f'{cache}_cache'] = None

# ============================================================================
# SECURITY
# ============================================================================

def check_admin_pin(pin: str) -> bool:
    return hashlib.sha256(pin.encode()).hexdigest() == ADMIN_PIN_HASH

def require_admin_auth(page_name: str):
    if not st.session_state.admin_authenticated:
        st.warning(f"🔒 {page_name} requires Admin PIN")
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            pin = st.text_input("Enter Admin PIN", type="password", key=f"pin_{page_name}")
            if st.button("Verify", use_container_width=True):
                if check_admin_pin(pin):
                    st.session_state.admin_authenticated = True
                    st.success("✓ Authenticated")
                    st.rerun()
                else:
                    st.error("❌ Invalid PIN")
        st.stop()

# ============================================================================
# UTILITIES
# ============================================================================

def get_jakarta_timezone():
    return pytz.timezone('Asia/Jakarta')

def get_current_datetime():
    return datetime.now(get_jakarta_timezone())

def generate_unique_id(prefix: str) -> str:
    timestamp = get_current_datetime().strftime('%Y%m%d%H%M%S')
    random_hex = secrets.token_hex(2).upper()
    return f"{prefix}-{timestamp}-{random_hex}"

def format_currency(amount: float) -> str:
    return f"Rp {amount:,.0f}".replace(',', '.')

def render_page_header(title: str, subtitle: str = None):
    subtitle_html = f'<p style="margin:0;color:{COLORS["text_muted"]};font-size:15px;">{subtitle}</p>' if subtitle else ''
    st.markdown(f"""
        <div style="margin-bottom:32px;padding-bottom:20px;border-bottom:1px solid {COLORS['border']};">
            <h1 style="margin:0 0 8px 0;">{title}</h1>
            {subtitle_html}
        </div>
    """, unsafe_allow_html=True)

# ============================================================================
# PRINT FUNCTIONALITY
# ============================================================================

def trigger_print_receipt(transaction_id: str):
    """Print receipt using window.print()"""
    try:
        trans_data = supabase.table("transaksi").select("*, pelanggan(nama_pelanggan)").eq("transaksi_id", transaction_id).execute()
        items_data = supabase.table("transaksi_item").select("*").eq("transaksi_id", transaction_id).execute()
        
        if not trans_data.data or not items_data.data:
            st.error("Transaction data not found")
            return
        
        trans = trans_data.data[0]
        items = items_data.data
        
        customer_name = trans.get('pelanggan', {}).get('nama_pelanggan', 'Guest') if isinstance(trans.get('pelanggan'), dict) else 'Guest'
        
        items_html = ""
        for item in items:
            items_html += f"<div style='display:flex;justify-content:space-between;margin:5px 0;'><span>{item['nama_produk']} x{item['jumlah']}</span><span>{format_currency(item['subtotal'])}</span></div>"
        
        receipt_html = f"""
        <div style="width:80mm;font-family:'Courier New',monospace;font-size:12px;padding:10mm;">
            <div style="text-align:center;margin-bottom:10px;">
                <h2 style="margin:0;">💡 PelitPos</h2>
                <p style="margin:0;font-size:10px;">gk medit gk sugeh ta?</p>
            </div>
            <hr>
            <div style="margin:10px 0;">
                <p style="margin:2px 0;">Invoice: {trans['transaksi_id']}</p>
                <p style="margin:2px 0;">Date: {trans['tanggal_transaksi']}</p>
                <p style="margin:2px 0;">Customer: {customer_name}</p>
            </div>
            <hr>
            {items_html}
            <hr>
            <div style="margin:10px 0;">
                <div style="display:flex;justify-content:space-between;"><span>Subtotal:</span><span>{format_currency(trans.get('subtotal', 0))}</span></div>
                <div style="display:flex;justify-content:space-between;"><span>PPN 11%:</span><span>{format_currency(trans.get('ppn', 0))}</span></div>
                <div style="display:flex;justify-content:space-between;"><span>Discount:</span><span>-{format_currency(trans.get('diskon', 0))}</span></div>
            </div>
            <hr>
            <div style="text-align:right;font-size:16px;font-weight:bold;margin:10px 0;">
                TOTAL: {format_currency(trans['total_bayar'])}
            </div>
            <hr>
            <p style="text-align:center;font-size:10px;margin-top:10px;">Thank you!</p>
        </div>
        """.replace("'", "\\'").replace("\n", "")
        
        print_js = f"""
        <script>
        (function() {{
            var w = window.open('', '', 'width=400,height=600');
            w.document.write('<html><head><title>Receipt</title>');
            w.document.write('<style>body{{margin:0;padding:10px;}}</style>');
            w.document.write('</head><body>{receipt_html}</body></html>');
            w.document.close();
            setTimeout(function(){{w.print();}}, 250);
        }})();
        </script>
        """
        
        components.html(print_js, height=0)
        
    except Exception as e:
        st.error(f"Print failed: {str(e)}")

# ============================================================================
# DATABASE OPERATIONS
# ============================================================================

def fetch_products(force_refresh=False):
    if not force_refresh and st.session_state.products_cache is not None:
        return st.session_state.products_cache
    try:
        response = supabase.table("produk").select("*").execute()
        df = pd.DataFrame(response.data) if response.data else pd.DataFrame()
        st.session_state.products_cache = df
        return df
    except:
        return pd.DataFrame()

def fetch_customers(force_refresh=False):
    if not force_refresh and st.session_state.customers_cache is not None:
        return st.session_state.customers_cache
    try:
        response = supabase.table("pelanggan").select("*").execute()
        df = pd.DataFrame(response.data) if response.data else pd.DataFrame()
        st.session_state.customers_cache = df
        return df
    except:
        return pd.DataFrame()

def fetch_transactions(force_refresh=False):
    if not force_refresh and st.session_state.transactions_cache is not None:
        return st.session_state.transactions_cache
    try:
        response = supabase.table("transaksi").select("*, pelanggan(nama_pelanggan)").order("tanggal_transaksi", desc=True).execute()
        df = pd.DataFrame(response.data) if response.data else pd.DataFrame()
        st.session_state.transactions_cache = df
        return df
    except:
        return pd.DataFrame()

def fetch_transaction_items(transaction_id: str):
    try:
        response = supabase.table("transaksi_item").select("*").eq("transaksi_id", transaction_id).execute()
        return response.data if response.data else []
    except:
        return []

def create_product(name, price, stock, category):
    try:
        supabase.table("produk").insert({
            "nama_produk": str(name),
            "harga": float(price),
            "stok": int(stock),
            "kategori": str(category)
        }).execute()
        invalidate_cache('products')
        return True, "Product added"
    except Exception as e:
        return False, str(e)

def update_product(product_id, name, price, stock, category):
    try:
        supabase.table("produk").update({
            "nama_produk": str(name),
            "harga": float(price),
            "stok": int(stock),
            "kategori": str(category)
        }).eq("produk_id", int(product_id)).execute()
        invalidate_cache('products')
        return True, "Product updated"
    except Exception as e:
        return False, str(e)

def delete_product(product_id):
    try:
        supabase.table("produk").delete().eq("produk_id", int(product_id)).execute()
        invalidate_cache('products')
        return True, "Product deleted"
    except Exception as e:
        return False, str(e)

def create_customer(customer_id, name, email):
    try:
        supabase.table("pelanggan").insert({
            "pelanggan_id": str(customer_id),
            "nama_pelanggan": str(name),
            "email": str(email)
        }).execute()
        invalidate_cache('customers')
        return True, "Customer registered"
    except Exception as e:
        return False, str(e)

def log_stock_movement(product_id, quantity_change, action_type, notes=""):
    try:
        supabase.table("stok_log").insert({
            "produk_id": int(product_id),
            "jumlah_perubahan": int(quantity_change),
            "tipe_aksi": str(action_type),
            "keterangan": str(notes),
            "waktu": get_current_datetime().isoformat()
        }).execute()
        return True
    except:
        return False

def atomic_stock_update(product_id, quantity):
    try:
        response = supabase.rpc('atomic_stock_deduct', {
            'p_product_id': int(product_id),
            'p_quantity': int(quantity)
        }).execute()
        if response.data and response.data > 0:
            return True, "Stock updated"
        return False, "Insufficient stock"
    except Exception as e:
        return False, str(e)

def process_transaction(customer_id, total_amount, items, discount=0, 
                       new_customer_name=None, new_customer_email=None):
    """Process transaction with PPN calculation and storage"""
    transaction_id = None
    items_created = []
    actual_customer_id = customer_id
    new_customer_created = False
    
    try:
        # Step 0: Create new customer if needed
        if customer_id == "NEW_CUST":
            if not new_customer_name or not new_customer_name.strip():
                return False, "Customer name required", None
            
            actual_customer_id = generate_unique_id("CUST")
            try:
                supabase.table("pelanggan").insert({
                    "pelanggan_id": str(actual_customer_id),
                    "nama_pelanggan": str(new_customer_name).strip(),
                    "email": str(new_customer_email).strip() if new_customer_email else ""
                }).execute()
                new_customer_created = True
                invalidate_cache('customers')
            except Exception as e:
                return False, f"Customer registration failed: {str(e)}", None
        
        # Step 1: Validate stock
        products_df = fetch_products()
        for item in items:
            product_row = products_df[products_df['produk_id'] == item['product_id']]
            if product_row.empty:
                if new_customer_created:
                    try:
                        supabase.table("pelanggan").delete().eq("pelanggan_id", actual_customer_id).execute()
                    except:
                        pass
                return False, f"Product {item['product_name']} not found", None
            
            current_stock = int(product_row.iloc[0]['stok'])
            if current_stock < item['quantity']:
                if new_customer_created:
                    try:
                        supabase.table("pelanggan").delete().eq("pelanggan_id", actual_customer_id).execute()
                    except:
                        pass
                return False, f"Insufficient stock for {item['product_name']} (Available: {current_stock})", None
        
        # Step 2: Calculate amounts
        subtotal = float(sum(item['quantity'] * item['price'] for item in items))
        ppn_amount = float(subtotal * 0.11)  # PPN 11%
        final_total = float(subtotal + ppn_amount - discount)
        
        # Step 3: Create transaction header WITH PPN
        transaction_id = generate_unique_id("TRX")
        transaction_data = {
            "transaksi_id": str(transaction_id),
            "pelanggan_id": str(actual_customer_id),
            "subtotal": float(subtotal),  # NEW: Stored in DB
            "ppn": float(ppn_amount),     # NEW: PPN 11% stored in DB
            "diskon": float(discount),
            "total_bayar": float(final_total),
            "tanggal_transaksi": get_current_datetime().isoformat()
        }
        supabase.table("transaksi").insert(transaction_data).execute()
        
        # Step 4: Create transaction items with price snapshots
        for item in items:
            item_data = {
                "transaksi_id": str(transaction_id),
                "produk_id": int(item['product_id']),
                "nama_produk": str(item['product_name']),
                "harga_satuan": float(item['price']),
                "jumlah": int(item['quantity']),
                "subtotal": float(item['price'] * item['quantity'])
            }
            supabase.table("transaksi_item").insert(item_data).execute()
            items_created.append(item['product_id'])
            
            # Step 5: Atomic stock update
            success, message = atomic_stock_update(int(item['product_id']), int(item['quantity']))
            if not success:
                # Rollback
                for pid in items_created:
                    supabase.table("transaksi_item").delete().eq("transaksi_id", transaction_id).eq("produk_id", pid).execute()
                supabase.table("transaksi").delete().eq("transaksi_id", transaction_id).execute()
                if new_customer_created:
                    try:
                        supabase.table("pelanggan").delete().eq("pelanggan_id", actual_customer_id).execute()
                    except:
                        pass
                return False, f"Stock update failed: {message}", None
            
            # Step 6: Log stock movement
            log_stock_movement(
                int(item['product_id']),
                -int(item['quantity']),
                "Penjualan",
                f"Transaction: {transaction_id}"
            )
        
        # Success
        invalidate_cache('all')
        st.session_state.last_transaction_id = transaction_id
        
        success_msg = "Transaction processed successfully"
        if new_customer_created:
            success_msg += f" (New customer '{new_customer_name}' registered)"
        
        return True, success_msg, transaction_id
        
    except Exception as e:
        # Rollback on error
        if transaction_id:
            try:
                supabase.table("transaksi_item").delete().eq("transaksi_id", transaction_id).execute()
                supabase.table("transaksi").delete().eq("transaksi_id", transaction_id).execute()
            except:
                pass
        if new_customer_created and actual_customer_id:
            try:
                supabase.table("pelanggan").delete().eq("pelanggan_id", actual_customer_id).execute()
            except:
                pass
        return False, f"Transaction failed: {str(e)}", None


# ============================================================================
# UI COMPONENTS
# ============================================================================

def render_receipt(items, subtotal, tax, discount, total, transaction_id=None, customer_name=None):
    """Render print-friendly receipt with PPN breakdown"""
    current_time = get_current_datetime()
    
    # Build items HTML
    items_html = ""
    for item in items:
        item_total = item['quantity'] * item['price']
        items_html += f"""
        <div style="display:flex;justify-content:space-between;padding:8px 0;font-size:13px;border-bottom:1px dotted {COLORS['border']};">
            <div>
                <div style="color:{COLORS['text_primary']};font-weight:500;">{item['product_name']}</div>
                <div style="color:{COLORS['text_muted']};font-size:11px;">{item['quantity']} x {format_currency(item['price'])}</div>
            </div>
            <div style="color:{COLORS['text_primary']};font-weight:600;">{format_currency(item_total)}</div>
        </div>
        """
    
    # Complete receipt HTML
    receipt_html = f"""
    <div class="receipt-container" id="receipt-to-print" style="background:{COLORS['bg_secondary']};border:2px solid {COLORS['border']};border-radius:12px;padding:28px;font-family:'Courier New',monospace;box-shadow:0 4px 6px rgba(0,0,0,0.3);">
        <div style="text-align:center;border-bottom:2px dashed {COLORS['border']};padding-bottom:20px;margin-bottom:20px;">
            <h2 style="margin:0;color:{COLORS['text_primary']};">💡 PelitPos</h2>
            <p style="margin:5px 0;color:{COLORS['text_muted']};font-size:12px;">gk medit gk sugeh ta?</p>
            <p style="margin:0;color:{COLORS['text_muted']};font-size:11px;">Jl. Enterprise Boulevard No. 123</p>
        </div>
        
        <div style="margin:16px 0;font-size:12px;color:{COLORS['text_muted']};">
            <div style="display:flex;justify-content:space-between;margin:5px 0;">
                <span>Invoice:</span>
                <span style="color:{COLORS['text_primary']};font-weight:600;">{transaction_id or 'PREVIEW'}</span>
            </div>
            <div style="display:flex;justify-content:space-between;margin:5px 0;">
                <span>Date:</span>
                <span>{current_time.strftime('%d %b %Y, %H:%M')}</span>
            </div>
            <div style="display:flex;justify-content:space-between;margin:5px 0;">
                <span>Customer:</span>
                <span>{customer_name or 'Guest'}</span>
            </div>
        </div>
        
        <div style="border-top:2px dashed {COLORS['border']};margin:16px 0;"></div>
        
        <h4 style="margin:10px 0;color:{COLORS['text_primary']};">Items:</h4>
        
        {items_html}
        
        <div style="border-top:2px dashed {COLORS['border']};margin:16px 0;padding-top:16px;">
            <div style="display:flex;justify-content:space-between;margin:8px 0;font-size:14px;">
                <span style="color:{COLORS['text_secondary']};">Subtotal:</span>
                <span style="color:{COLORS['text_primary']};">{format_currency(subtotal)}</span>
            </div>
            <div style="display:flex;justify-content:space-between;margin:8px 0;font-size:14px;">
                <span style="color:{COLORS['text_secondary']};">PPN (11%):</span>
                <span style="color:{COLORS['text_primary']};">{format_currency(tax)}</span>
            </div>
            <div style="display:flex;justify-content:space-between;margin:8px 0;font-size:14px;">
                <span style="color:{COLORS['text_secondary']};">Discount:</span>
                <span style="color:{COLORS['danger']};">-{format_currency(discount)}</span>
            </div>
        </div>
        
        <div style="font-size:28px;font-weight:700;color:{COLORS['success']};text-align:right;margin-top:20px;padding-top:20px;border-top:3px solid {COLORS['accent']};letter-spacing:-1px;">
            TOTAL: {format_currency(total)}
        </div>
        
        <div style="text-align:center;margin-top:20px;padding-top:20px;border-top:1px dashed {COLORS['border']};color:{COLORS['text_muted']};font-size:11px;">
            Thank you for your purchase!<br>
            Semoga berkah dan sukses selalu 🙏
        </div>
    </div>
    """
    
    st.markdown(receipt_html, unsafe_allow_html=True)

# ============================================================================
# SIDEBAR NAVIGATION
# ============================================================================

def render_sidebar_nav():
    """Professional sidebar navigation with active states"""
    with st.sidebar:
        st.markdown(f"""
            <div style="text-align:center;padding:20px 0;border-bottom:1px solid {COLORS['border']};">
                <h2 style="margin:0;color:{COLORS['text_primary']};">💡 PelitPos</h2>
                <p style="margin:5px 0 0;color:{COLORS['text_muted']};font-size:11px;">gk medit gk sugeh ta?</p>
                <p style="margin:5px 0 0;color:{COLORS['text_muted']};font-size:10px;">Enterprise Edition v4.0</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### Navigation")
        
        pages = {
            "Kasir": "🛒",
            "Data Master": "📦",
            "Riwayat": "📋",
            "Dashboard": "📊"
        }
        
        for page, icon in pages.items():
            is_active = st.session_state.current_page == page
            
            # Use type parameter only when active
            if is_active:
                if st.button(f"{icon} {page}", key=f"nav_{page}", use_container_width=True, type="primary"):
                    st.session_state.current_page = page
                    st.rerun()
            else:
                if st.button(f"{icon} {page}", key=f"nav_{page}", use_container_width=True):
                    st.session_state.current_page = page
                    st.rerun()
        
        st.markdown("---")
        
        if st.button("🔄 Refresh Data", use_container_width=True):
            invalidate_cache('all')
            st.success("Cache cleared!")
            time.sleep(0.5)
            st.rerun()
        
        if st.session_state.admin_authenticated:
            if st.button("🔒 Logout Admin", use_container_width=True):
                st.session_state.admin_authenticated = False
                st.success("Logged out")
                time.sleep(0.5)
                st.rerun()
        
        st.markdown("---")
        current_time = get_current_datetime()
        st.caption(f"🕒 {current_time.strftime('%H:%M:%S WIB')}")
        st.caption(f"📅 {current_time.strftime('%d %B %Y')}")

# ============================================================================
# PAGES
# ============================================================================

def render_cashier_page():
    """Cashier terminal with instant customer registration"""
    render_page_header("Terminal Kasir", "Process sales transactions")
    
    products_df = fetch_products()
    customers_df = fetch_customers()
    
    if products_df.empty:
        st.warning("⚠️ No products available. Please add products first.")
        return
    
    col_cart, col_receipt = st.columns([2, 1])
    
    with col_cart:
        st.subheader("Shopping Cart")
        
        # Customer Selection
        st.markdown("#### 👤 Customer Information")
        
        is_new_customer = st.checkbox("🆕 New / Unregistered Customer?", key="new_customer_check")
        
        new_customer_name = None
        new_customer_email = None
        
        if is_new_customer:
            new_customer_name = st.text_input("Customer Name", placeholder="Enter name...", key="new_cust_name")
            new_customer_email = st.text_input("Email (Optional)", placeholder="email@example.com", key="new_cust_email")
            customer_id = "NEW_CUST"
            selected_customer_name = new_customer_name if new_customer_name.strip() else "New Customer"
            
            if not new_customer_name.strip():
                st.warning("⚠️ Please enter customer name")
        else:
            if not customers_df.empty:
                customer_options = ["General Customer"] + customers_df['nama_pelanggan'].tolist()
                selected_customer_name = st.selectbox("Select Customer", options=customer_options, key="existing_cust")
                
                if selected_customer_name == "General Customer":
                    general = customers_df[customers_df['nama_pelanggan'] == 'Pelanggan Umum']
                    if not general.empty:
                        customer_id = general.iloc[0]['pelanggan_id']
                    else:
                        customer_id = "NEW_CUST"
                        new_customer_name = "Pelanggan Umum"
                        new_customer_email = "umum@pelitpos.com"
                else:
                    selected_customer = customers_df[customers_df['nama_pelanggan'] == selected_customer_name].iloc[0]
                    customer_id = selected_customer['pelanggan_id']
            else:
                st.info("ℹ️ No customers registered. Please enter new customer details.")
                new_customer_name = st.text_input("Customer Name", value="General Customer", key="first_cust")
                new_customer_email = st.text_input("Email", value="umum@pelitpos.com", key="first_email")
                customer_id = "NEW_CUST"
                selected_customer_name = new_customer_name
        
        st.markdown("---")
        
        # Product Selection
        st.markdown("#### 🛒 Add Products")
        col_prod, col_qty = st.columns([3, 1])
        
        with col_prod:
            product_names = products_df['nama_produk'].tolist()
            selected_product_name = st.selectbox("Select Product", options=product_names, key="prod_select")
        
        selected_product = products_df[products_df['nama_produk'] == selected_product_name].iloc[0]
        
        max_qty = int(selected_product['stok'])
        product_price = float(selected_product['harga'])
        
        with col_qty:
            quantity = st.number_input("Quantity", min_value=1, max_value=max_qty if max_qty > 0 else 1, value=1, key="qty")
        
        if max_qty == 0:
            st.error(f"❌ Out of stock: {selected_product_name}")
        elif max_qty < 5:
            st.warning(f"⚠️ Low stock: {max_qty} units remaining")
        
        if st.button("➕ Add to Cart", use_container_width=True, disabled=(max_qty == 0)):
            cart_item = {
                'product_id': selected_product['produk_id'],
                'product_name': selected_product_name,
                'price': product_price,
                'quantity': quantity
            }
            st.session_state.cart_items.append(cart_item)
            st.success(f"✓ Added: {quantity}x {selected_product_name}")
            st.rerun()
        
        st.markdown("---")
        
        # Cart Display
        if st.session_state.cart_items:
            st.subheader("Cart Items")
            
            for idx, item in enumerate(st.session_state.cart_items):
                col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                
                with col1:
                    st.write(f"**{item['product_name']}**")
                with col2:
                    st.write(f"{item['quantity']} x {format_currency(item['price'])}")
                with col3:
                    st.write(f"**{format_currency(item['quantity'] * item['price'])}**")
                with col4:
                    if st.button("🗑", key=f"remove_{idx}"):
                        st.session_state.cart_items.pop(idx)
                        st.rerun()
            
            if st.button("🗑 Clear Cart", use_container_width=True):
                st.session_state.cart_items = []
                st.rerun()
        else:
            st.info("Cart is empty. Add products to start transaction.")
    
    # Receipt Panel
    with col_receipt:
        st.subheader("Receipt Preview")
        
        if st.session_state.cart_items:
            subtotal = sum(item['quantity'] * item['price'] for item in st.session_state.cart_items)
            tax_amount = subtotal * 0.11  # PPN 11%
            
            discount_amount = st.number_input(
                "Discount (Rp)",
                min_value=0.0,
                max_value=float(subtotal),
                value=0.0,
                step=1000.0,
                key="discount"
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
            
            can_process = True
            if is_new_customer and (not new_customer_name or not new_customer_name.strip()):
                can_process = False
                st.error("❌ Customer name required!")
            
            if st.button("💳 PROCESS PAYMENT", use_container_width=True, type="primary", disabled=not can_process):
                with st.spinner("Processing transaction..."):
                    if customer_id == "NEW_CUST":
                        success, message, transaction_id = process_transaction(
                            customer_id=customer_id,
                            total_amount=grand_total,
                            items=st.session_state.cart_items,
                            discount=discount_amount,
                            new_customer_name=str(new_customer_name).strip() if new_customer_name else "",
                            new_customer_email=str(new_customer_email).strip() if new_customer_email else ""
                        )
                    else:
                        success, message, transaction_id = process_transaction(
                            customer_id=customer_id,
                            total_amount=grand_total,
                            items=st.session_state.cart_items,
                            discount=discount_amount
                        )
                    
                    if success:
                        st.success(f"✓ {message}")
                        st.info(f"Transaction ID: **{transaction_id}**")
                        
                        # Auto-print receipt
                        if st.checkbox("🖨️ Print Receipt", value=True, key="auto_print"):
                            trigger_print_receipt(transaction_id)
                        
                        st.session_state.cart_items = []
                        invalidate_cache('customers')
                        time.sleep(2)
                        st.balloons()
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")
        else:
            st.info("Add items to preview receipt")


def render_master_data_page():
    """Master data management with Admin PIN protection"""
    require_admin_auth("Data Master")
    
    render_page_header("Data Master", "Manage products and customers")
    
    tab_products, tab_customers = st.tabs(["Products", "Customers"])
    
    with tab_products:
        st.subheader("Product Management")
        
        with st.expander("➕ Add New Product", expanded=False):
            with st.form("create_product", clear_on_submit=True):
                col1, col2 = st.columns(2)
                with col1:
                    name = st.text_input("Product Name", placeholder="e.g. Laptop Dell")
                    price = st.number_input("Price (Rp)", min_value=0, step=1000)
                with col2:
                    stock = st.number_input("Initial Stock", min_value=0, step=1)
                    category = st.selectbox("Category", ["Elektronik", "Makanan & Minuman", "Pakaian", "Kesehatan", "Lainnya"])
                
                if st.form_submit_button("Save Product", use_container_width=True):
                    if not name.strip():
                        st.error("Product name required!")
                    else:
                        success, message = create_product(name, price, stock, category)
                        if success:
                            st.success(message)
                            log_stock_movement(0, stock, "Restock", f"Initial stock: {name}")
                            st.rerun()
                        else:
                            st.error(message)
        
        st.markdown("---")
        
        products_df = fetch_products(force_refresh=True)
        
        if not products_df.empty:
            st.subheader(f"Products ({len(products_df)})")
            
            search = st.text_input("🔍 Search products", placeholder="Type product name...")
            
            if search:
                products_df = products_df[products_df['nama_produk'].str.contains(search, case=False, na=False)]
            
            for idx, product in products_df.iterrows():
                col1, col2, col3, col4, col5, col6 = st.columns([3, 2, 1.5, 1.5, 1, 1])
                
                with col1:
                    st.markdown(f"**{product['nama_produk']}**")
                    st.caption(f"ID: {product['produk_id']}")
                with col2:
                    st.markdown(f"Category: {product['kategori']}")
                with col3:
                    st.markdown(f"Price: {format_currency(product['harga'])}")
                with col4:
                    color = COLORS['success'] if product['stok'] >= 10 else (COLORS['warning'] if product['stok'] >= 5 else COLORS['danger'])
                    st.markdown(f"<span style='color:{color};'>Stock: {product['stok']}</span>", unsafe_allow_html=True)
                with col5:
                    if st.button("✏", key=f"edit_prod_{product['produk_id']}"):
                        st.session_state[f"editing_product_{product['produk_id']}"] = True
                with col6:
                    if st.button("🗑", key=f"del_prod_{product['produk_id']}"):
                        st.session_state[f"deleting_product_{product['produk_id']}"] = True
                
                if st.session_state.get(f"editing_product_{product['produk_id']}", False):
                    with st.expander("Edit Product", expanded=True):
                        with st.form(f"edit_{product['produk_id']}"):
                            col1, col2 = st.columns(2)
                            with col1:
                                new_name = st.text_input("Name", value=product['nama_produk'])
                                new_price = st.number_input("Price", value=int(product['harga']), step=1000)
                            with col2:
                                old_stock = int(product['stok'])
                                new_stock = st.number_input("Stock", value=old_stock, step=1)
                                new_category = st.selectbox("Category", ["Elektronik", "Makanan & Minuman", "Pakaian", "Kesehatan", "Lainnya"], 
                                                          index=["Elektronik", "Makanan & Minuman", "Pakaian", "Kesehatan", "Lainnya"].index(product['kategori']) if product['kategori'] in ["Elektronik", "Makanan & Minuman", "Pakaian", "Kesehatan", "Lainnya"] else 4)
                            
                            col_save, col_cancel = st.columns(2)
                            with col_save:
                                if st.form_submit_button("💾 Update", use_container_width=True):
                                    success, message = update_product(product['produk_id'], new_name, new_price, new_stock, new_category)
                                    if success:
                                        if new_stock != old_stock:
                                            log_stock_movement(product['produk_id'], new_stock - old_stock, "Adjustment", f"Manual: {old_stock} → {new_stock}")
                                        st.success(message)
                                        st.session_state[f"editing_product_{product['produk_id']}"] = False
                                        st.rerun()
                                    else:
                                        st.error(message)
                            with col_cancel:
                                if st.form_submit_button("❌ Cancel", use_container_width=True):
                                    st.session_state[f"editing_product_{product['produk_id']}"] = False
                                    st.rerun()
                
                if st.session_state.get(f"deleting_product_{product['produk_id']}", False):
                    st.warning(f"⚠️ Delete **{product['nama_produk']}**?")
                    col_yes, col_no = st.columns(2)
                    with col_yes:
                        if st.button("Yes, Delete", key=f"confirm_del_{product['produk_id']}", type="primary"):
                            success, message = delete_product(product['produk_id'])
                            if success:
                                st.success(message)
                                st.session_state[f"deleting_product_{product['produk_id']}"] = False
                                st.rerun()
                            else:
                                st.error(message)
                    with col_no:
                        if st.button("Cancel", key=f"cancel_del_{product['produk_id']}"):
                            st.session_state[f"deleting_product_{product['produk_id']}"] = False
                            st.rerun()
                
                st.markdown("---")
        else:
            st.info("No products yet. Add your first product above.")
    
    with tab_customers:
        st.subheader("Customer Management")
        
        with st.expander("➕ Register New Customer", expanded=False):
            with st.form("create_customer", clear_on_submit=True):
                new_customer_id = generate_unique_id("CUST")
                st.info(f"Customer ID: `{new_customer_id}`")
                
                col1, col2 = st.columns(2)
                with col1:
                    name = st.text_input("Customer Name", placeholder="e.g. John Doe")
                with col2:
                    email = st.text_input("Email", placeholder="john@email.com")
                
                if st.form_submit_button("Register Customer", use_container_width=True):
                    if not name.strip():
                        st.error("Customer name required!")
                    elif not email.strip() or '@' not in email:
                        st.error("Valid email required!")
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
            st.subheader(f"Customers ({len(customers_df)})")
            
            for idx, customer in customers_df.iterrows():
                col1, col2 = st.columns([4, 4])
                with col1:
                    st.markdown(f"**{customer['nama_pelanggan']}**")
                    st.caption(f"ID: {customer['pelanggan_id']}")
                with col2:
                    st.markdown(f"📧 {customer['email']}")
                
                st.markdown("---")

def render_history_page():
    """Transaction history with PPN details and reprint functionality"""
    render_page_header("Transaction History", "View past transactions with PPN breakdown")
    
    transactions_df = fetch_transactions(force_refresh=True)
    
    if transactions_df.empty:
        st.warning("No transaction history yet.")
        return
    
    transactions_df['tanggal_transaksi'] = pd.to_datetime(transactions_df['tanggal_transaksi'])
    transactions_df['customer_name'] = transactions_df['pelanggan'].apply(
        lambda x: x.get('nama_pelanggan', 'Unknown') if isinstance(x, dict) else 'Unknown'
    )
    
    st.subheader(f"Total Transactions: {len(transactions_df)}")
    
    # Summary metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        total_revenue = transactions_df['total_bayar'].sum()
        st.metric("Total Revenue", format_currency(total_revenue))
    with col2:
        avg_transaction = total_revenue / len(transactions_df) if len(transactions_df) > 0 else 0
        st.metric("Average Transaction", format_currency(avg_transaction))
    with col3:
        st.metric("Number of Transactions", len(transactions_df))
    
    st.markdown("---")
    
    # Transaction list with expandable details
    for idx, trans in transactions_df.iterrows():
        with st.expander(f"🧾 {trans['transaksi_id']} - {trans['customer_name']} - {format_currency(trans['total_bayar'])}"):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"**Date:** {trans['tanggal_transaksi'].strftime('%d %B %Y, %H:%M WIB')}")
                st.write(f"**Customer:** {trans['customer_name']}")
                
                # PPN BREAKDOWN - NEW FEATURE
                st.markdown("### Financial Details")
                st.write(f"**Subtotal:** {format_currency(trans.get('subtotal', 0))}")
                st.write(f"**PPN (11%):** {format_currency(trans.get('ppn', 0))}")
                st.write(f"**Discount:** {format_currency(trans.get('diskon', 0))}")
                st.write(f"**Total Payment:** {format_currency(trans['total_bayar'])}")
                
                # Show items
                st.markdown("---")
                st.write("**Items Purchased:**")
                
                items = fetch_transaction_items(trans['transaksi_id'])
                if items:
                    items_df = pd.DataFrame(items)
                    display_items = items_df[['nama_produk', 'harga_satuan', 'jumlah', 'subtotal']].copy()
                    display_items['harga_satuan'] = display_items['harga_satuan'].apply(format_currency)
                    display_items['subtotal'] = display_items['subtotal'].apply(format_currency)
                    display_items.columns = ['Product', 'Unit Price', 'Quantity', 'Subtotal']
                    
                    st.dataframe(display_items, use_container_width=True, hide_index=True)
                else:
                    st.info("Item details not available")
            
            with col2:
                # REPRINT BUTTON - NEW FEATURE
                st.markdown("### Actions")
                if st.button("🖨️ Reprint Receipt", key=f"print_{trans['transaksi_id']}", use_container_width=True):
                    trigger_print_receipt(trans['transaksi_id'])
                    st.success("Sending to printer...")
                
                # Mini summary
                st.markdown("---")
                st.markdown("**Summary:**")
                for item in items[:3]:  # Show first 3 items
                    st.caption(f"{item['nama_produk']} x{item['jumlah']}")
                if len(items) > 3:
                    st.caption(f"... and {len(items)-3} more")

def render_dashboard_page():
    """Analytics dashboard with PPN insights - Admin only"""
    require_admin_auth("Dashboard")
    
    render_page_header("Analytics Dashboard", "Real-time business performance metrics")
    
    df_transactions = fetch_transactions(force_refresh=True)
    
    if df_transactions.empty:
        st.warning("No transaction data to display.")
        return
    
    df_transactions['tanggal_transaksi'] = pd.to_datetime(df_transactions['tanggal_transaksi'])
    df_transactions['date'] = df_transactions['tanggal_transaksi'].dt.date
    
    # KPI Cards
    total_revenue = df_transactions['total_bayar'].sum()
    total_ppn = df_transactions.get('ppn', pd.Series([0])).sum()
    total_discount = df_transactions.get('diskon', pd.Series([0])).sum()
    total_orders = len(df_transactions)
    avg_order = total_revenue / total_orders if total_orders > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Revenue", format_currency(total_revenue))
    with col2:
        st.metric("Total PPN Collected", format_currency(total_ppn))
    with col3:
        st.metric("Average Order Value", format_currency(avg_order))
    with col4:
        products_df = fetch_products()
        low_stock = len(products_df[products_df['stok'] < 10]) if not products_df.empty else 0
        st.metric("Low Stock Items", low_stock)
    
    st.markdown("---")
    
    # Revenue trend chart
    st.subheader("Revenue Trend (Last 30 Days)")
    
    daily_revenue = df_transactions.groupby('date')['total_bayar'].sum().reset_index()
    daily_revenue = daily_revenue.sort_values('date')
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=daily_revenue['date'],
        y=daily_revenue['total_bayar'],
        mode='lines+markers',
        name='Revenue',
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
        xaxis=dict(title="Date", gridcolor=COLORS['border']),
        yaxis=dict(title="Revenue (Rp)", gridcolor=COLORS['border']),
        hovermode='x unified',
        margin=dict(l=0, r=0, t=30, b=0)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # PPN Analysis
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Tax Collection (PPN)")
        st.write(f"**Total PPN Collected:** {format_currency(total_ppn)}")
        st.write(f"**Average PPN per Transaction:** {format_currency(total_ppn / total_orders if total_orders > 0 else 0)}")
        st.write(f"**PPN as % of Revenue:** {(total_ppn / total_revenue * 100 if total_revenue > 0 else 0):.2f}%")
    
    with col2:
        st.subheader("Discount Analysis")
        st.write(f"**Total Discounts Given:** {format_currency(total_discount)}")
        st.write(f"**Average Discount:** {format_currency(total_discount / total_orders if total_orders > 0 else 0)}")
        st.write(f"**Discount as % of Revenue:** {(total_discount / total_revenue * 100 if total_revenue > 0 else 0):.2f}%")

# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """Main application entry point"""
    init_session_state()
    inject_enterprise_css()
    
    render_sidebar_nav()
    
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
