## Обработчик для построения графиков из файла selections.json
import math
import json
import matplotlib.pyplot as plt
import numpy as np

def plot_all_bins_DISTANCES(selection_data):
    bin_count = len(selection_data)
    cols = 3
    rows = math.ceil(bin_count / cols)

    fig, axes = plt.subplots(rows, cols, figsize=(5 * cols, 2 * rows))
    axes = axes.flatten()  # чтобы обращаться к осям по индексу
    fig.suptitle('Графики расстояния от времени для всех выборок', fontsize=16)

    for i, bin_entry in enumerate(selection_data):
        ax = axes[i]
        
        # Графики для каждой частицы (тонкая черная линия)
        for particle in bin_entry['particles']:
            distances = particle['distance']
            if distances:
                times = [j * 0.04 for j in range(len(distances))]
                ax.plot(times, distances, color='black', linewidth=0.8, alpha=0.4)

        # График для осреднённых расстояний (толстая красная линия)
        avg_distances = bin_entry['averaged_distances']
        if avg_distances:
            times_avg = [point[0] for point in avg_distances]
            distances_avg = [point[1] for point in avg_distances]
            ax.plot(times_avg, distances_avg, color='red', linewidth=2.0, label='Среднее')

        ax.set_title( f"Dср={bin_entry['header']["average_diameter"]} мкм ({bin_entry['header']["min_diameter"]} - {bin_entry['header']["max_diameter"]})")
        ax.set_xlabel('Время (с)')
        ax.set_ylabel('Расстояние (см)')
        ax.grid(True)

    # Удаляем пустые графики, если их больше, чем выборок
    for j in range(i + 1, len(axes)):
        fig.delaxes(axes[j])

    plt.tight_layout()
    plt.savefig('./_RESULTS_PLOTS/dist_t_ALL.png', bbox_inches='tight')

def plot_all_bins_av_SPEED(selection_data):

    bin_count = len(selection_data)
    cols = 3
    rows = math.ceil(bin_count / cols)

    fig, axes = plt.subplots(rows, cols, figsize=(5 * cols, 5 * rows))
    axes = axes.flatten()
    fig.suptitle('Графики скорости от времени для всех выборок', fontsize=16)

    initial_speeds_data = []  # сюда будем собирать (Dср, v0)

    for i, bin_entry in enumerate(selection_data):
        ax = axes[i]

        avg_speeds = bin_entry['averaged_speeds']
        if avg_speeds:
            times_avg = [point[0] for point in avg_speeds]
            speeds_avg = [point[1] for point in avg_speeds]

            # График средних скоростей
            ax.plot(times_avg, speeds_avg, color='black', linewidth=1.0, label='Среднее')

            # Аппроксимация полиномом 3-й степени
            coeffs = np.polyfit(times_avg, speeds_avg, deg=3)
            poly_times = np.linspace(min(times_avg), max(times_avg), 200)
            poly_speeds = np.polyval(coeffs, poly_times)
            ax.plot(poly_times, poly_speeds, color='red', linewidth=1.0, label='Полином 3 ст.')

            # Начальная скорость (значение полинома при t=0)
            v0 = np.polyval(coeffs, 0)
            D_avg = bin_entry['header']['average_diameter']
            initial_speeds_data.append((D_avg, v0))

        ax.set_title(f"Dср={bin_entry['header']['average_diameter']} мкм "
                     f"({bin_entry['header']['min_diameter']} - {bin_entry['header']['max_diameter']})")
        ax.set_xlabel('Время (с)')
        ax.set_ylabel('Скорость (см/с)')
        ax.grid(True)
        ax.legend()

    # Удаляем пустые графики, если их больше, чем выборок
    for j in range(i + 1, len(axes)):
        fig.delaxes(axes[j])

    plt.tight_layout(pad=1.0, h_pad=14.0, w_pad=1.0, rect=[0.05, 0.05, 0.95, 0.95])
    plt.savefig('./_RESULTS_PLOTS/vel_t_ALL.png', bbox_inches='tight')

    return initial_speeds_data  # возвращаем список (Dср, v0)

def OLD_plot_initial_speed_vs_diameter_from_DISCRETE(bin_data):
    diameters = []
    initial_speeds = []

    for bin_entry in bin_data:
        avg_diameter = bin_entry['header']['average_diameter']
        speeds = bin_entry['averaged_speeds']
        if speeds:
            initial_speed = speeds[0][1]
            diameters.append(avg_diameter)
            initial_speeds.append(initial_speed)

    # Преобразуем в numpy массивы
    x = np.array(diameters)
    y = np.array(initial_speeds)

    # Линейная аппроксимация (1-я степень)
    coeffs = np.polyfit(x, y, deg=1)
    poly = np.poly1d(coeffs)

    plt.figure()
    # Построение графика точек
    plt.scatter(x, y, color='green', label='Данные')

    # Построение линии аппроксимации
    x_fit = np.linspace(min(x), max(x), 100)
    y_fit = poly(x_fit)
    plt.plot(x_fit, y_fit, color='red', linewidth=2, linestyle='--', label=f'Линия МНК: v0 = {coeffs[0]:.2f}D + {coeffs[1]:.2f}')

    plt.title('Зависимость начальной скорости от диаметра с линией МНК')
    plt.xlabel('Dср (мкм)')
    plt.ylabel('v0 (см/с)')
    plt.grid(True)
    plt.legend()

