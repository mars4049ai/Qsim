"""
net.py -- Модуль моделирования деградации квантовой памяти.

Содержит класс:
    RealisticQuantumMemory -- симуляция затухания квантовых состояний на основе
                              уравнения Линдблада (мастер-уравнения Линдблада-Горини-
                              Косаковски-Сударшана), три режима защиты данных,
                              генерация 2D-анимаций и сравнительных графиков.
"""

import numpy as np
import qutip
from scipy.special import hermite
from math import factorial
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import os


class RealisticQuantumMemory:
    """
    Реалистичная модель квантовой памяти с симуляцией деградации состояний.

    Квантовые состояния хранятся в виде состояний Фока квантовых осцилляторов.
    Деградация моделируется через мастер-уравнение Линдблада (QuTiP mesolve)
    с оператором распада a (оператор уничтожения).

    Поддерживаются три режима симуляции:
        "none"      -- без защиты (скорость затухания kappa).
        "protected" -- с кодами Бозе (скорость затухания kappa / 15).
        "ideal"     -- идеальная память (без затухания).

    Параметры:
        memory_capacity_qudits (int) : количество слотов памяти (осцилляторов).
        num_qudit_levels (int)       : число уровней Фока каждого осциллятора.
        kappa (float)                : скорость декогеренции (1/с).
    """

    def __init__(self, memory_capacity_qudits=100, num_qudit_levels=10, kappa=2.5):
        self.num_qudit_levels = num_qudit_levels
        self.memory_capacity = memory_capacity_qudits
        self.kappa = kappa
        self.memory_slots = [qutip.fock(num_qudit_levels, 0)
                             for _ in range(memory_capacity_qudits)]
        self.current_fill = 0

    def store_data(self, data_bytes):
        """
        Загрузить байтовые данные в слоты квантовой памяти.

        Каждый байт преобразуется в уровень Фока соответствующего осциллятора
        (по модулю num_qudit_levels).

        Параметры:
            data_bytes (bytes | list[int]) : входные данные (до memory_capacity байт).
        """
        for i, b in enumerate(data_bytes[:self.memory_capacity]):
            level = int(b % self.num_qudit_levels)
            self.memory_slots[i] = qutip.fock(self.num_qudit_levels, level)
        self.current_fill = len(data_bytes)

    def simulate_decay(self, total_time=1.0, steps=100, mode="none"):
        """
        Симулировать временную эволюцию квантового состояния с учётом декогеренции.

        Начальное состояние -- суперпозиция |0> и |2>. Гамильтониан:
        H = hbar * omega * a^dag * a,  omega = 2*pi*2 Гц.

        Параметры:
            total_time (float) : полное время симуляции (секунды).
            steps (int)        : количество временных шагов.
            mode (str)         : режим защиты: "none", "protected" или "ideal".

        Возвращает:
            tuple: (times, states)
                times (np.ndarray)       -- временные точки.
                states (list[Qobj])      -- список квантовых состояний rho(t).
        """
        a = qutip.destroy(self.num_qudit_levels)
        omega = 2.0 * np.pi * 2.0
        H = omega * a.dag() * a

        if mode == "ideal":
            c_ops = []
        elif mode == "protected":
            c_ops = [np.sqrt(self.kappa / 15.0) * a]
        else:
            c_ops = [np.sqrt(self.kappa) * a]

        times = np.linspace(0, total_time, steps)
        psi0 = (qutip.fock(self.num_qudit_levels, 0) + qutip.fock(self.num_qudit_levels, 2)).unit()
        result = qutip.mesolve(H, psi0, times, c_ops, [])
        return times, result.states

    def generate_visualizations(self):
        """
        Сгенерировать 2D-анимации деградации (GIF) и сводный сравнительный график.

        Создаёт три GIF-файла (по одному для каждого режима) и отображает
        итоговый график сохранности данных во времени для всех трёх режимов.

        Выходные файлы:
            memory_decay_2d_no_protection.gif
            memory_decay_2d_with_protection.gif
            memory_decay_2d_ideal.gif
        """
        sim_time = 2.0
        display_duration = 12.0
        fps = 20
        total_frames = int(display_duration * fps)
        grid_pts = 60
        x_vec = np.linspace(-5, 5, grid_pts)
        wf_basis = [self._get_psi_n_x(n, x_vec) for n in range(self.num_qudit_levels)]

        modes = [
            ("none",      "Без защиты",                 "no_protection"),
            ("protected", "С защитой",                  "with_protection"),
            ("ideal",     "Идеальное (без деградации)", "ideal"),
        ]

        for mode_key, label_rus, file_suffix in modes:
            print(f"Генерация 2D динамики: {label_rus}...")
            times, states = self.simulate_decay(
                total_time=sim_time, steps=total_frames, mode=mode_key)

            fig, ax = plt.subplots(figsize=(6, 5))
            ax.set_aspect('equal')
            ax.set_xlim(-5, 5)
            ax.set_ylim(-5, 5)
            ax.set_title(f"2D Динамика: {label_rus}")

            im = ax.imshow(np.zeros((grid_pts, grid_pts)), origin='lower',
                           extent=[-5, 5, -5, 5], cmap='viridis', vmin=0, vmax=0.25)
            time_text = ax.text(0.05, 0.92, '', transform=ax.transAxes,
                                color='white', fontweight='bold')

            def init():
                im.set_array(np.zeros((grid_pts, grid_pts)))
                return [im, time_text]

            def animate(i, _states=states, _times=times):
                rho = (_states[i].full() if _states[i].type == 'oper'
                       else qutip.ket2dm(_states[i]).full())
                pdf_2d = np.zeros((grid_pts, grid_pts), dtype=float)
                for n in range(self.num_qudit_levels):
                    for m in range(self.num_qudit_levels):
                        if abs(rho[n, m]) > 1e-4:
                            term = rho[n, m] * np.outer(wf_basis[n], wf_basis[m])
                            pdf_2d += term.real
                im.set_array(pdf_2d)
                time_text.set_text(f"Время: {_times[i]:.3f} с")
                return [im, time_text]

            ani = FuncAnimation(fig, animate, init_func=init,
                                frames=total_frames, blit=True)
            filename = f"memory_decay_2d_{file_suffix}.gif"
            ani.save(filename, writer='pillow', fps=fps)
            plt.close(fig)
            print(f"Файл сохранен: {filename}")

        print("Генерация итогового графика...")
        t_plot = np.linspace(0, sim_time, 100)
        plt.figure(figsize=(10, 5))
        plt.plot(t_plot, np.exp(-self.kappa * t_plot) * 100,
                 'r-', label='Без защиты', lw=2)
        plt.plot(t_plot, np.exp(-(self.kappa / 15.0) * t_plot) * 100,
                 'g-', label='С защитой (Коды Бозе)', lw=2)
        plt.plot(t_plot, np.ones_like(t_plot) * 100,
                 'b--', label='Идеальное', lw=2)
        plt.axhline(y=10, color='gray', linestyle='--', label='Порог потери данных')
        plt.title("Сравнение сохранности данных")
        plt.xlabel("Время (секунды)")
        plt.ylabel("Целостность данных (%)")
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.show()

    def _get_psi_n_x(self, n, x):
        """
        Вычислить волновую функцию n-го состояния квантового гармонического осциллятора.

        Параметры:
            n (int)        : квантовое число (n >= 0).
            x (np.ndarray) : массив координат.

        Возвращает:
            np.ndarray : значения psi_n(x).
        """
        norm = 1.0 / np.sqrt(2**n * factorial(n)) * (np.pi**(-0.25))
        return norm * np.exp(-x**2 / 2.0) * hermite(n)(x)


# ----------------------------------------------------------------------
# Точка входа для автономного запуска / демонстрации
# ----------------------------------------------------------------------

if __name__ == '__main__':
    memory = RealisticQuantumMemory(num_qudit_levels=10)
    memory.store_data([9])
    memory.generate_visualizations()
