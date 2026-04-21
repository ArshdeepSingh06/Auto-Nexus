DELETE FROM sales;
DELETE FROM services;
DELETE FROM vehicles;
DELETE FROM customers;

ALTER TABLE sales AUTO_INCREMENT = 1;
ALTER TABLE services AUTO_INCREMENT = 1;
ALTER TABLE vehicles AUTO_INCREMENT = 1;
ALTER TABLE customers AUTO_INCREMENT = 1;

INSERT INTO customers (name, phone, email) VALUES

('Aditya', '9999999999', 'aditya@gmail.com');

INSERT INTO vehicles (vin, brand, model, price, status) VALUES

('VIN001', 'Tesla', 'Model S', 9000000, 'Available');