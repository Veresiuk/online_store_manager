import unittest
import numpy as np
from src.store_manager.models import Product
from src.store_manager.analytics import (
    calculate_total_stock_value_baseline,
    calculate_total_stock_value_numpy,
    calculate_category_stats_cached,
    invalidate_category_stats_cache,
    reprice_products_baseline,
    _internal_cached_stats,
)
from src.store_manager.parallel import (
    reprice_products_threads,
    reprice_products_processes,
    concurrent_stock_update_locked,
)

class TestStoreManager(unittest.TestCase):
    def setUp(self):
        self.sample_products = [
            Product(id=1, name="Смартфон", category="Електроніка", price=1000.0, quantity=5),
            Product(id=2, name="Ноутбук", category="Електроніка", price=2500.0, quantity=2),
            Product(id=3, name="Футболка", category="Одяг та взуття", price=50.0, quantity=20),
        ]

    def test_stock_value_consistency(self):
        baseline_val = calculate_total_stock_value_baseline(self.sample_products)
        prices = np.array([p.price for p in self.sample_products], dtype=np.float64)
        quantities = np.array([p.quantity for p in self.sample_products], dtype=np.int32)
        numpy_val = calculate_total_stock_value_numpy(prices, quantities)
        self.assertAlmostEqual(baseline_val, numpy_val, places=2)
        self.assertEqual(baseline_val, 1000.0*5 + 2500.0*2 + 50.0*20)

    def test_parallel_reprice_correctness(self):
        prices = [100.0, 250.0, 500.0]
        sequential = reprice_products_baseline(prices)
        threaded = reprice_products_threads(prices, workers=2)
        multiprocessed = reprice_products_processes(prices, workers=2)
        
        self.assertEqual(sequential, threaded)
        self.assertEqual(sequential, multiprocessed)

    def test_caching_and_invalidation(self):
        invalidate_category_stats_cache()
        # Перший виклик - miss
        res1 = calculate_category_stats_cached(self.sample_products, "Електроніка")
        info1 = _internal_cached_stats.cache_info()
        self.assertEqual(info1.misses, 1)
        
        # Другий виклик - hit
        res2 = calculate_category_stats_cached(self.sample_products, "Електроніка")
        info2 = _internal_cached_stats.cache_info()
        self.assertEqual(info2.hits, 1)
        self.assertEqual(res1, res2)

        # Інвалідація
        invalidate_category_stats_cache()
        res3 = calculate_category_stats_cached(self.sample_products, "Електроніка")
        info3 = _internal_cached_stats.cache_info()
        self.assertEqual(info3.currsize, 1)

    def test_synchronization_lock(self):
        threads = 10
        ops = 500
        expected = threads * ops
        locked_result = concurrent_stock_update_locked(threads_count=threads, operations_per_thread=ops)
        self.assertEqual(locked_result, expected)

if __name__ == "__main__":
    unittest.main()