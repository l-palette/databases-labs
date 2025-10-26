# Блок 1: Проектирование БД
## 1.1. Сущности и связи

### Сущность клиент
> Хранит информацию о клиентах. PK: ClientID.

Сlient
- `ID` (PRIMARY KEY) - INT, тк уникальный идентификатор, целое число.
- `Name` - VARCHAR(100), тк 100 символов хватит для имени клиента
- `PhoneNumber` - VARCHAR(20), тк 20 символов точно хватит для номера телефона
- `Username` - VARCHAR(16), тк имя пользователя не должно быть длинным
- `Password` - VARCHAR(128), тк 128 это длина SHA-512 в hex

### Сущность заказ
> Хранит заказы с датой и статусом. PK: OrderID. FK: CustomerID → Customers

Order
- `ID` (PRIMARY KEY) - INT, тк уникальный идентификатор, целое число.
- `ClientID` - INT, тк внешний ключ на Client(ID)
- `Date` - DATETIME, так как дата и время заказа
- `Status` - ENUM('Completed', 'Cancelled', 'Processing'), тк других значений быть не должно

### Элементы заказа
> Разбивает заказы на товары (многие-ко-многим). PK: (OrderID, ProductID). FK: OrderID → Orders, ProductID → Products.

OrderItem
- `ID` (PRIMARY KEY) - INT, тк уникальный идентификатор, целое число.
- `ProductID` - INT, тк внешний ключ на Product(ID)
- `Quantity` - INT, тк количество товаров
- `OrderID` - INT, тк внешний ключ на Order(ID)

### Категории товаров
> Хранит информацию о категориях. PK: CategoryID.

Category
- `ID` (PRIMARY KEY) - INT, тк уникальный идентификатор, целое число.
- `Name` - VARCHAR(100), тк 100 символов хватит для категории товара

### Товар - категория
> Хранит связь категории и товара. Много ко многим.

ProductCategory
- `ID`(PRIMARY KEY) - INT, тк уникальный идентификатор, целое число
- `ProductID` - INT, тк внешний ключ на Product(ID)
- `CategoryID` - INT, тк внешний ключ на Category(ID)

### Товары
> Хранит товары с категорией и ценой. PK: ProductID

Product
- `ID` (PRIMARY KEY) - INT, тк уникальный идентификатор, целое число.
- `Name` - VARCHAR(100), тк 100 символов хватит для названия товара
- `Description` - VARCHAR(255), тк описание не должно быть сильно большим
- `Grams` - NUMERIC(6,2), тк нецелое число
- `Calories` - NUMERIC(6,2), тк нецелое число
- `Proteins` - NUMERIC(5,2), тк нецелое число
- `Fats` - NUMERIC(5,2), тк нецелое число
- `Carbs` - NUMERIC(5,2), тк нецелое число
- `Ingredients` - TEXT, тк нельзя ограничить по длине
- `UnitPrice` - NUMERIC(10,2), тк цена с двумя знаками после запятой

Также добавлю ограничения:

- `client.phoneNumber` - UNIQUE, NOT NULL - тк нужен для регистрации
- `client.username` - UNIQUE, NOT NULL - тк нужен для регистрации
- `client.password` - NOT NULL - тк нужен для регистрации
- `category.name` - UNIQUE, NOT NULL - тк не нужны две одинаковые или пустые категории товаров
- `product.unit_price` - NOT NULL - тк цена не может быть нулевой
- `order.date` - TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, время заказа если не указано, то текущее
- `order_item.quantity` - INT NOT NULL CHECK (quantity > 0) - тк количество должно быть больше нуля
- `order_item` - UNIQUE (order_id, product_id) - тк если несколько товаров, то нужно увеличивать кол-во

## 1.2. Скрипт инициализации
> Будем работать в PostgreSQL

