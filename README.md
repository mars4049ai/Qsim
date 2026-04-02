# Qsim

Библиотека Python для симуляции квантовых коммуникаций и квантовой памяти.

Реализует:
- протокол квантового распределения ключей **BB84** (с симуляцией перехватчика);
- шифрование сообщений на основе квантового ключа (XOR + SHA-256);
- хранение данных в квантовых осцилляторах (**кудиты**, QuTiP);
- моделирование деградации квантовой памяти (уравнение **Линдблада**);
- визуализацию волновой функции **2D гармонического осциллятора**.

---

## Установка

```bash
pip install -r requirements.txt
```

Для установки как пакета (из папки, содержащей `Qsim/`):

```bash
pip install -e ./Qsim
```

---

## Структура проекта

```
Qsim/
├── __init__.py      -- экспорт классов библиотеки
├── qsim.py          -- классы Qsim и QuantumMemoryServer
├── net.py           -- класс RealisticQuantumMemory
├── setup.py         -- метаданные пакета
├── requirements.txt -- зависимости
├── README.md        -- описание библиотеки
└── annotation.txt   -- аннотация библиотеки
```

---

## Классы

### `Qsim`

Основной класс симулятора квантового распределения ключей.

| Параметр | Тип | Описание |
|---|---|---|
| `num_bits` | `int` | Количество кубитов для генерации ключа (по умолчанию 32) |
| `use_quantum_memory` | `bool` | Включить квантовую память в демонстрацию |
| `default_eve_active` | `bool` | Активировать перехватчика по умолчанию |

Основные методы:

| Метод | Описание |
|---|---|
| `simulate_qkd_bb84(num_bits, eve_active)` | Симуляция BB84, возвращает `(qber, key_alice, key_bob)` |
| `find_secure_channel(num_bits, ...)` | Итеративный поиск канала с QBER ниже порога |
| `encrypt_message(plaintext, key)` | Зашифровать строку, вернуть Base64 |
| `decrypt_message(base64_msg, key)` | Расшифровать Base64-строку |
| `classical_message_exchange(key, ...)` | Обмен сообщениями с демонстрацией атаки Евы |
| `display_2d_harmonic_oscillator_animation(...)` | 2D-анимация гармонического осциллятора |
| `run_demonstration(...)` | Полная демонстрация всех функций |

---

### `QuantumMemoryServer`

Сервер квантовой памяти на кудитах.

| Параметр | Тип | Описание |
|---|---|---|
| `num_qudit_levels` | `int` | Число уровней Фока каждого кудита (по умолчанию 10) |
| `memory_capacity_qudits` | `int` | Общее число слотов памяти (по умолчанию 100) |

Основные методы:

| Метод | Описание |
|---|---|
| `store_client_data(client_id, base64_msg)` | Сохранить зашифрованные данные клиента |
| `retrieve_client_data(client_id)` | Извлечь данные клиента из памяти |

---

### `RealisticQuantumMemory`

Модель деградации квантовой памяти.

| Параметр | Тип | Описание |
|---|---|---|
| `memory_capacity_qudits` | `int` | Число слотов памяти |
| `num_qudit_levels` | `int` | Уровни Фока |
| `kappa` | `float` | Скорость декогеренции (1/с), по умолчанию 2.5 |

Основные методы:

| Метод | Описание |
|---|---|
| `store_data(data_bytes)` | Загрузить байты в слоты памяти |
| `simulate_decay(total_time, steps, mode)` | Симуляция Линдблада, режимы: `"none"`, `"protected"`, `"ideal"` |
| `generate_visualizations()` | Генерация GIF-анимаций и сравнительного графика |

---

## Примеры использования

### 1. Квантовое распределение ключей (BB84)

```python
from qsim import Qsim

sim = Qsim(num_bits=32)

# Установить безопасный канал (без перехватчика)
key = sim.find_secure_channel(num_bits=32, eve_active=False)
print(f"Ключ: {key[:20]}...")

# Тот же канал с перехватчиком -- обычно не устанавливается
sim.eve_name = "Ева"
key_with_eve = sim.find_secure_channel(num_bits=32, eve_active=True, max_attempts=5)
if not key_with_eve:
    print("Перехватчик обнаружен, канал не установлен.")
```

### 2. Шифрование и расшифрование сообщений

```python
from qsim import Qsim

sim = Qsim(num_bits=32)
key = sim.find_secure_channel(num_bits=32, eve_active=False)

encrypted = sim.encrypt_message("Секретное сообщение", key)
print(f"Зашифровано: {encrypted}")

decrypted = sim.decrypt_message(encrypted, key)
print(f"Расшифровано: {decrypted}")
```

### 3. Обмен сообщениями с демонстрацией MITM-атаки

```python
from qsim import Qsim

def alice_gen():
    yield "Привет, Боб!"
    yield "Кодовое слово: 'Квант'"

def bob_gen():
    yield "Получил. Подтверждаю: 'Квант'."

sim = Qsim(num_bits=32)
sim.alice_name = "Алиса"
sim.bob_name = "Боб"
sim.eve_name = "Ева"

key = sim.find_secure_channel(num_bits=32, eve_active=False)
sim.classical_message_exchange(key, alice_gen, bob_gen)
```

### 4. Хранение данных в квантовой памяти

```python
from qsim import Qsim, QuantumMemoryServer

sim = Qsim(num_bits=32)
key = sim.find_secure_channel(num_bits=32, eve_active=False)

server = QuantumMemoryServer(num_qudit_levels=10, memory_capacity_qudits=300)

# Боб шифрует и сохраняет пароль
encrypted = sim.encrypt_message("МойПароль123", key)
server.store_client_data("Боб", encrypted)

# Боб извлекает и расшифровывает пароль
retrieved = server.retrieve_client_data("Боб")
print(sim.decrypt_message(retrieved, key))
```

### 5. Моделирование деградации квантовой памяти

```python
from qsim import RealisticQuantumMemory
import numpy as np

mem = RealisticQuantumMemory(num_qudit_levels=10, kappa=2.5)
mem.store_data([9, 3, 7])

# Симуляция без защиты
times, states = mem.simulate_decay(total_time=1.0, steps=50, mode="none")

# Симуляция с кодами Бозе
times, states_prot = mem.simulate_decay(total_time=1.0, steps=50, mode="protected")

# Генерация GIF-анимаций и сравнительного графика
mem.generate_visualizations()
```

### 6. Полная демонстрация

```python
from qsim import Qsim

def alice_messages():
    yield "Привет, Боб! Это Алиса."
    yield "Как насчет обеда завтра?"

def bob_messages():
    yield "Привет, Алиса! Давай пообедаем."

sim = Qsim(num_bits=32, use_quantum_memory=True, default_eve_active=True)
sim.run_demonstration(
    alice_name="Алиса",
    bob_name="Боб",
    eve_name="Ева",
    alice_msg_gen=alice_messages,
    bob_msg_gen=bob_messages,
)
```

---

## Требования

- Python >= 3.9
- numpy >= 1.24
- scipy >= 1.10
- matplotlib >= 3.7
- qutip >= 5.0
- qiskit >= 1.0
- qiskit-aer >= 0.14

---

## Лицензия

MIT License
