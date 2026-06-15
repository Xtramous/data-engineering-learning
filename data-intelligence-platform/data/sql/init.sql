-- Create schemas
CREATE SCHEMA IF NOT EXISTS public;
CREATE SCHEMA IF NOT EXISTS metadata;

-- Customer Dimension Table
CREATE TABLE IF NOT EXISTS public.customer_dim (
    customer_id SERIAL PRIMARY KEY,
    customer_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(20),
    city VARCHAR(100),
    country VARCHAR(100),
    signup_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Product Dimension Table
CREATE TABLE IF NOT EXISTS public.product_dim (
    product_id SERIAL PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    subcategory VARCHAR(100),
    price DECIMAL(10, 2),
    cost DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sales Fact Table
CREATE TABLE IF NOT EXISTS public.sales_fact (
    sales_id BIGSERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES public.customer_dim(customer_id),
    product_id INTEGER REFERENCES public.product_dim(product_id),
    sales_date DATE NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    total_amount DECIMAL(15, 2) NOT NULL,
    discount_amount DECIMAL(10, 2) DEFAULT 0,
    tax_amount DECIMAL(10, 2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Order Fact Table
CREATE TABLE IF NOT EXISTS public.order_fact (
    order_id BIGSERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES public.customer_dim(customer_id),
    order_date DATE NOT NULL,
    delivery_date DATE,
    order_status VARCHAR(50),
    total_order_value DECIMAL(15, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Inventory Fact Table
CREATE TABLE IF NOT EXISTS public.inventory_fact (
    inventory_id BIGSERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES public.product_dim(product_id),
    warehouse_location VARCHAR(100),
    quantity_on_hand INTEGER,
    quantity_reserved INTEGER,
    reorder_level INTEGER,
    measurement_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_customer_email ON public.customer_dim(email);
CREATE INDEX IF NOT EXISTS idx_sales_date ON public.sales_fact(sales_date);
CREATE INDEX IF NOT EXISTS idx_sales_customer ON public.sales_fact(customer_id);
CREATE INDEX IF NOT EXISTS idx_sales_product ON public.sales_fact(product_id);
CREATE INDEX IF NOT EXISTS idx_order_date ON public.order_fact(order_date);
CREATE INDEX IF NOT EXISTS idx_order_customer ON public.order_fact(customer_id);
CREATE INDEX IF NOT EXISTS idx_inventory_product ON public.inventory_fact(product_id);

-- Table metadata table (optional, for additional metadata)
CREATE TABLE IF NOT EXISTS metadata.table_metadata (
    table_id SERIAL PRIMARY KEY,
    table_name VARCHAR(255) NOT NULL UNIQUE,
    schema_name VARCHAR(100),
    owner VARCHAR(255),
    description TEXT,
    row_count BIGINT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Column metadata table (optional)
CREATE TABLE IF NOT EXISTS metadata.column_metadata (
    column_id SERIAL PRIMARY KEY,
    table_id INTEGER REFERENCES metadata.table_metadata(table_id),
    column_name VARCHAR(255),
    column_type VARCHAR(100),
    is_nullable BOOLEAN DEFAULT TRUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert initial metadata
INSERT INTO metadata.table_metadata (table_name, schema_name, owner, description, row_count)
VALUES
    ('customer_dim', 'public', 'analytics-team', 'Customer dimension table with customer details and signup information', 10000),
    ('product_dim', 'public', 'analytics-team', 'Product dimension table with product details and pricing', 5000),
    ('sales_fact', 'public', 'analytics-team', 'Sales fact table with transaction-level details', 500000),
    ('order_fact', 'public', 'analytics-team', 'Order fact table with order-level information', 100000),
    ('inventory_fact', 'public', 'analytics-team', 'Inventory fact table with warehouse stock levels', 50000)
ON CONFLICT (table_name) DO NOTHING;

COMMIT;
