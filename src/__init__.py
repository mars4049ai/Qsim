"""
Qsim -- библиотека симуляции квантовых коммуникаций и квантовой памяти.

Экспортируемые классы:
    Qsim                  -- симулятор BB84 QKD, шифрование, обмен сообщениями,
                             2D-анимация гармонического осциллятора.
    QuantumMemoryServer   -- сервер хранения данных в квантовых осцилляторах (кудиты).
    RealisticQuantumMemory-- модель деградации квантовой памяти (уравнение Линдблада).

Пример быстрого старта::

    from qsim import Qsim

    sim = Qsim(num_bits=32)
    key = sim.find_secure_channel(num_bits=32, eve_active=False)
    encrypted = sim.encrypt_message("Привет!", key)
    print(sim.decrypt_message(encrypted, key))
"""

from .qsim import Qsim, QuantumMemoryServer
from .net import RealisticQuantumMemory

__all__ = ['Qsim', 'QuantumMemoryServer', 'RealisticQuantumMemory']
__version__ = '1.0.0'
__author__ = 'Qsim Contributors'
