-- 商品表
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    stock INT NOT NULL,
    image_url TEXT
);

-- 购物车表
CREATE TABLE IF NOT EXISTS cart_items (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(50) NOT NULL,
    product_id INT REFERENCES products(id),
    quantity INT NOT NULL,
    UNIQUE(session_id, product_id)
);

-- 订单主表
CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(50) NOT NULL,
    total DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'pending'
);

-- 订单明细表
CREATE TABLE IF NOT EXISTS order_items (
    id SERIAL PRIMARY KEY,
    order_id INT REFERENCES orders(id),
    product_id INT REFERENCES products(id),
    quantity INT,
    price DECIMAL(10,2)
);

-- 插入示例商品
INSERT INTO products (name, price, stock, image_url) VALUES
('iPhone 15', 799.00, 10, 'https://via.placeholder.com/150'),
('Samsung Galaxy S24', 699.00, 15, 'https://via.placeholder.com/150'),
('Sony WH-1000XM5', 399.00, 30, 'https://via.placeholder.com/150')
ON CONFLICT (id) DO NOTHING;