def OLD_plot_initial_speed_vs_diameter_from_POLYNOMS(initial_speeds_data):
    diameters = [item[0] for item in initial_speeds_data]
    initial_speeds = [item[1] for item in initial_speeds_data]

    plt.figure(figsize=(7, 7))
    plt.scatter(diameters, initial_speeds, color='blue', label='Начальные скорости')

    # Линейная аппроксимация
    coeffs_fit = np.polyfit(diameters, initial_speeds, deg=1)
    d_fit = np.linspace(min(diameters), max(diameters), 200)
    v0_fit = np.polyval(coeffs_fit, d_fit)
    plt.plot(d_fit, v0_fit, color='red', linewidth=2, linestyle='--', label=f'Линия МНК: v0 = {coeffs_fit[0]:.5f}D + {coeffs_fit[1]:.5f}')

    plt.title('Начальная скорость от среднего диаметра (линейная аппроксимация)')
    plt.xlabel('Dср (мкм)')
    plt.ylabel('v₀ (см/с)')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()

def plot_combined_initial_speed_vs_diameter(discrete_bin_data, polynom_initial_speeds_data):
    import numpy as np
    import matplotlib.pyplot as plt

    # Данные из дискретных скоростей
    diameters_discrete = []
    initial_speeds_discrete = []
    for bin_entry in discrete_bin_data:
        avg_diameter = bin_entry['header']['average_diameter']
        speeds = bin_entry['averaged_speeds']
        if speeds:
            initial_speed = speeds[0][1]
            diameters_discrete.append(avg_diameter)
            initial_speeds_discrete.append(initial_speed)

    # Данные из полиномов
    diameters_poly = [item[0] for item in polynom_initial_speeds_data]
    initial_speeds_poly = [item[1] for item in polynom_initial_speeds_data]

    plt.figure(figsize=(8, 8))

    # Точки дискретных скоростей
    plt.scatter(diameters_discrete, initial_speeds_discrete, color='green', label='Начальная скорость (эмпирические данные)')

    # Аппроксимация дискретных скоростей
    coeffs_discrete = np.polyfit(diameters_discrete, initial_speeds_discrete, deg=1)
    d_fit = np.linspace(min(diameters_discrete + diameters_poly), max(diameters_discrete + diameters_poly), 200)
    v0_fit_discrete = np.polyval(coeffs_discrete, d_fit)
    plt.plot(d_fit, v0_fit_discrete, color='green', linestyle='--', linewidth=2, label=f'МНК (эмпирические данные): v₀={coeffs_discrete[0]:.3f}D+{coeffs_discrete[1]:.3f}')

    # Точки из полиномов
    plt.scatter(diameters_poly, initial_speeds_poly, color='blue', label='Начальная скорость (из полиномов)')

    # Аппроксимация полиномных скоростей
    coeffs_poly = np.polyfit(diameters_poly, initial_speeds_poly, deg=1)
    v0_fit_poly = np.polyval(coeffs_poly, d_fit)
    plt.plot(d_fit, v0_fit_poly, color='blue', linestyle='--', linewidth=2, label=f'МНК (полиномы): v₀={coeffs_poly[0]:.3f}D+{coeffs_poly[1]:.3f}')

    # Среднее значение дискретных начальных скоростей
    mean_discrete = np.mean(initial_speeds_discrete)
    plt.axhline(mean_discrete, color='green', linestyle=':', linewidth=2, label=f'Среднее (дискретная): {mean_discrete:.2f} см/с')

    # Среднее значение начальных скоростей из полиномов
    mean_poly = np.mean(initial_speeds_poly)
    plt.axhline(mean_poly, color='blue', linestyle=':', linewidth=2, label=f'Среднее (полиномы): {mean_poly:.2f} см/с')

    # Оформление
    plt.title('Начальная скорость от диаметра (эмпирические данныее и полиномы)')
    plt.xlabel('Dср (мкм)')
    plt.ylabel('v₀ (см/с)')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig('./_RESULTS_PLOTS/init_vel_D_ALL.png', bbox_inches='tight')

def plot_burnTime_D(selection_data):

    burn_times = []
    diameters = []

    for i, bin_entry in enumerate(selection_data):
        for particle in bin_entry['particles']:
            burn_times.append(particle['burn_time'])
            diameters.append(particle['diameter'])
    plt.figure(figsize=(8, 8))
    plt.scatter(diameters, burn_times, c='blue', alpha=0.5)
    plt.title('Зависимость времени горения от диаметра частицы')
    plt.xlabel('D (мкм)')
    plt.ylabel('Tгор (c)')
    plt.grid(True)
    plt.savefig('./_RESULTS_PLOTS/burnTimeD.png', bbox_inches='tight')

def main(input_file='selections.json', show_plots=True):
    with open(input_file, 'r', encoding='utf-8') as f:
        selection_data = json.load(f)

    plot_all_bins_DISTANCES(selection_data)
    initial_speeds_data = plot_all_bins_av_SPEED(selection_data)
    plot_combined_initial_speed_vs_diameter(selection_data, initial_speeds_data)
    plot_burnTime_D(selection_data)

    if show_plots:
        plt.show()

if __name__ == "__main__":
    main()
