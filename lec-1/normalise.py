import pandas as pd
from sqlalchemy import create_engine, text
import re

def insert_categories(unique_categories):
    with engine.connect() as connection:
        transaction = connection.begin()
        try:
            inserted = 0
            for category in unique_categories:
                result = connection.execute(
                    text("INSERT INTO category (name) VALUES (:name) ON CONFLICT (name) DO NOTHING"),
                    {'name': category}
                )
                if result.rowcount > 0:
                    inserted += 1
            transaction.commit()
            print(f"Inserted {inserted} new categories (total unique: {len(unique_categories)})")
        except Exception as e:
            print(f"Failed to insert categories: {e}")
            transaction.rollback()


def insert_clients(clients_df) -> dict:
    clients = {}
    with engine.connect() as connection:
        transaction = connection.begin()
        try:
            inserted = 0
            for _, row in clients_df.iterrows():
                client_name = row['clientName'].strip() if pd.notna(row['clientName']) else None
                phone_number = row['phoneNumber'].strip() if pd.notna(row['phoneNumber']) else None
                username = row['username'].strip() if pd.notna(row['username']) else None
                password = row['password'].strip() if pd.notna(row['password']) else None

                if phone_number and username and password:
                    result = connection.execute(
                        text("""
                            INSERT INTO client (name, phone_number, username, password) 
                            VALUES (:name, :phone, :username, :password)
                            ON CONFLICT (username) DO NOTHING
                            RETURNING id, name
                        """),
                        {
                            'name': client_name,
                            'phone': phone_number,
                            'username': username,
                            'password': password
                        }
                    )
                    row_result = result.fetchone()
                    if row_result:
                        clients[client_name] = row_result[0]
                        inserted += 1

            # Получаем всех клиентов для словаря
            result = connection.execute(text("SELECT id, name FROM client"))
            for row in result:
                if row[1]:
                    clients[row[1]] = row[0]

            transaction.commit()
            print(f"Inserted {inserted} new clients (total: {len(clients)})")
        except Exception as e:
            print(f"Failed to insert clients: {e}")
            transaction.rollback()
    print(f"{clients=}")
    return clients


def clean_numeric_field(value):
    if pd.isna(value):
        return None
    cleaned = re.sub(r'[^\d.,]', '', str(value))
    cleaned = cleaned.replace(',', '.')
    try:
        return float(cleaned) if cleaned else None
    except:
        return None


def insert_products(products_df) -> dict:
    products = {}
    with engine.connect() as connection:
        transaction = connection.begin()
        try:
            inserted = 0
            for _, row in products_df.iterrows():
                product_name = row['productName'].strip() if pd.notna(row['productName']) else None

                # Проверяем существование продукта
                existing = connection.execute(
                    text("SELECT id FROM product WHERE name = :name"),
                    {'name': product_name}
                ).fetchone()

                if existing:
                    products[product_name] = existing[0]
                    continue

                description = row['productDescription'].strip() if pd.notna(row['productDescription']) else None
                grams = clean_numeric_field(row['grams'])
                calories = clean_numeric_field(row['calories'])
                proteins = clean_numeric_field(row['proteins'])
                fats = clean_numeric_field(row['fats'])
                carbs = clean_numeric_field(row['carbs'])
                unit_price = clean_numeric_field(row['unit_price'])
                ingredients = row['ingredients'].strip() if pd.notna(row['ingredients']) else None

                if product_name and unit_price is not None:
                    result = connection.execute(
                        text("""
                            INSERT INTO product (name, description, grams, calories, proteins, 
                                               fats, carbs, ingredients, unit_price)
                            VALUES (:name, :desc, :grams, :calories, :proteins, 
                                   :fats, :carbs, :ingredients, :price)
                            ON CONFLICT (name) DO NOTHING
                            RETURNING id
                        """),
                        {
                            'name': product_name,
                            'desc': description,
                            'grams': grams,
                            'calories': calories,
                            'proteins': proteins,
                            'fats': fats,
                            'carbs': carbs,
                            'ingredients': ingredients,
                            'price': unit_price
                        }
                    )
                    product_result = result.fetchone()
                    if product_result:
                        product_id = product_result[0]
                        products[product_name] = product_id
                        inserted += 1

            # Получаем все продукты
            result = connection.execute(text("SELECT id, name FROM product"))
            for row in result:
                products[row[1]] = row[0]

            transaction.commit()
            print(f"Inserted {inserted} new products (total: {len(products)})")
        except Exception as e:
            print(f"Failed to insert products: {e}")
            transaction.rollback()

    print(f"{products=}")
    return products


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

insert_categories(unique_categories)

categories = {}
with engine.connect() as connection:
    print("Categories in database:")
    result = connection.execute(text("SELECT * FROM category"))
    for row in result:
        categories[row[1]] = row[0]

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
clients = insert_clients(clients_df)

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

products = insert_products(products_df)



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
