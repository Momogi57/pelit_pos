-- ============================================================================
-- PelitPos Enterprise Edition - Database Schema v4.0
-- Normalized structure with PPN tracking and audit trail
-- ============================================================================

-- Drop old/deprecated tables if they exist
DROP TABLE IF EXISTS Detail_transaksi CASCADE;
DROP TABLE IF EXISTS Inventaris CASCADE;

-- ============================================================================
-- CORE TABLES
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

-- Table: transaksi (Transaction Headers) - WITH PPN COLUMN
CREATE TABLE IF NOT EXISTS transaksi (
    transaksi_id VARCHAR(50) PRIMARY KEY,
    pelanggan_id VARCHAR(50) REFERENCES pelanggan(pelanggan_id) ON DELETE SET NULL,
    subtotal DECIMAL(15, 2) NOT NULL DEFAULT 0,
    ppn DECIMAL(15, 2) NOT NULL DEFAULT 0,  -- NEW: PPN 11% stored permanently
    diskon DECIMAL(15, 2) DEFAULT 0,
    total_bayar DECIMAL(15, 2) NOT NULL,
    tanggal_transaksi TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table: transaksi_item (Transaction Line Items with Price Snapshots)
CREATE TABLE IF NOT EXISTS transaksi_item (
    item_id SERIAL PRIMARY KEY,
    transaksi_id VARCHAR(50) REFERENCES transaksi(transaksi_id) ON DELETE CASCADE,
    produk_id INTEGER REFERENCES produk(produk_id) ON DELETE SET NULL,
    nama_produk VARCHAR(255) NOT NULL,
    harga_satuan DECIMAL(15, 2) NOT NULL,  -- Price snapshot
    jumlah INTEGER NOT NULL,
    subtotal DECIMAL(15, 2) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table: stok_log (Stock Movement Audit Trail)
CREATE TABLE IF NOT EXISTS stok_log (
    log_id SERIAL PRIMARY KEY,
    produk_id INTEGER REFERENCES produk(produk_id) ON DELETE CASCADE,
    jumlah_perubahan INTEGER NOT NULL,
    tipe_aksi VARCHAR(50) NOT NULL,
    keterangan TEXT,
    waktu TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_transaksi_tanggal ON transaksi(tanggal_transaksi DESC);
CREATE INDEX IF NOT EXISTS idx_transaksi_pelanggan ON transaksi(pelanggan_id);
CREATE INDEX IF NOT EXISTS idx_transaksi_item_transaksi ON transaksi_item(transaksi_id);
CREATE INDEX IF NOT EXISTS idx_transaksi_item_produk ON transaksi_item(produk_id);
CREATE INDEX IF NOT EXISTS idx_stok_log_produk ON stok_log(produk_id);
CREATE INDEX IF NOT EXISTS idx_stok_log_waktu ON stok_log(waktu DESC);

-- ============================================================================
-- ATOMIC STOCK FUNCTION
-- ============================================================================

CREATE OR REPLACE FUNCTION atomic_stock_deduct(
    p_product_id INTEGER,
    p_quantity INTEGER
)
RETURNS INTEGER AS $$
DECLARE
    rows_updated INTEGER;
BEGIN
    UPDATE produk
    SET 
        stok = stok - p_quantity,
        updated_at = NOW()
    WHERE 
        produk_id = p_product_id
        AND stok >= p_quantity;
    
    GET DIAGNOSTICS rows_updated = ROW_COUNT;
    RETURN rows_updated;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- TRIGGERS
-- ============================================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS update_produk_updated_at ON produk;
CREATE TRIGGER update_produk_updated_at
    BEFORE UPDATE ON produk
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_pelanggan_updated_at ON pelanggan;
CREATE TRIGGER update_pelanggan_updated_at
    BEFORE UPDATE ON pelanggan
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- MIGRATION: Add PPN column to existing transaksi table (if upgrading)
-- ============================================================================

-- Check if ppn column exists, if not add it
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'transaksi' AND column_name = 'ppn'
    ) THEN
        ALTER TABLE transaksi ADD COLUMN ppn DECIMAL(15, 2) NOT NULL DEFAULT 0;
    END IF;
    
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'transaksi' AND column_name = 'subtotal'
    ) THEN
        ALTER TABLE transaksi ADD COLUMN subtotal DECIMAL(15, 2) NOT NULL DEFAULT 0;
    END IF;
END $$;

-- ============================================================================
-- SAMPLE DATA
-- ============================================================================

INSERT INTO produk (nama_produk, harga, stok, kategori) VALUES
('Laptop Dell Inspiron 15', 8500000, 10, 'Elektronik'),
('Mouse Wireless Logitech', 150000, 50, 'Elektronik'),
('Keyboard Mechanical RGB', 750000, 25, 'Elektronik'),
('Lenovo Thinkpad', 3700000, 15, 'Elektronik'),
('Redmi 9c', 1000000, 30, 'Elektronik')
ON CONFLICT DO NOTHING;

INSERT INTO pelanggan (pelanggan_id, nama_pelanggan, email) VALUES
('CUST-GENERAL', 'Pelanggan Umum', 'umum@pelitpos.com'),
('CUST-20260207000001-A1B2', 'Budi Santoso', 'budi@email.com'),
('CUST-20260207000002-C3D4', 'Siti Aminah', 'siti@email.com')
ON CONFLICT DO NOTHING;

-- ============================================================================
-- USEFUL MONITORING QUERIES
-- ============================================================================

-- View transactions with PPN breakdown
COMMENT ON COLUMN transaksi.subtotal IS 'Subtotal sebelum PPN dan diskon';
COMMENT ON COLUMN transaksi.ppn IS 'PPN 11% yang dihitung dari subtotal';
COMMENT ON COLUMN transaksi.diskon IS 'Diskon yang diberikan';
COMMENT ON COLUMN transaksi.total_bayar IS 'Total final (subtotal + ppn - diskon)';

-- Query: Transaction details with PPN
-- SELECT 
--     t.transaksi_id,
--     t.tanggal_transaksi,
--     pel.nama_pelanggan,
--     t.subtotal,
--     t.ppn,
--     t.diskon,
--     t.total_bayar
-- FROM transaksi t
-- JOIN pelanggan pel ON t.pelanggan_id = pel.pelanggan_id
-- ORDER BY t.tanggal_transaksi DESC;

-- Query: Revenue analysis with tax
-- SELECT 
--     DATE(tanggal_transaksi) as tanggal,
--     COUNT(*) as jumlah_transaksi,
--     SUM(subtotal) as total_subtotal,
--     SUM(ppn) as total_ppn,
--     SUM(diskon) as total_diskon,
--     SUM(total_bayar) as total_pendapatan
-- FROM transaksi
-- GROUP BY DATE(tanggal_transaksi)
-- ORDER BY tanggal DESC;