```sql
-- Создание последовательностей
CREATE SEQUENCE IF NOT EXISTS client_id_seq START WITH 1;
CREATE SEQUENCE IF NOT EXISTS order_id_seq START WITH 1;
CREATE SEQUENCE IF NOT EXISTS category_id_seq START WITH 1;
CREATE SEQUENCE IF NOT EXISTS product_id_seq START WITH 1;
CREATE SEQUENCE IF NOT EXISTS order_item_id_seq START WITH 1;
CREATE SEQUENCE IF NOT EXISTS product_category_id_seq START WITH 1;

-- Создание типов
CREATE TYPE ENUM_STATUS AS ENUM ('Completed', 'Cancelled', 'Processing');

-- Создание таблицы клиентов
CREATE TABLE client (
    id INT PRIMARY KEY DEFAULT nextval('client_id_seq'),
    name VARCHAR(100),
    phone_number VARCHAR(20) NOT NULL UNIQUE,
    username VARCHAR(16) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);

-- Создание таблицы категорий
CREATE TABLE category (
    id INT PRIMARY KEY DEFAULT nextval('category_id_seq'),
    name VARCHAR(100) NOT NULL UNIQUE,
);

-- Создание таблицы товаров
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

-- Создание таблицы связи товаров и категорий
CREATE TABLE product_category (
    id INT PRIMARY KEY DEFAULT nextval('product_category_id_seq'),
    product_id INT NOT NULL,
    category_id INT NOT NULL,
    FOREIGN KEY (product_id) REFERENCES product(id),
    FOREIGN KEY (category_id) REFERENCES category(id),
    UNIQUE (product_id, category_id)
);

-- Создание таблицы заказов
CREATE TABLE "order" (
    id INT PRIMARY KEY DEFAULT nextval('order_id_seq'),
    client_id INT NOT NULL,
    date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status ENUM_STATUS,
    FOREIGN KEY (client_id) REFERENCES client(id)
);

-- Создание таблицы элементов заказа
CREATE TABLE order_item (
    id INT PRIMARY KEY DEFAULT nextval('order_item_id_seq'),
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL CHECK (quantity > 0),
    FOREIGN KEY (order_id) REFERENCES "order"(id),
    FOREIGN KEY (product_id) REFERENCES product(id),
    UNIQUE (order_id, product_id)
);

-- Добавление индексов для улучшения производительности
CREATE INDEX idx_product_category_product ON product_category(product_id);
CREATE INDEX idx_product_category_category ON product_category(category_id);
CREATE INDEX idx_order_item_order ON order_item(order_id);
CREATE INDEX idx_order_item_product ON order_item(product_id);
CREATE INDEX idx_order_client ON "order"(client_id);
```

## 1.3. SQL-запросы
Для написания запросов необходимо поднять базу данных и заполнить ее значениями. Заполнение значениями будет описано в 
блоке 2, а инициализация БД здесь.
```bash
services:
  db:
    image: postgres
    container_name: db_shop_container
    ports:
      - "5435:5432"
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
      POSTGRES_DB: db_shop
      PGDATA: /var/lib/postgresql/data/pgdata
    volumes:
      - ./postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    restart: unless-stopped
```

```bash
docker exec -it db_shop_container /bin/bash
  psql -U user -d db_shop
```

1) Вывести топ-5 самых продаваемых товаров по количеству за весь период.
```sql
SELECT 
    p.id AS product_id, 
    p.name AS product_name, 
    SUM(oi.quantity) AS total_quantity
FROM 
    product p
JOIN 
    order_item oi ON p.id = oi.product_id
GROUP BY 
    p.id, p.name
ORDER BY 
    total_quantity DESC
LIMIT 5; 
```
2) Рассчитать ежемесячную выручку магазина за последний год.
```sql
SELECT 
    DATE_TRUNC('month', o.date) AS month,
    ROUND(SUM(p.unit_price * oi.quantity), 2) AS monthly_revenue
FROM 
    "order" o
JOIN 
    order_item oi ON o.id = oi.order_id
JOIN 
    product p ON oi.product_id = p.id
WHERE 
    o.date >= DATE_TRUNC('year', CURRENT_DATE - INTERVAL '1 year')
GROUP BY 
    month
ORDER BY 
    month;
```
3) Найти клиента, сделавшего самый дорогой заказ за всё время.
```sql
WITH order_totals AS (
    SELECT 
        o.id AS order_id,
        o.client_id,
        c.name AS client_name,
        SUM(p.unit_price * oi.quantity) AS total_order_value
    FROM 
        "order" o
    JOIN 
        order_item oi ON o.id = oi.order_id
    JOIN 
        product p ON oi.product_id = p.id
    JOIN 
        client c ON o.client_id = c.id
    GROUP BY 
        o.id, o.client_id, c.name
)
SELECT 
    client_id, 
    client_name, 
    MAX(total_order_value) AS max_order_value
FROM 
    order_totals
ORDER BY 
    max_order_value DESC
LIMIT 1;
```
4) Определить категорию товаров с самой высокой средней ценой заказа.
```sql
WITH category_order_values AS (
    SELECT 
        c.id AS category_id,
        c.name AS category_name,
        AVG(p.unit_price * oi.quantity) AS avg_order_value
    FROM 
        category c
    JOIN 
        product p ON c.id = p.category_id
    JOIN 
        order_item oi ON p.id = oi.product_id
    JOIN 
        "order" o ON oi.order_id = o.id
    GROUP BY 
        c.id, c.name
)
SELECT 
    category_id, 
    category_name, 
    ROUND(avg_order_value, 2) AS average_order_value
FROM 
    category_order_values
ORDER BY 
    average_order_value DESC
LIMIT 1;
```
5) Посчитать процент отмененных заказов (Status = 'Cancelled') от общего числа.
```sql
WITH total_orders AS (
    SELECT COUNT(*) AS total 
    FROM "order"
),
cancelled_orders AS (
    SELECT COUNT(*) AS cancelled 
    FROM "order" 
    WHERE status = 'Cancelled'
)
SELECT 
    ROUND(cancelled * 100.0 / total, 2) AS cancelled_percentage
FROM 
    total_orders, cancelled_orders;
```
# Блок 2: Загрузка данных в БД
## 2.1. Генерация исходных данных
- `clients.csv`: clientName, phoneNumber, username, password
```bash
Лобова Татьяна Викторовна | +7(982)980-81-30 | tatianalobova | e90901a8e9ab0aaad99cbf489540e331dcfe97e6f9fd7d4679270d4681d659f44cca2aae1e796c3704b29680cf73e841db73aac51d845766d66f1b35975a5369
Anna Emily Smith | +44 20 7123 4567 | emilysmith | 740f622cf44efddb688b0936e7eca686be6e4d73e1ce2ca00fc8e48130bf1d825159c26e728b942795d59ac5f445005cd155175f559f132f40ed6e5ff20a51cc
```

