# PelitPos Enterprise - Technical Documentation v4.0

## Architecture Overview

### Key Enterprise Features

#### 1. PPN Tracking System
**Problem Solved:** Tax reporting requires permanent record of PPN calculations

**Implementation:**
- Database columns: `subtotal`, `ppn`, `diskon`, `total_bayar`
- PPN = subtotal × 0.11
- Total = subtotal + ppn - discount
- All values stored as DECIMAL(15,2)

**Code:**
```python
subtotal = float(sum(item['quantity'] * item['price'] for item in items))
ppn_amount = float(subtotal * 0.11)
final_total = float(subtotal + ppn_amount - discount)

transaction_data = {
    "subtotal": float(subtotal),
    "ppn": float(ppn_amount),  # Stored permanently
    "diskon": float(discount),
    "total_bayar": float(final_total)
}
```

#### 2. Print Functionality
**Implementation:** window.print() with print-specific CSS

**CSS:**
```css
@media print {
    body * { visibility: hidden; }
    .receipt-container * { visibility: visible; }
    .receipt-container {
        position: absolute;
        width: 80mm;
        /* Thermal printer optimization */
    }
}
```

**JavaScript:**
```javascript
var w = window.open('', '', 'width=400,height=600');
w.document.write(receipt_html);
setTimeout(function(){w.print();}, 250);
```

#### 3. Atomic Stock Updates
**Prevents:** Race conditions in concurrent transactions

**SQL Function:**
```sql
CREATE OR REPLACE FUNCTION atomic_stock_deduct(
    p_product_id INTEGER,
    p_quantity INTEGER
)
RETURNS INTEGER AS $$
BEGIN
    UPDATE produk
    SET stok = stok - p_quantity
    WHERE produk_id = p_product_id
      AND stok >= p_quantity;
    RETURN ROW_COUNT;
END;
$$ LANGUAGE plpgsql;
```

#### 4. Price Snapshots
**Ensures:** Historical price accuracy in reports

**Implementation:**
```python
item_data = {
    "nama_produk": str(item['product_name']),  # Snapshot
    "harga_satuan": float(item['price']),      # Snapshot
    "jumlah": int(item['quantity']),
    "subtotal": float(item['price'] * item['quantity'])
}
```

#### 5. Transaction Rollback
**Ensures:** Data integrity with all-or-nothing processing

**Flow:**
```
Start Transaction
├─ Create Customer (if new)
├─ Validate Stock
├─ Create Transaction Header
├─ Create Transaction Items
├─ Atomic Stock Update ← If fails, rollback all
└─ Log Stock Movement
```

## Database Schema

### transaksi (NEW COLUMNS)
```sql
CREATE TABLE transaksi (
    transaksi_id VARCHAR(50) PRIMARY KEY,
    pelanggan_id VARCHAR(50),
    subtotal DECIMAL(15, 2) NOT NULL,  -- NEW
    ppn DECIMAL(15, 2) NOT NULL,       -- NEW
    diskon DECIMAL(15, 2) DEFAULT 0,
    total_bayar DECIMAL(15, 2) NOT NULL,
    tanggal_transaksi TIMESTAMP
);
```

## API Functions

### process_transaction()
**Purpose:** Process sale with PPN calculation

**Parameters:**
- `customer_id`: str
- `total_amount`: float
- `items`: List[Dict]
- `discount`: float
- `new_customer_name`: Optional[str]
- `new_customer_email`: Optional[str]

**Returns:** (success: bool, message: str, transaction_id: str)

### trigger_print_receipt()
**Purpose:** Open print dialog with receipt

**Parameters:**
- `transaction_id`: str

**Implementation:** Fetches transaction data, generates HTML, opens print window

## Performance Optimizations

### Session Caching
```python
def fetch_products(force_refresh=False):
    if not force_refresh and st.session_state.products_cache:
        return st.session_state.products_cache
    # Query database only when needed
```

### Selective Cache Invalidation
```python
invalidate_cache('products')  # Only products
invalidate_cache('all')        # Everything
```

## Security

### PIN Authentication
```python
ADMIN_PIN_HASH = hashlib.sha256("1234".encode()).hexdigest()

def check_admin_pin(pin: str) -> bool:
    return hashlib.sha256(pin.encode()).hexdigest() == ADMIN_PIN_HASH
```

### Protected Routes
- Data Master (edit/delete)
- Dashboard Analytics

## UI/UX Design System

### Color Palette
```python
COLORS = {
    "accent": "#3b82f6",       # Primary actions
    "success": "#10b981",      # Positive states
    "warning": "#f59e0b",      # Caution
    "danger": "#ef4444",       # Destructive
}
```

### Button Hierarchy
1. **Primary** - Main actions (Process Payment)
2. **Secondary** - Add to cart
3. **Destructive** - Delete operations
4. **Ghost** - Cancel actions

### Typography Scale
- H1: 32px (Page titles)
- H2: 24px (Section headers)
- H3: 18px (Subsections)
- H4: 16px (Labels - uppercase)

## Monitoring Queries

### PPN Analysis
```sql
SELECT 
    DATE(tanggal_transaksi) as date,
    SUM(subtotal) as gross_sales,
    SUM(ppn) as tax_collected,
    SUM(total_bayar) as net_revenue
FROM transaksi
GROUP BY DATE(tanggal_transaksi);
```

### Revenue by Product
```sql
SELECT 
    ti.nama_produk,
    SUM(ti.subtotal) as revenue
FROM transaksi_item ti
GROUP BY ti.nama_produk
ORDER BY revenue DESC;
```

## Migration from v3.x

### Step 1: Add Columns
```sql
ALTER TABLE transaksi ADD COLUMN subtotal DECIMAL(15,2);
ALTER TABLE transaksi ADD COLUMN ppn DECIMAL(15,2);
```

### Step 2: Backfill Data (Optional)
```sql
UPDATE transaksi
SET subtotal = total_bayar / 1.11,
    ppn = (total_bayar / 1.11) * 0.11
WHERE ppn IS NULL;
```

## Troubleshooting

### Issue: PPN not calculated
**Check:** process_transaction() function has PPN calculation
**Fix:** Ensure formula: `ppn = subtotal * 0.11`

### Issue: Print window blank
**Check:** Ad blocker, popup blocker
**Fix:** Allow popups for localhost

### Issue: Stock oversold
**Check:** atomic_stock_deduct function exists
**Fix:** Re-run function creation from schema

## Best Practices

1. **Always convert types:**
   ```python
   int(value)    # pandas int64 → Python int
   float(value)  # pandas float64 → Python float
   str(value)    # Force string
   ```

2. **Cache invalidation:**
   ```python
   # After any data modification
   invalidate_cache('relevant_cache')
   ```

3. **Error handling:**
   ```python
   try:
       # Database operation
   except Exception as e:
       # Rollback if needed
       return False, str(e)
   ```

4. **PPN calculation:**
   ```python
   # Always calculate from subtotal
   ppn = subtotal * 0.11  # Not from total
   ```

---

**Version:** 4.0.0 Enterprise
**Last Updated:** 2026-02-15
**Author:** PelitPos Development Team
