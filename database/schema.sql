CREATE DATABASE autonexus;

USE autonexus;

CREATE TABLE vehicles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vin VARCHAR(50) UNIQUE,
    brand VARCHAR(50),
    model VARCHAR(50),
    price FLOAT,
    status VARCHAR(20)
);

CREATE TABLE customers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    phone VARCHAR(15),
    email VARCHAR(100)
);

CREATE TABLE sales (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vehicle_id INT,
    customer_id INT,
    price FLOAT,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(id),
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);

CREATE TABLE services (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT,
    vehicle_id INT,
    service_type VARCHAR(50),
    status VARCHAR(20),
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE,
    password VARCHAR(255),
    role VARCHAR(20)
);

CREATE TABLE rentals (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vehicle_id INT,
    customer_id INT,
    start_date DATE,
    end_date DATE,
    status VARCHAR(20)
);

CREATE TABLE service_jobs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vehicle_id INT,
    customer_id INT,
    type VARCHAR(50),
    status VARCHAR(20),
    cost FLOAT
);

CREATE TABLE invoices (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ref_id INT,
    type VARCHAR(20),
    amount FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO users (username, password, role) VALUES
('admin', 'admin123', 'Admin'),
('sales', 'sales123', 'Sales'),
('tech', 'tech123', 'Technician');