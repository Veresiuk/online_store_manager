import os
import csv
import time
import numpy as np
from src.store_manager.repository import ProductRepository
from src.store_manager.analytics import (
    calculate_total_stock_value_baseline,
    calculate_total_stock_value_numpy,
    calculate_category_stats_cached,
    invalidate_category_stats_cache,
    reprice_products_baseline,
)
from src.store_manager.parallel import (
    reprice_products_threads,
    reprice_products_processes,
)

def run_benchmarks():
    print("=" * 70)
    print("   БЕНЧМАРК ОПТИМІЗАЦІЇ ТА ПАРАЛЕЛЬНОСТІ (ВАРІАНТ 3: ІНТЕРНЕТ-МАГАЗИН)")
    print("=" * 70)

    results = []
    dataset_sizes = [10_000, 50_000, 100_000]
    repeats = 5

    # 1. Дослідження агрегації складських залишків (Baseline vs NumPy)
    print("\n[Експеримент 1] Розрахунок загальної вартості складу (Stock Value)")
    for size in dataset_sizes:
        products = ProductRepository.generate_sample_data(size)
        prices = np.array([p.price for p in products], dtype=np.float64)
        quantities = np.array([p.quantity for p in products], dtype=np.int32)

        # Baseline
        base_times = []
        for _ in range(repeats):
            t0 = time.perf_counter()
            calculate_total_stock_value_baseline(products)
            base_times.append(time.perf_counter() - t0)
        mean_base = sum(base_times) / repeats

        # NumPy
        np_times = []
        for _ in range(repeats):
            t0 = time.perf_counter()
            calculate_total_stock_value_numpy(prices, quantities)
            np_times.append(time.perf_counter() - t0)
        mean_np = sum(np_times) / repeats

        speedup_np = mean_base / mean_np if mean_np > 0 else 0
        print(f"Dataset: {size:7d} | Python: {mean_base:.6f}s | NumPy: {mean_np:.6f}s | Speedup: {speedup_np:6.2f}x")
        
        results.append({
            "Experiment": "Stock Value Aggregation",
            "Dataset_Size": size,
            "Method": "Python Baseline",
            "Workers": 1,
            "Mean_Time_s": round(mean_base, 6),
            "Speedup": 1.0,
        })
        results.append({
            "Experiment": "Stock Value Aggregation",
            "Dataset_Size": size,
            "Method": "NumPy Vectorized",
            "Workers": "-",
            "Mean_Time_s": round(mean_np, 6),
            "Speedup": round(speedup_np, 2),
        })

    # 2. Дослідження CPU-bound динамічного ціноутворення (Baseline vs Threads vs Processes)
    print("\n[Експеримент 2] Динамічний перерахунок цін (CPU-bound workload, 10,000 позицій)")
    sample_prices = [p.price for p in ProductRepository.generate_sample_data(10_000)]
    
    # Sequential
    seq_times = []
    for _ in range(3):
        t0 = time.perf_counter()
        reprice_products_baseline(sample_prices)
        seq_times.append(time.perf_counter() - t0)
    mean_seq = sum(seq_times) / len(seq_times)
    print(f"Sequential Baseline: {mean_seq:.4f}s")
    results.append({
        "Experiment": "Heavy Repricing",
        "Dataset_Size": 10_000,
        "Method": "Sequential Baseline",
        "Workers": 1,
        "Mean_Time_s": round(mean_seq, 6),
        "Speedup": 1.0,
    })

    worker_configs = [1, 2, 4, 8]
    for w in worker_configs:
        # Threads
        t_times = []
        for _ in range(3):
            t0 = time.perf_counter()
            reprice_products_threads(sample_prices, workers=w)
            t_times.append(time.perf_counter() - t0)
        mean_thread = sum(t_times) / len(t_times)
        sp_thread = mean_seq / mean_thread

        # Processes
        p_times = []
        for _ in range(3):
            t0 = time.perf_counter()
            reprice_products_processes(sample_prices, workers=w)
            p_times.append(time.perf_counter() - t0)
        mean_proc = sum(p_times) / len(p_times)
        sp_proc = mean_seq / mean_proc

        print(f"Workers: {w:2d} | Threads: {mean_thread:.4f}s (Sp: {sp_thread:.2f}x) | Processes: {mean_proc:.4f}s (Sp: {sp_proc:.2f}x)")
        results.append({
            "Experiment": "Heavy Repricing",
            "Dataset_Size": 10_000,
            "Method": "ThreadPoolExecutor",
            "Workers": w,
            "Mean_Time_s": round(mean_thread, 6),
            "Speedup": round(sp_thread, 2),
        })
        results.append({
            "Experiment": "Heavy Repricing",
            "Dataset_Size": 10_000,
            "Method": "ProcessPoolExecutor",
            "Workers": w,
            "Mean_Time_s": round(mean_proc, 6),
            "Speedup": round(sp_proc, 2),
        })

    # 3. Дослідження Caching (Cold vs Warm Cache)
    print("\n[Експеримент 3] Кешування статистики категорій (LRU Cache)")
    cat_products = ProductRepository.generate_sample_data(100_000)
    invalidate_category_stats_cache()
    
    t0 = time.perf_counter()
    calculate_category_stats_cached(cat_products, "Електроніка")
    cold_time = time.perf_counter() - t0

    t0 = time.perf_counter()
    calculate_category_stats_cached(cat_products, "Електроніка")
    warm_time = time.perf_counter() - t0

    speedup_cache = cold_time / warm_time if warm_time > 0 else float('inf')
    print(f"Cold Cache (Miss): {cold_time:.6f}s | Warm Cache (Hit): {warm_time:.8f}s | Speedup: {speedup_cache:.1f}x")

    results.append({
        "Experiment": "Category Statistics Caching",
        "Dataset_Size": 100_000,
        "Method": "Cold Cache (Miss)",
        "Workers": "-",
        "Mean_Time_s": round(cold_time, 6),
        "Speedup": 1.0,
    })
    results.append({
        "Experiment": "Category Statistics Caching",
        "Dataset_Size": 100_000,
        "Method": "Warm Cache (Hit)",
        "Workers": "-",
        "Mean_Time_s": round(warm_time, 8),
        "Speedup": round(speedup_cache, 2),
    })

    # Збереження результатів у CSV
    csv_file = "benchmarks/results/benchmark_results.csv"
    os.makedirs(os.path.dirname(csv_file), exist_ok=True)
    with open(csv_file, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["Experiment", "Dataset_Size", "Method", "Workers", "Mean_Time_s", "Speedup"])
        writer.writeheader()
        writer.writerows(results)
    print(f"\n[Успішно] Результати збережено у {csv_file}")

if __name__ == "__main__":
    run_benchmarks()