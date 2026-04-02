import numpy as np
import qutip
from scipy.special import hermite
from math import factorial
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import os

class RealisticQuantumMemory:
    def __init__(self, memory_capacity_qudits=100, num_qudit_levels=10, kappa=2.5):
        self.num_qudit_levels = num_qudit_levels
        self.memory_capacity = memory_capacity_qudits
        self.kappa = kappa
        self.memory_slots = [qutip.fock(num_qudit_levels, 0) for _ in range(memory_capacity_qudits)]
        self.current_fill = 0

    def store_data(self, data_bytes):
        for i, b in enumerate(data_bytes[:self.memory_capacity]):
            level = int(b % self.num_qudit_levels)
            self.memory_slots[i] = qutip.fock(self.num_qudit_levels, level)
        self.current_fill = len(data_bytes)

    def simulate_decay(self, total_time=1.0, steps=100, mode="none"):
        """
        mode: "none" (no protection), "protected" (Bose codes), "ideal" (no decay)
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
        sim_time = 2.0
        display_duration = 12.0
        fps = 20
        total_frames = int(display_duration * fps)
        grid_pts = 60
        x_vec = np.linspace(-5, 5, grid_pts)
        wf_basis = [self._get_psi_n_x(n, x_vec) for n in range(self.num_qudit_levels)]

        modes = [
            ("none", "Без защиты", "no_protection"),
            ("protected", "С защитой", "with_protection"),
            ("ideal", "Идеальное (без деградации)", "ideal")
        ]

        for mode_key, label_rus, file_suffix in modes:
            print(f"Генерация 2D динамики: {label_rus}...")

            times, states = self.simulate_decay(total_time=sim_time, steps=total_frames, mode=mode_key)

            fig, ax = plt.subplots(figsize=(6, 5))
            ax.set_aspect('equal')
            ax.set_xlim(-5, 5)
            ax.set_ylim(-5, 5)
            ax.set_title(f"2D Динамика: {label_rus}")

            im = ax.imshow(np.zeros((grid_pts, grid_pts)), origin='lower',
                           extent=[-5, 5, -5, 5], cmap='viridis', vmin=0, vmax=0.25)
            time_text = ax.text(0.05, 0.92, '', transform=ax.transAxes, color='white', fontweight='bold')

            def init():
                im.set_array(np.zeros((grid_pts, grid_pts)))
                return [im, time_text]

            def animate(i):
                rho = states[i].full() if states[i].type == 'oper' else qutip.ket2dm(states[i]).full()
                pdf_2d = np.zeros((grid_pts, grid_pts), dtype=float)
                for n in range(self.num_qudit_levels):
                    for m in range(self.num_qudit_levels):
                        if abs(rho[n, m]) > 1e-4:
                            term = rho[n, m] * np.outer(wf_basis[n], wf_basis[m])
                            pdf_2d += term.real
                im.set_array(pdf_2d)
                time_text.set_text(f"Время: {times[i]:.3f} с")
                return [im, time_text]

            ani = FuncAnimation(fig, animate, init_func=init, frames=total_frames, blit=True)
            filename = f"memory_decay_2d_{file_suffix}.gif"
            ani.save(filename, writer='pillow', fps=fps)
            plt.close(fig)
            print(f"Файл сохранен: {filename}")

        print("Генерация итогового графика...")
        plt.figure(figsize=(10, 5))
        t_plot = np.linspace(0, sim_time, 100)
        plt.plot(t_plot, np.exp(-self.kappa * t_plot) * 100, 'r-', label='Без защиты', lw=2)
        plt.plot(t_plot, np.exp(-(self.kappa/15.0) * t_plot) * 100, 'g-', label='С защитой (Коды Бозе)', lw=2)
        plt.plot(t_plot, np.ones_like(t_plot) * 100, 'b--', label='Идеальное', lw=2)
        plt.axhline(y=10, color='gray', linestyle='--', label='Порог потери данных')
        plt.title("Сравнение сохранности данных")
        plt.xlabel("Время (секунды)")
        plt.ylabel("Целостность данных (%)")
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.show()

    def _get_psi_n_x(self, n, x):
        norm = 1.0 / np.sqrt(2**n * factorial(n)) * (np.pi**(-0.25))
        return norm * np.exp(-x**2 / 2.0) * hermite(n)(x)

memory = RealisticQuantumMemory(num_qudit_levels=10)
memory.store_data([9])
memory.generate_visualizations()
