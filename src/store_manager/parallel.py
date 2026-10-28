from __future__ import annotations
import threading
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from typing import List
from .analytics import heavy_price_adjustment

def reprice_products_threads(prices: List[float], workers: int = 4) -> List[float]:
    """Паралельний перерахунок цін за допомогою ThreadPoolExecutor."""
    with ThreadPoolExecutor(max_workers=workers) as executor:
        return list(executor.map(heavy_price_adjustment, prices))

def reprice_products_processes(prices: List[float], workers: int = 4, chunksize: int = 250) -> List[float]:
    """Багатопроцесний перерахунок цін за допомогою ProcessPoolExecutor."""
    with ProcessPoolExecutor(max_workers=workers) as executor:
        return list(executor.map(heavy_price_adjustment, prices, chunksize=chunksize))

class SharedWarehouseStock:
    def __init__(self, initial_stock: int = 0) -> None:
        self.stock = initial_stock
        self.lock = threading.Lock()

    def update_without_lock(self, delta: int) -> None:
        """Небезпечне оновлення залишків без блокування (Race Condition)."""
        current = self.stock
        self.stock = current + delta

    def update_with_lock(self, delta: int) -> None:
        """Потокобезпечне оновлення залишків із синхронізацією через Lock."""
        with self.lock:
            self.stock += delta

def concurrent_stock_update_race(threads_count: int = 10, operations_per_thread: int = 1000) -> int:
    warehouse = SharedWarehouseStock(0)
    threads = []
    def worker():
        for _ in range(operations_per_thread):
            warehouse.update_without_lock(1)
    for _ in range(threads_count):
        t = threading.Thread(target=worker)
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    return warehouse.stock

def concurrent_stock_update_locked(threads_count: int = 10, operations_per_thread: int = 1000) -> int:
    warehouse = SharedWarehouseStock(0)
    threads = []
    def worker():
        for _ in range(operations_per_thread):
            warehouse.update_with_lock(1)
    for _ in range(threads_count):
        t = threading.Thread(target=worker)
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    return warehouse.stock