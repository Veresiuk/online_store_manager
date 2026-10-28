from dataclasses import dataclass

@dataclass(slots=True, frozen=True)
class Product:
    id: int
    name: str
    category: str
    price: float
    quantity: int

    @property
    def total_value(self) -> float:
        return self.price * self.quantity