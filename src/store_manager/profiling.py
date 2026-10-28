import cProfile
import pstats
import tracemalloc
import numpy as np
from .repository import ProductRepository
from .analytics import (
    calculate_total_stock_value_baseline,
    reprice_products_baseline,
)

def profile_cpu_and_bottlenecks():
    print("=== ПРОФІЛЮВАННЯ ЦИКЛІВ ТА ВИЗНАЧЕННЯ BOTTLENECK (cProfile) ===")
    products = ProductRepository.generate_sample_data(count=100_000)
    prices = [p.price for p in products[:10_000]]
    
    profiler = cProfile.Profile()
    profiler.enable()
    calculate_total_stock_value_baseline(products)
    reprice_products_baseline(prices)
    profiler.disable()
    
    stats = pstats.Stats(profiler)
    stats.sort_stats("cumulative")
    stats.print_stats(10)

def profile_memory_tracemalloc():
    print("\n=== АНАЛІЗ ВИКОРИСТАННЯ ПАМ'ЯТІ (tracemalloc) ===")
    tracemalloc.start()
    products = ProductRepository.generate_sample_data(count=100_000)
    _, peak_1 = tracemalloc.get_traced_memory()
    print(f"[Python Objects] Кількість: 100k | Пікова пам'ять: {peak_1 / (1024*1024):.2f} MB")
    
    prices = np.array([p.price for p in products], dtype=np.float64)
    quantities = np.array([p.quantity for p in products], dtype=np.int32)
    _, peak_2 = tracemalloc.get_traced_memory()
    print(f"[NumPy Arrays]   Після створення масивів | Пікова пам'ять: {peak_2 / (1024*1024):.2f} MB")
    tracemalloc.stop()

if __name__ == "__main__":
    profile_cpu_and_bottlenecks()
    profile_memory_tracemalloc()