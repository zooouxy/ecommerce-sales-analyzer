-- ============================================
-- AI Ecommerce Analyst
-- Database Schema
-- ============================================

-- 创建客户表
-- 一个客户可以对应多个订单
CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY,
    country TEXT
); 

-- 创建商品表
-- 一个商品可以出现在多个订单明细中
CREATE TABLE products (
    stock_code TEXT PRIMARY KEY,
    description TEXT
);

-- ============================================
-- 订单表
-- 一个客户可以有多个订单
-- 一个订单可以包含多个订单商品明细
-- ============================================

CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY,      -- 数据库内部的订单编号
    invoice_no TEXT NOT NULL UNIQUE,
    invoice_date DATETIME NOT NULL,
    customer_id INTEGER,
    
    FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id)
);

-- ============================================
-- 订单商品明细表
-- 一条记录代表一个订单中的一个商品明细
-- ============================================

CREATE TABLE order_items (
    transaction_id INTEGER PRIMARY KEY,
    order_id INTEGER NOT NULL,
    stock_code TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    sales DECIMAL(12, 2) NOT NULL,

    FOREIGN KEY (order_id)
        REFERENCES orders(order_id),

    FOREIGN KEY (stock_code)
        REFERENCES products(stock_code)
);

-- ============================================
-- Indexes
-- 为常用查询字段建立索引
-- ============================================

-- 按客户查询订单
CREATE INDEX idx_orders_customer_id
ON orders(customer_id);

-- 按订单日期查询订单
CREATE INDEX idx_orders_invoice_date
ON orders(invoice_date);

-- 按订单查询商品明细
CREATE INDEX idx_order_items_order_id
ON order_items(order_id);

-- 按商品查询订单明细
CREATE INDEX idx_order_items_stock_code
ON order_items(stock_code);