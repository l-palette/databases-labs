import pandas as pd
from sqlalchemy import create_engine, text
import os
import matplotlib.pyplot as plt

DATABASE_URL = "postgresql://user:password@localhost:5435/db_shop"
CSV_DIR = "initial-data"
engine = create_engine(DATABASE_URL)

with engine.connect() as connection:
    result = connection.execute(text("SELECT 1"))
    print("Connection successful:", result.fetchone())

query = "SELECT * FROM mart_category_monthly_sales;"
df = pd.read_sql(query, engine)

csv_path = os.path.join(CSV_DIR, "mart_category_monthly_sales.csv")
df.to_csv(csv_path, index=False)
print(f"Data exported to {csv_path}. Shape: {df.shape}")

# Группировка для графиков
pivot_orders = df.pivot(index='month_name', columns='category_name', values='total_orders')
pivot_revenue = df.pivot(index='month_name', columns='category_name', values='total_revenue')
# График 1: Количество заказов по категориям и месяцам
plt.figure(figsize=(12, 6))
pivot_orders.plot(kind='bar', ax=plt.gca(), title='Количество заказов по категориям и месяцам (2025)')
plt.ylabel('Количество заказов')
plt.xlabel('Месяц')
plt.legend(title='Категория')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
# График 2: Выручка по категориям и месяцам
plt.figure(figsize=(12, 6))
pivot_revenue.plot(kind='bar', ax=plt.gca(), title='Выручка по категориям и месяцам (2024)')
plt.ylabel('Выручка (руб.)')
plt.xlabel('Месяц')
plt.legend(title='Категория')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
