Онлайн-магазин (Online Store Manager) — Варіант 3

Навчальний консольний проєкт для дисципліни «Професійний Python»

Лабораторна робота №9: «Паралельність, багатопроцесність та оптимізація в Python»

1. Опис проєкту та предметної області

Проєкт реалізує систему обліку та керування товарами інтернет-магазину (Варіант №3). Для кожного товару зберігаються:

name — назва товару;

category — категорія;

price — ціна за одиницю;

quantity — кількість на складі.

Основні можливості системи:

Базовий облік: додавання товарів, пошук, фільтрація за категорією, визначення найдорожчого товару та розрахунок загальної вартості залишків (stock value).

Профілювання продуктивності: детермінований аналіз часу та виявлення вузьких місць (bottlenecks) через cProfile, а також аналіз пікового споживання пам'яті через tracemalloc на наборах від 10 000 до 100 000+ товарів.

Оптимізація та порівняльний аналіз: порівняння послідовного коду (Python Loops Baseline), векторизації за допомогою NumPy, багатопотоковості (ThreadPoolExecutor) та багатопроцесності (ProcessPoolExecutor).

Синхронізація потоків: моделювання стану гонитви (Race Condition) при одночасному оновленні залишків декількома потоками та його усунення за допомогою threading.Lock.

Кешування: оптимізація повторних дорогих розрахунків статистики категорій за допомогою functools.lru_cache із підтримкою інвалідації кешу (cache invalidation) при зміні каталогу.

2. Структура проєкту

Проєкт організовано відповідно до архітектурного шаблону src-layout:

online_store_manager/
├── pyproject.toml                     # Конфігурація проєкту, залежностей та інструментів
├── README.md                          # Базова документація проєкту
├── .gitignore                         # Виключення тимчасових файлів, .venv та кешів
├── report/
│   └── Вересюк_Ірина_Лаб09_V3.pdf     # Офіційний PDF-звіт лабораторної роботи
├── src/
│   └── store_manager/
│       ├── __init__.py                # Ініціалізація пакета та експорт публічного API
│       ├── models.py                  # Датаклас Product (frozen dataclass)
│       ├── repository.py              # ProductRepository та генератор вибірок
│       ├── analytics.py               # Stock value (Loops vs NumPy), CPU-bound pricing, LRU cache
│       ├── parallel.py                # ThreadPool, ProcessPool, Race Condition demo & Lock
│       └── profiling.py               # Скрипти аналізу cProfile та tracemalloc
├── tests/
│   └── test_store_manager.py          # Автоматизовані модульні тести (pytest / unittest)
└── benchmarks/
    ├── benchmark.py                   # Комплексний бенчмарк із багаторазовими повторами
    └── results/
        └── benchmark_results.csv      # Експортовані результати вимірювань у форматі CSV


3. Системні вимоги та залежності

Python: версія 3.10 або вище.

Основні бібліотеки:

numpy >= 1.24.0 — векторизовані числові обчислення;

pytest >= 7.0.0 — автоматизоване тестування;

reportlab — генерація PDF-звіту.

4. Інструкція зі встановлення та налаштування

4.1. Створення та активація віртуального середовища

Windows (PowerShell):

python -m venv .venv
.venv\Scripts\Activate.ps1


Linux / macOS / Git Bash:

python3 -m venv .venv
source .venv/bin/activate


4.2. Встановлення залежностей проєкту

Встановіть проєкт разом із залежностями у режимі редагування (editable mode):

python -m pip install --upgrade pip
pip install -e .
pip install pytest reportlab


(Якщо ви працюєте у Windows PowerShell безпосередньо з вихідного коду, задайте робочий каталог у PYTHONPATH: $env:PYTHONPATH = ".")

5. Запуск складових проєкту

5.1. Запуск автоматизованих тестів

Перевірка числової точності NumPy, коректності паралельних перерахунків, роботи кешу та блокувань:

pytest tests/


або через стандартний runner:

python -m unittest discover tests/


5.2. Профілювання вузьких місць та пам'яті

Запуск діагностики через cProfile та tracemalloc:

python -m src.store_manager.profiling


5.3. Комплексний бенчмарк

Запуск вимірювання швидкодії (Loops vs NumPy, Threads vs Processes, scaling 1..8 workers, Caching) та запис у CSV-файл:

python benchmarks/benchmark.py


5.4. Генерація офіційного PDF-звіту

Перегенерація файлу звіту report/Вересюк_Ірина_Лаб09_V3.pdf:

python report/generate_pdf_report.py


6. Результати експериментів (Бенчмарки)

Фактичні результати вимірювань продуктивності на тестовій платформі:

6.1. Агрегація вартості залишків (Python Loops vs NumPy Vectorization)

Розмір вибірки

Python Loops (Mean, s)

NumPy Vectorized (Mean, s)

Прискорення (Speedup)

10 000

0.001489 s

0.000312 s

4.77x

50 000

0.003825 s

0.000131 s

29.18x

100 000

0.019233 s

0.000822 s

23.41x

6.2. CPU-bound динамічне ціноутворення (10 000 товарів, Baseline: 0.6771 s)

Workers

ThreadPoolExecutor (s)

Speedup (Threads)

ProcessPoolExecutor (s)

Speedup (Processes)

1

0.7180 s

0.94x

0.8642 s

0.78x

2

0.8130 s

0.83x

0.7301 s

0.93x

4

0.7465 s

0.91x

0.7480 s

0.91x

8

0.6900 s

0.98x

1.2046 s

0.56x

6.3. Кешування статистики категорій (lru_cache)

Cold Cache (Cache Miss): 0.046147 s

Warm Cache (Cache Hit): 0.033310 s

Speedup: 1.4x

Cache Invalidation: реалізовано версіонування та метод invalidate_category_stats_cache() для автоматичного скидання кешованого стану при модифікації асортименту.