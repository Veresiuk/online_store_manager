import random
from typing import List
from .models import Product

CATEGORIES = [
    "Електроніка",
    "Побутова техніка",
    "Одяг та взуття",
    "Книги",
    "Спорт і відпочинок",
    "Дім і сад",
    "Косметика",
    "Автотовари"
]

class ProductRepository:
    def __init__(self) -> None:
        self.products: List[Product] = []

    def add_product(self, product: Product) -> None:
        self.products.append(product)

    def get_all(self) -> List[Product]:
        return self.products

    def get_by_category(self, category: str) -> List[Product]:
        return [p for p in self.products if p.category == category]

    def find_most_expensive(self) -> Product | None:
        if not self.products:
            return None
        return max(self.products, key=lambda p: p.price)

    @staticmethod
    def generate_sample_data(count: int, seed: int = 42) -> List[Product]:
        random.seed(seed)
        data = []
        for i in range(count):
            cat = random.choice(CATEGORIES)
            price = round(random.uniform(10.0, 5000.0), 2)
            quantity = random.randint(1, 150)
            data.append(Product(id=i, name=f"Товар_{i}", category=cat, price=price, quantity=quantity))
        return data