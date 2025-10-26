import pandas as pd
from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://user:password@localhost:5435/db_shop"
CSV_DIR = "initial-data"
engine = create_engine(DATABASE_URL)

with engine.connect() as connection:
    result = connection.execute(text("SELECT 1"))
    print("Connection successful:", result.fetchone())

clients_df = pd.read_csv(f'{CSV_DIR}/clients.csv')
products_df = pd.read_csv(f'{CSV_DIR}/product.csv')
orders_df = pd.read_csv(f'{CSV_DIR}/orders.csv')

# 1. Вынесем все уникальные значения из products_df (productName, productDescription, grams, calories, proteins, fats,
# carbs, ingredients, unit_price, categoryName) столбца categoryName в таблицу category, сохраним все id в словарь
# categories
"""
CREATE TABLE category (
    id INT PRIMARY KEY DEFAULT nextval('category_id_seq'),
    name VARCHAR(100) NOT NULL UNIQUE,
);
"""

unique_categories = set()
for category in products_df['categoryName'].unique():
    category = category.strip()
    if category:
        categories_multiple = category.split(";")
        for one_category in categories_multiple:
            one_category = one_category.strip()
            unique_categories.add(one_category)

print(f"Unique categories to be inserted: {unique_categories}")


def insert_categories(unique_categories):
    with engine.connect() as connection:
        transaction = connection.begin()
        try:
            for category in unique_categories:
                print(f"Inserting category: '{category}'")
                try:
                    result = connection.execute(
                        text("INSERT INTO category (name) VALUES (:name) ON CONFLICT (name) DO NOTHING"),
                        {'name': category}
                    )
                    if result.rowcount > 0:
                        print(f"Inserted category: '{category}'")
                    else:
                        print(f"Category '{category}' already exists")
                except Exception as e:
                    print(f"Error inserting category: '{category}'. Error: {e}")
            transaction.commit()
        except Exception as e:
            print(f"Transaction failed: {e}")
            transaction.rollback()


insert_categories(unique_categories)

categories = {}
with engine.connect() as connection:
    print("Categories in database:")
    result = connection.execute(text("SELECT * FROM category"))
    for row in result:
        categories[row[0]] = row[1]

print(f"{categories=}")

# 2. Заполним таблицу clients из clients_df (clientName, phoneNumber, username, password), сохраним все id в словарь
# clients
"""
CREATE TABLE client (
    id INT PRIMARY KEY DEFAULT nextval('client_id_seq'),
    name VARCHAR(100),
    phone_number VARCHAR(20) NOT NULL UNIQUE,
    username VARCHAR(16) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);
"""

# 3. Заполним таблицу product из product_df (productName, productDescription, grams, calories, proteins, fats, carbs,
# ingredients, unit_price, categoryName) всем кроме categoryName. Преобразование поля Price к числовому типу, удалив
# нечисловые символы.
"""
CREATE TABLE product (
    id INT PRIMARY KEY DEFAULT nextval('product_id_seq'),
    name VARCHAR(100),
    description VARCHAR(255),
    grams NUMERIC(6,2), 
    calories NUMERIC(6,2),
    proteins NUMERIC(5,2),
    fats NUMERIC(5,2),
    carbs NUMERIC(5,2),
    ingredients TEXT,
    unit_price NUMERIC(10,2) NOT NULL
);
"""

# 4. Заполним таблицу product_category значениями product_id из таблицы product при заполнении и соответствующим
# category_id из словаря categories
"""
CREATE TABLE product_category (
    id INT PRIMARY KEY DEFAULT nextval('product_category_id_seq'),
    product_id INT NOT NULL,
    category_id INT NOT NULL,
    FOREIGN KEY (product_id) REFERENCES product(id),
    FOREIGN KEY (category_id) REFERENCES category(id),
    UNIQUE (product_id, category_id)
);
"""

# 5. Заполним таблицу order из orders_df(clientName, orderDate, status, totalAmount, products) значениями client_id из
# словаря clients. Проверка поля Status на допустимость значений (только 'Completed', 'Cancelled', 'Processing').
# Недопустимые значения заменить на 'Processing'.
"""
CREATE TABLE "order" (
    id INT PRIMARY KEY DEFAULT nextval('order_id_seq'),
    client_id INT NOT NULL,
    date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status ENUM_STATUS,
    FOREIGN KEY (client_id) REFERENCES client(id)
);
"""
# 6. Используя значение products из orders_df заполним order_item, учитывая, что кол-во товара указано после двоеточия
# "Чизбургер с говяжьей котлетой и плавленым сыром «Грабли»: 1; Макароны с сырным соусом Mac&Cheese Карбонара с беконом:
# 1"
"""
CREATE TABLE order_item (
    id INT PRIMARY KEY DEFAULT nextval('order_item_id_seq'),
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL CHECK (quantity > 0),
    FOREIGN KEY (order_id) REFERENCES "order"(id),
    FOREIGN KEY (product_id) REFERENCES product(id),
    UNIQUE (order_id, product_id)
);
"""
