# 💡 PelitPos Enterprise Edition v4.0
> **"gk medit gk sugeh ta?"**

## ✨ Fitur Enterprise v4.0
- 🖨️ **Auto-Print Receipt** - window.print() dengan CSS thermal printer
- 💰 **PPN 11% Tracking** - Tersimpan permanen di database
- 🔄 **Reprint Receipts** - Cetak ulang dari history
- 🎨 **Professional UI** - Sidebar navigation enterprise-grade
- ⚡ **Instant Customer Reg** - Daftar pelanggan saat transaksi
- 📊 **Enhanced Analytics** - Dashboard dengan breakdown PPN

## 🚀 Quick Installation
```bash
pip install streamlit supabase pandas plotly pytz
```

1. Create Supabase project
2. Run `schema_enterprise.sql` in SQL Editor
3. Create `.streamlit/secrets.toml` with credentials
4. Run `streamlit run app.py`

## 🔐 Default PIN: 1234

## 📖 Key Features
- PPN 11% calculated and stored in database
- Print-optimized CSS (@media print)
- Atomic stock updates (SQL-level)
- Price snapshots for historical accuracy
- Session caching (80% fewer queries)

## 🏗️ Database Changes
New columns in `transaksi` table:
- `subtotal` - Before tax amount
- `ppn` - PPN 11% permanently stored

## 📊 Transaction Flow
```
Cart → Subtotal → PPN 11% → Discount → Total
         ↓          ↓          ↓         ↓
      Stored    Stored     Stored   Stored
```

## 🖨️ Print Functionality
- Auto-print after transaction
- Reprint from history
- 80mm thermal printer optimized
- Shows PPN breakdown

Full documentation: See DOCUMENTATION.md