- `product.csv`: productName, productDescription, grams, calories, proteins, fats, carbs, ingredients, unit_price, categoryName
```bash
Чизбургер с говяжьей котлетой и плавленым сыром «Грабли» | Классический бургер с говяжьей котлетой, ломтиком сыра чеддер и маринованными огурцами в мягкой булочке с кунжутом. В составе есть лук и фирменный соус на основе майонеза и горчицы. | 125 | 264 | 9.4 | 14.3 | 24.3 | - | 299 |Фастфуд
Макароны с сырным соусом Mac&Cheese Карбонара с беконом | Макароны с сырным соусом и беконом быстро готовятся с молоком и сливочным маслом. Их можно разделить на две порции или съесть за раз | 143 | 12.4 | 4.7 | 64.8 | Макаронные изделия (группа А высший сорт): мука из твёрдой пшеницы (дурум) для макаронных изделий высшего сорта, вода питьевая. Соус «Сырный Карбонара с беконом» быстрого приготовления: сырный продукт сухой (сыр с м. д. жиры в сухом веществе 50%, мальтодекстрин, эмульгирующая соль (Е339Н), соль, бекон сушёный, гидролизат соевого белка, натуральные ароматизаторы, перец черный, белый. | 107 | Макароны, крупы и мука; Популярное  
```

- `orders.csv`: clientName, orderDate, status, totalAmount, products
```bash
Лобова Татьяна | 2025-03-15 | Completed | 406 | Чизбургер с говяжьей котлетой и плавленым сыром «Грабли»; Макароны с сырным соусом Mac&Cheese Карбонара с беконом 
Anna Emily Smith | 2025-03-16 | | 107 | Макароны с сырным соусом Mac&Cheese Карбонара с беконом 
```

## 2.2. Нормализация данных
- Очистка данных от дубликатов
- Обработка пропусков в поле Category (заменить на значение 'Other').
- Преобразование поля Price к числовому типу, удалив нечисловые символы.
- Проверка поля Status на допустимость значений (только 'Completed', 'Cancelled', 'Processing'). Недопустимые значения 
заменить на 'Processing'.

## 2.3. Вывод
Объясните, какие аномалии устраняет проведенная вами очистка данных.

 
# Блок 3: Проектирование хранилища и визуализация (5 баллов)
Задание:

1) Спроектируйте упрощенную схему хранилища данных (Data Warehouse) по принципу «звезда» для анализа продаж. Опишите 
таблицу фактов и таблицы измерений.

2) Напишите SQL-запрос, который подготавливает витрину данных для построения дашборда: «Выручка и количество заказов по 
категориям товаров и месяцам».

3) Постройте эту визуализацию (график или диаграмму) с помощью любого инструмента (Excel, Google Data Studio, Power BI,
Python matplotlib) и сделайте краткий вывод по результатам.

---
