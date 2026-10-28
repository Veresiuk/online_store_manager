from __future__ import annotations
import math
from functools import lru_cache
from typing import List, Dict, Any, Tuple
import numpy as np
from .models import Product

def calculate_total_stock_value_baseline(products: List[Product]) -> float:
    """Baseline: підрахунок загальної вартості через звичайний цикл Python."""
    total = 0.0
    for p in products:
        total += p.price * p.quantity
    return total

def calculate_total_stock_value_numpy(prices: np.ndarray, quantities: np.ndarray) -> float:
    """Векторизований підрахунок вартості складських залишків за допомогою NumPy."""
    return float(np.sum(prices * quantities))

def heavy_price_adjustment(price: float) -> float:
    """CPU-bound функція динамічного ціноутворення."""
    val = price
    for _ in range(80):
        val = math.sqrt(abs(val) + 1.0) + math.sin(val) ** 2 + math.cos(val) ** 2
    return round(val * 1.05, 2)

def reprice_products_baseline(prices: List[float]) -> List[float]:
    """Послідовний перерахунок цін (CPU-bound baseline)."""
    return [heavy_price_adjustment(p) for p in prices]

def calculate_category_stats_baseline(products: List[Product], category: str) -> Dict[str, Any]:
    """Розрахунок агрегованої статистики для категорії без кешування."""
    filtered = [p for p in products if p.category == category]
    if not filtered:
        return {"category": category, "count": 0, "avg_price": 0.0, "total_value": 0.0, "max_price": 0.0}
    
    prices = [p.price for p in filtered]
    total_val = sum(p.price * p.quantity for p in filtered)
    return {
        "category": category,
        "count": len(filtered),
        "avg_price": sum(prices) / len(prices),
        "total_value": total_val,
        "max_price": max(prices)
    }

# Глобальна версія для Cache Invalidation
_CACHE_VERSION: int = 1

def invalidate_category_stats_cache() -> None:
    """Інкремент версії та повне очищення кешу при зміні каталогу."""
    global _CACHE_VERSION
    _CACHE_VERSION += 1
    _internal_cached_stats.cache_clear()

@lru_cache(maxsize=128)
def _internal_cached_stats(category: str, version: int, products_tuple: Tuple[Product, ...]) -> Dict[str, Any]:
    filtered = [p for p in products_tuple if p.category == category]
    if not filtered:
        return {"category": category, "count": 0, "avg_price": 0.0, "total_value": 0.0, "max_price": 0.0}
    prices = [p.price for p in filtered]
    total_val = sum(p.price * p.quantity for p in filtered)
    return {
        "category": category,
        "count": len(filtered),
        "avg_price": sum(prices) / len(prices),
        "total_value": total_val,
        "max_price": max(prices)
    }

def calculate_category_stats_cached(products: List[Product], category: str) -> Dict[str, Any]:
    """Кешована версія статистики за категорією з LRU-кешем та підтримкою інвалідації."""
    return _internal_cached_stats(category, _CACHE_VERSION, tuple(products))