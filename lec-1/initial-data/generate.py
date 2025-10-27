import csv
import random
import hashlib
import faker
import datetime
from datetime import timedelta


def generate_password(username):
    return hashlib.sha512(username.encode()).hexdigest()


def generate_csv_files():
    fake = faker.Faker(["ru_RU", "en_US"])

    # clients.csv

    is_empty = 1
    clients = []
    with open(f"{CSV_DIR}/clients.csv", "r", newline="", encoding="utf-8") as file:
        reader = csv.reader(file)

        for _ in reader:
            is_empty = 0
            break

    with open(f"{CSV_DIR}/clients.csv", "a", newline="", encoding="utf-8") as file:

        writer = csv.writer(file)
        if is_empty:
            writer.writerow(["clientName", "phoneNumber", "username", "password"])

        used_usernames = set()
        for _ in range(100):
            # Случайный выбор между русским и английским именем
            if random.random() < 0.7:  # 70% русских имен
                full_name = f"{fake.last_name_female()} {fake.first_name_female()} {fake.middle_name_female()}"
                phone = f"+7({random.randint(900, 999)}){random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(10, 99)}"
            else:
                full_name = fake.name()
                phone = f"+44 {random.randint(20, 79)} {random.randint(1000, 9999)} {random.randint(1000, 9999)}"
            clients.append(full_name)
            # Создание уникального username
            base_username = full_name.lower().replace(" ", "").replace("ё", "е")
            username = base_username
            counter = 1
            while username in used_usernames:
                username = f"{base_username}{counter}"
                counter += 1

            used_usernames.add(username)
            password = generate_password(username)

            writer.writerow([full_name, phone, username, password])

    # products.csv

    is_empty = 1

    with open(f"{CSV_DIR}/products.csv", "r", newline="", encoding="utf-8") as file:
        reader = csv.reader(file)

        for _ in reader:
            is_empty = 0
            break

    categories = [
        "Фастфуд",
        "Макароны, крупы и мука",
        "Популярное",
        "Здоровое питание",
        "Десерты",
        "Напитки",
        "Салаты",
        "Горячие блюда",
        "",  # пустая, должна заполниться Other
    ]

    ingredients_list = [
        "Мука пшеничная",
        "Яйца",
        "Молоко",
        "Сахар",
        "Соль",
        "Масло подсолнечное",
        "Сыр",
        "Говядина",
        "Курица",
        "Рис",
        "Макароны",
        "Картофель",
        "Лук",
        "Чеснок",
        "Перец",
        "Помидоры",
        "Огурцы",
        "Зелень",
    ]

    product_names = [
        "Чикенбургер Двойной сыр",
        "Макароны с сыром Пармезан",
        "Цезарь с курицей",
        "Пицца Маргарита",
        "Салат Греческий",
        "Суп-крем грибной",
        "Стейк из лосося",
        "Утиная ножка конфи",
        "Круассан с ветчиной и сыром",
        "Борщ с говядиной",
        "Том-ям с креветками",
        "Спагетти Болоньезе",
        "Ролл Филадельфия",
        "Шашлык из свинины",
        "Тирамису",
        "Карпаччо из говядины",
        "Сырный суп с беконом",
        "Лазанья мясная",
        "Фалафель в пите",
        "Рыба по-средиземноморски",
    ]

    product_descriptions = [
        "Классический бургер с сочной говяжьей котлетой",
        "Нежные макароны с аппетитным сырным соусом",
        "Свежий салат с хрустящими овощами и курицей",
        "Традиционная итальянская пицца с томатным соусом",
        "Легкий и полезный салат с морепродуктами",
        "Нежный суп-крем с ароматными грибами",
        "Сочный стейк из свежего лосося",
        "Изысканная утиная ножка с хрустящей корочкой",
        "Воздушный круассан с аппетитной начинкой",
        "Наваристый борщ с мягкой говядиной",
        "Острый таиландский суп с морепродуктами",
        "Классическая паста с мясным соусом",
        "Популярный роллы с лососем и сливочным сыром",
        "Сочный шашлык из свежей свинины",
        "Нежный итальянский десерт с кофейным вкусом",
        "Тонко нарезанная говядина с оливковым маслом",
        "Насыщенный сырный суп с хрустящим беконом",
        "Аппетитная запеченная лазанья с мясом",
        "Вегетарианская закуска в мягкой пите",
        "Рыбное блюдо в средиземноморском стиле",
    ]
    products_data = []
    for _ in range(len(product_descriptions)):
        product_name = product_names[_]
        product_description = product_descriptions[_]

        grams = str(random.randint(50, 500))
        calories = "{:.1f}".format(random.uniform(50, 500))
        proteins = "{:.1f}".format(random.uniform(1, 30))
        fats = "{:.1f}".format(random.uniform(1, 30))
        carbs = "{:.1f}".format(random.uniform(10, 80))

        num_ingredients = random.randint(3, 7)
        ingredients = " ".join(random.sample(ingredients_list, num_ingredients))

        unit_price = "{:.2f}".format(random.uniform(50, 1000))
        # 15% вероятность неверных символов в цене
        if random.random() < 0.15:
            invalid_patterns = [
                lambda p: f"{p:.2f}$",
                lambda p: f"${p:.2f}",
                lambda p: f"{p:.2f}руб",
                lambda p: f"{p:.0f}ABC",
                lambda p: f"abc{p:.0f}",
                lambda p: f"{p:.2f}#",
                lambda p: f"@{p:.2f}",
                lambda p: f"{p:.1f}*",
                lambda p: f"{p:.2f}!!!",
                lambda p: f"~{p:.0f}~",
                lambda p: f"{p:.2f} рублей",
                lambda p: f"цена: {p:.2f}",
                lambda p: "N/A",
                lambda p: "TBD",
                lambda p: f"{p:.2f}%",
                lambda p: f"({p:.2f})",
                lambda p: f"{p:.2f}+",
                lambda p: f"{p:.2f}/шт",
                lambda p: str(p).replace(".", ","),
            ]
            pattern = random.choice(invalid_patterns)
            unit_price = pattern(float(unit_price))
        else:
            unit_price = "{:.2f}".format(float(unit_price))

        category_name = random.choice(categories)

        product = {
            "productName": product_name,
            "productDescription": product_description,
            "grams": grams,
            "calories": calories,
            "proteins": proteins,
            "fats": fats,
            "carbs": carbs,
            "ingredients": ingredients,
            "unit_price": unit_price,
            "categoryName": category_name,
        }

        products_data.append(product)

    with open(f"{CSV_DIR}/products.csv", "a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "productName",
                "productDescription",
                "grams",
                "calories",
                "proteins",
                "fats",
                "carbs",
                "ingredients",
                "unit_price",
                "categoryName",
            ],
            quoting=csv.QUOTE_ALL,
        )
        if is_empty:
            writer.writeheader()
        writer.writerows(products_data)

    orders_data = []
    statuses = [
        "Completed",
        "Processing",
        "Cancelled",
        "",
    ]  # пустой должен заполниться Processing

    start_date = datetime.date.today() - timedelta(days=90)
    end_date = datetime.date.today() + timedelta(days=30)

    for _ in range(200):
        client_name = random.choice(clients)

        days_between = (end_date - start_date).days
        random_days = random.randint(0, days_between)
        order_date = start_date + timedelta(days=random_days)
        order_date_str = order_date.strftime("%Y-%m-%d")

        status = random.choice(statuses) if random.random() > 0.05 else ""

        num_products = random.randint(1, 5)
        selected_products = random.choices(product_names, k=num_products)

        products_list = []
        total_amount = 0

        product_counts = {}
        for product in selected_products:
            if product in product_counts:
                product_counts[product] += 1
            else:
                product_counts[product] = 1

        for product_name, quantity in product_counts.items():
            products_list.append(f"{product_name}: {quantity}")

            for p in product_names:
                if p == product_name:
                    total_amount += random.randint(1, 1000) * quantity
                    break

        products_str = "; ".join(products_list)
        total_amount = int(total_amount)

        orders_data.append(
            {
                "clientName": client_name,
                "orderDate": order_date_str,
                "status": status,
                "totalAmount": total_amount,
                "products": products_str,
            }
        )

    is_empty = 1
    try:
        with open(f"{CSV_DIR}/orders.csv", "r", newline="", encoding="utf-8") as file:
            reader = csv.reader(file)
            for _ in reader:
                is_empty = 0
                break
    except FileNotFoundError:
        pass

    with open(f"{CSV_DIR}/orders.csv", "a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["clientName", "orderDate", "status", "totalAmount", "products"],
            quoting=csv.QUOTE_ALL,
        )
        if is_empty:
            writer.writeheader()
        writer.writerows(orders_data)


def add_duplicates(file_name):
    data_to_write = []
    with open(f"{CSV_DIR}/{file_name}", "r", newline="", encoding="utf-8") as file:
        reader = csv.reader(file)
        i = 0
        for line in reader:
            if i:
                data_to_write.append(line)
            i += 1
            if i == 10:
                break

    with open(f"{CSV_DIR}/{file_name}", "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerows(data_to_write)


CSV_DIR = "initial-data"

generate_csv_files()
files = ["clients.csv", "orders.csv", "products.csv"]
for file in files:
    add_duplicates(file)
