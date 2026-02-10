-- ============================================================================
-- PelitPos Database Schema
-- Normalized structure with price snapshots and audit trail
-- ============================================================================

-- Table: produk (Products)
CREATE TABLE IF NOT EXISTS produk (
    produk_id SERIAL PRIMARY KEY,
    nama_produk VARCHAR(255) NOT NULL,
    harga DECIMAL(15, 2) NOT NULL,
    stok INTEGER NOT NULL DEFAULT 0,
    kategori VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table: pelanggan (Customers)
CREATE TABLE IF NOT EXISTS pelanggan (
    pelanggan_id VARCHAR(50) PRIMARY KEY,
    nama_pelanggan VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table: transaksi (Transaction Headers)
CREATE TABLE IF NOT EXISTS transaksi (
    transaksi_id VARCHAR(50) PRIMARY KEY,
    pelanggan_id VARCHAR(50) REFERENCES pelanggan(pelanggan_id) ON DELETE SET NULL,
    total_bayar DECIMAL(15, 2) NOT NULL,
    diskon DECIMAL(15, 2) DEFAULT 0,
    tanggal_transaksi TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table: transaksi_item (Transaction Line Items with Price Snapshots)
-- CRITICAL: This table stores price snapshots to maintain historical accuracy
CREATE TABLE IF NOT EXISTS transaksi_item (
    item_id SERIAL PRIMARY KEY,
    transaksi_id VARCHAR(50) REFERENCES transaksi(transaksi_id) ON DELETE CASCADE,
    produk_id INTEGER REFERENCES produk(produk_id) ON DELETE SET NULL,
    nama_produk VARCHAR(255) NOT NULL,  -- Price snapshot: product name at time of sale
    harga_satuan DECIMAL(15, 2) NOT NULL,  -- Price snapshot: unit price at time of sale
    jumlah INTEGER NOT NULL,
    subtotal DECIMAL(15, 2) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table: stok_log (Stock Movement Audit Trail)
CREATE TABLE IF NOT EXISTS stok_log (
    log_id SERIAL PRIMARY KEY,
    produk_id INTEGER REFERENCES produk(produk_id) ON DELETE CASCADE,
    jumlah_perubahan INTEGER NOT NULL,  -- Negative for sales, positive for restock
    tipe_aksi VARCHAR(50) NOT NULL,  -- 'Penjualan', 'Restock', 'Adjustment', 'Pengembalian'
    keterangan TEXT,
    waktu TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- Indexes for Performance Optimization
-- ============================================================================

CREATE INDEX idx_transaksi_tanggal ON transaksi(tanggal_transaksi DESC);
CREATE INDEX idx_transaksi_pelanggan ON transaksi(pelanggan_id);
CREATE INDEX idx_transaksi_item_transaksi ON transaksi_item(transaksi_id);
CREATE INDEX idx_transaksi_item_produk ON transaksi_item(produk_id);
CREATE INDEX idx_stok_log_produk ON stok_log(produk_id);
CREATE INDEX idx_stok_log_waktu ON stok_log(waktu DESC);

-- ============================================================================
-- Database Function: Atomic Stock Deduction (Prevents Race Conditions)
-- ============================================================================

-- This function performs atomic stock updates directly in SQL
-- Usage: SELECT atomic_stock_deduct(product_id, quantity_to_deduct);
-- Returns: number of rows updated (1 if successful, 0 if failed)

CREATE OR REPLACE FUNCTION atomic_stock_deduct(
    p_product_id INTEGER,
    p_quantity INTEGER
)
RETURNS INTEGER AS $$
DECLARE
    rows_updated INTEGER;
BEGIN
    -- Perform atomic UPDATE with stock validation
    -- Only updates if current stock >= quantity to deduct
    UPDATE produk
    SET 
        stok = stok - p_quantity,
        updated_at = NOW()
    WHERE 
        produk_id = p_product_id
        AND stok >= p_quantity;
    
    -- Get number of rows affected
    GET DIAGNOSTICS rows_updated = ROW_COUNT;
    
    -- Return number of rows updated (1 = success, 0 = failed/insufficient stock)
    RETURN rows_updated;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- Triggers for Automatic Timestamp Updates
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger to produk table
CREATE TRIGGER update_produk_updated_at
    BEFORE UPDATE ON produk
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Apply trigger to pelanggan table
CREATE TRIGGER update_pelanggan_updated_at
    BEFORE UPDATE ON pelanggan
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- Sample Data (Optional - for testing)
-- ============================================================================

-- Insert sample products
INSERT INTO produk (nama_produk, harga, stok, kategori) VALUES
('Laptop Dell Inspiron 15', 8500000, 10, 'Elektronik'),
('Mouse Wireless Logitech', 150000, 50, 'Elektronik'),
('Keyboard Mechanical RGB', 750000, 25, 'Elektronik'),
('Kopi Arabika 250g', 75000, 100, 'Makanan & Minuman'),
('Teh Hijau Premium', 50000, 80, 'Makanan & Minuman')
ON CONFLICT DO NOTHING;

-- Insert sample customers
INSERT INTO pelanggan (pelanggan_id, nama_pelanggan, email) VALUES
('CUST-20260207000001-A1B2', 'Budi Santoso', 'budi@email.com'),
('CUST-20260207000002-C3D4', 'Siti Aminah', 'siti@email.com'),
('CUST-20260207000003-E5F6', 'Ahmad Wijaya', 'ahmad@email.com')
ON CONFLICT DO NOTHING;

-- ============================================================================
-- Useful Queries for Monitoring
-- ============================================================================

-- View all products with low stock (< 10 units)
-- SELECT * FROM produk WHERE stok < 10 ORDER BY stok ASC;

-- View recent stock movements
-- SELECT 
--     sl.log_id,
--     p.nama_produk,
--     sl.jumlah_perubahan,
--     sl.tipe_aksi,
--     sl.keterangan,
--     sl.waktu
-- FROM stok_log sl
-- JOIN produk p ON sl.produk_id = p.produk_id
-- ORDER BY sl.waktu DESC
-- LIMIT 50;

-- View transaction details with line items
-- SELECT 
--     t.transaksi_id,
--     t.tanggal_transaksi,
--     p.nama_pelanggan,
--     ti.nama_produk,
--     ti.harga_satuan,
--     ti.jumlah,
--     ti.subtotal,
--     t.total_bayar
-- FROM transaksi t
-- JOIN pelanggan p ON t.pelanggan_id = p.pelanggan_id
-- JOIN transaksi_item ti ON t.transaksi_id = ti.transaksi_id
-- ORDER BY t.tanggal_transaksi DESC;

-- View revenue by product
-- SELECT 
--     ti.nama_produk,
--     COUNT(*) as jumlah_terjual,
--     SUM(ti.jumlah) as total_unit,
--     SUM(ti.subtotal) as total_pendapatan
-- FROM transaksi_item ti
-- GROUP BY ti.nama_produk
-- ORDER BY total_pendapatan DESC;
