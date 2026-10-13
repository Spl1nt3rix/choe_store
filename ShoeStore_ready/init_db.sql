-- Схема базы shoe_store. Выполнять в пустой базе shoe_store.
CREATE TABLE roles(role_id SERIAL PRIMARY KEY, role_name VARCHAR(30) NOT NULL UNIQUE);
CREATE TABLE categories(category_id SERIAL PRIMARY KEY, category_name VARCHAR(100) NOT NULL UNIQUE);
CREATE TABLE manufacturers(manufacturer_id SERIAL PRIMARY KEY, manufacturer_name VARCHAR(150) NOT NULL UNIQUE);
CREATE TABLE suppliers(supplier_id SERIAL PRIMARY KEY, supplier_name VARCHAR(150) NOT NULL UNIQUE);
CREATE TABLE order_statuses(status_id SERIAL PRIMARY KEY, status_name VARCHAR(50) NOT NULL UNIQUE);
CREATE TABLE users(user_id SERIAL PRIMARY KEY, login VARCHAR(50) NOT NULL UNIQUE, password_hash VARCHAR(255) NOT NULL, full_name VARCHAR(150) NOT NULL, role_id INTEGER NOT NULL REFERENCES roles(role_id));
CREATE TABLE products(product_id SERIAL PRIMARY KEY, product_name VARCHAR(200) NOT NULL, category_id INTEGER NOT NULL REFERENCES categories(category_id), manufacturer_id INTEGER NOT NULL REFERENCES manufacturers(manufacturer_id), supplier_id INTEGER NOT NULL REFERENCES suppliers(supplier_id), price NUMERIC(10,2) NOT NULL CHECK(price>=0), quantity_in_stock INTEGER NOT NULL DEFAULT 0 CHECK(quantity_in_stock>=0), discount_percent NUMERIC(5,2) NOT NULL DEFAULT 0 CHECK(discount_percent BETWEEN 0 AND 100), image_path VARCHAR(255));
CREATE TABLE orders(order_id SERIAL PRIMARY KEY, article VARCHAR(50) NOT NULL UNIQUE, product_id INTEGER NOT NULL REFERENCES products(product_id), client_id INTEGER NOT NULL REFERENCES users(user_id), status_id INTEGER NOT NULL REFERENCES order_statuses(status_id), pickup_address VARCHAR(255) NOT NULL, order_date DATE NOT NULL DEFAULT CURRENT_DATE, issue_date DATE, CHECK(issue_date IS NULL OR issue_date>=order_date));
INSERT INTO roles(role_name) VALUES ('client'),('manager'),('administrator');
INSERT INTO categories(category_name) VALUES ('Кроссовки'),('Ботинки'),('Туфли'),('Сандалии');
INSERT INTO manufacturers(manufacturer_name) VALUES ('Nike'),('Adidas'),('Reebok'),('Puma'),('Timberland');
INSERT INTO suppliers(supplier_name) VALUES ('ООО Спортопт'),('ИП Иванов'),('ТД Обувь Плюс');
INSERT INTO order_statuses(status_name) VALUES ('новый'),('в обработке'),('выдан'),('отменён');
-- Демо-аккаунты. Сразу после выполнения запустите set_test_passwords.py, чтобы заменить заглушки bcrypt-хешами.
INSERT INTO users(login,password_hash,full_name,role_id) VALUES
('client','$2b$12$placeholder_not_a_real_hash_xxxxxxxxxxxxxxxx','Иван Иванов',(SELECT role_id FROM roles WHERE role_name='client')),
('petrova','$2b$12$placeholder_not_a_real_hash_xxxxxxxxxxxxxxxx','Анна Петрова',(SELECT role_id FROM roles WHERE role_name='client')),
('manager','$2b$12$placeholder_not_a_real_hash_xxxxxxxxxxxxxxxx','Сергей Сидоров',(SELECT role_id FROM roles WHERE role_name='manager')),
('admin','$2b$12$placeholder_not_a_real_hash_xxxxxxxxxxxxxxxx','Администратор',(SELECT role_id FROM roles WHERE role_name='administrator'));
INSERT INTO products(product_name,category_id,manufacturer_id,supplier_id,price,quantity_in_stock,discount_percent) VALUES
('Air Max 90',(SELECT category_id FROM categories WHERE category_name='Кроссовки'),(SELECT manufacturer_id FROM manufacturers WHERE manufacturer_name='Nike'),(SELECT supplier_id FROM suppliers WHERE supplier_name='ООО Спортопт'),12999,12,10),
('Ultraboost 22',(SELECT category_id FROM categories WHERE category_name='Кроссовки'),(SELECT manufacturer_id FROM manufacturers WHERE manufacturer_name='Adidas'),(SELECT supplier_id FROM suppliers WHERE supplier_name='ИП Иванов'),14999,0,5),
('Classic Leather',(SELECT category_id FROM categories WHERE category_name='Кроссовки'),(SELECT manufacturer_id FROM manufacturers WHERE manufacturer_name='Reebok'),(SELECT supplier_id FROM suppliers WHERE supplier_name='ТД Обувь Плюс'),7999,8,0),
('Timberland Style Boot',(SELECT category_id FROM categories WHERE category_name='Ботинки'),(SELECT manufacturer_id FROM manufacturers WHERE manufacturer_name='Timberland'),(SELECT supplier_id FROM suppliers WHERE supplier_name='ООО Спортопт'),18999,4,15),
('Loafer Classic',(SELECT category_id FROM categories WHERE category_name='Туфли'),(SELECT manufacturer_id FROM manufacturers WHERE manufacturer_name='Puma'),(SELECT supplier_id FROM suppliers WHERE supplier_name='ИП Иванов'),6999,6,0);
INSERT INTO orders(article,product_id,client_id,status_id,pickup_address,order_date,issue_date) VALUES
('ORD-0001',(SELECT product_id FROM products WHERE product_name='Air Max 90'),(SELECT user_id FROM users WHERE login='client'),(SELECT status_id FROM order_statuses WHERE status_name='выдан'),'Москва, ул. Примерная, 1',CURRENT_DATE-5,CURRENT_DATE-2),
('ORD-0002',(SELECT product_id FROM products WHERE product_name='Ultraboost 22'),(SELECT user_id FROM users WHERE login='petrova'),(SELECT status_id FROM order_statuses WHERE status_name='в обработке'),'Москва, ул. Центральная, 10',CURRENT_DATE-2,NULL),
('ORD-0003',(SELECT product_id FROM products WHERE product_name='Classic Leather'),(SELECT user_id FROM users WHERE login='client'),(SELECT status_id FROM order_statuses WHERE status_name='новый'),'Москва, ул. Примерная, 5',CURRENT_DATE,NULL);
