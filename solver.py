import math
import json
import matplotlib.pyplot as plt
import numpy as np

### Константы
ro = 2400  # Плотность частиц (кг/м^3)
ro_g = 0.17066 # Плотность газа (кг/м^3)
mu = 6.98 *10**-5 # Вязкость газа (Па*с)
g = 9.81 # Ускорение свободного падения (м/с^2)

def get_velosity_polynom_coeffs_for_bin(bin_entry):
    """
    Получает коэффициенты полинома для зависимости скорости от времени для выборки.
    """
    coeffs = []

    avg_speeds = bin_entry['averaged_speeds']
    if avg_speeds and len(avg_speeds) > 3:
        # Извлекаем скорости и времена из данных
        times = [entry[0] for entry in avg_speeds]
        speeds = [entry[1] for entry in avg_speeds]

        # Применяем полиномиальную регрессию для нахождения коэффициентов
        coeffs = np.polyfit(times, speeds, deg=3)

    return coeffs
 
def get_mass_and_area(bin_entry):
    """
    Получает массу и площадь для выборки частиц.
    """
    diameter = bin_entry['header']['average_diameter'] * 10**-6  # Приводим к метрам из мкм

    mass = ro * math.pi / 6 * diameter**3  # Масса частицы
    area = math.pi * diameter**2 / 4  # Эффективная площадь

    return mass, area, diameter

def solve_eq(selection_data, dt_poly=0.001, output_filename='results.json'):
    results = []

    for bin_entry in selection_data:
        if bin_entry['header']['average_diameter'] is None:
            continue

        m, S, D = get_mass_and_area(bin_entry)
        coeffs = get_velosity_polynom_coeffs_for_bin(bin_entry)

        # Диапазон времени по averaged_speeds
        times = [t for t, _ in bin_entry['averaged_speeds']]
        t_min = min(times)
        t_max = max(times)

        ## === По полиному ===
        Cd_poly = []
        Re_poly = []
        A_poly = []

        t = t_min + dt_poly

        while t <= t_max:
            t_prev = t - dt_poly

            u = np.polyval(coeffs, t) * 1e-2  # м/с
            u_prev = np.polyval(coeffs, t_prev) * 1e-2  # м/с

            if u == 0:
                t += dt_poly
                continue

            Cd_temp = -2 * m / (S * ro_g * u) * ((u - u_prev) / dt_poly - g)
            Re_temp = (ro_g * abs(u) * D) / mu
            A_temp = Re_temp * Cd_temp

            Cd_poly.append(Cd_temp)
            Re_poly.append(Re_temp)
            A_poly.append(A_temp)

            t += dt_poly

        ## === По дискретным averaged_speeds ===
        Cd_disc = []
        Re_disc = []
        A_disc = []

        speeds = bin_entry['averaged_speeds']
        for i in range(1, len(speeds)):
            t = speeds[i][0]
            t_prev = speeds[i-1][0]
            dt_disc = t - t_prev

            u = speeds[i][1] * 1e-2  # м/с
            u_prev = speeds[i-1][1] * 1e-2  # м/с

            if u == 0:
                continue

            Cd_temp = -2 * m / (S * ro_g * u) * ((u - u_prev) / dt_disc - g)
            Re_temp = (ro_g * abs(u) * D) / mu
            A_temp = Re_temp * Cd_temp

            Cd_disc.append(Cd_temp)
            Re_disc.append(Re_temp)
            A_disc.append(A_temp)

        ## Запись результата по выборке
        result_entry = {
            "D": [
                bin_entry['header']['min_diameter'],
                bin_entry['header']['max_diameter'],
                bin_entry['header']['average_diameter']
            ],
            "Re": [
                min(Re_poly + Re_disc) if (Re_poly or Re_disc) else None,
                max(Re_poly + Re_disc) if (Re_poly or Re_disc) else None
            ],
            "avgCd": {
                "poly": np.mean(Cd_poly) if Cd_poly else None,
                "disc": np.mean(Cd_disc) if Cd_disc else None,
                "all": np.mean([np.mean(Cd_poly), np.mean(Cd_disc)])
            },
            "avgA": {
                "poly": np.mean(A_poly) if A_poly else None,
                "disc": np.mean(A_disc) if A_disc else None,
                "all": np.mean([np.mean(A_poly), np.mean(A_disc)])
            },
            "data": {
                "Cd_poly": Cd_poly,
                "Cd_disc": Cd_disc,
                "A_poly": A_poly,
                "A_disc": A_disc,
                "Re_poly": Re_poly,
                "Re_disc": Re_disc
            }
        }

        results.append(result_entry)

    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

    print(f'\033[92mРезультаты сохранены в {output_filename}\033[0m')

def plot_results_table(filename='results.json'):
    with open(filename, 'r', encoding='utf-8') as f:
        results = json.load(f)

    # Заголовки таблицы
    columns = [
        "Диаметры (мин-макс, ср.)",
        "Re (мин-макс)",
        "Cd (полином)",
        "Cd (дискретн.)",
        "A (полином)",
        "A (дискретн.)"
    ]

    # Данные таблицы
    table_data = []

    for entry in results:
        D_min, D_max, D_avg = entry["D"]
        Re_min, Re_max = entry["Re"]
        Cd_poly = entry["avgCd"]["poly"]
        Cd_disc = entry["avgCd"]["disc"]
        A_poly = entry["avgA"]["poly"]
        A_disc = entry["avgA"]["disc"]

        row = [
            f"{D_min}-{D_max}, {round(D_avg, 2) if D_avg is not None else '—'}",
            f"{round(Re_min, 2) if Re_min is not None else '—'} - {round(Re_max, 2) if Re_max is not None else '—'}",
            f"{round(Cd_poly, 4) if Cd_poly is not None else '—'}",
            f"{round(Cd_disc, 4) if Cd_disc is not None else '—'}",
            f"{round(A_poly, 4) if A_poly is not None else '—'}",
            f"{round(A_disc, 4) if A_disc is not None else '—'}"
        ]

        table_data.append(row)
    
    avgCd_poly = np.mean([entry["avgCd"]["poly"] for entry in results if entry["avgCd"]["poly"] is not None])
    avgCd_disc = np.mean([entry["avgCd"]["disc"] for entry in results if entry["avgCd"]["disc"] is not None])
    avgA_poly = np.mean([entry["avgA"]["poly"] for entry in results if entry["avgA"]["poly"] is not None])
    avgA_disc = np.mean([entry["avgA"]["disc"] for entry in results if entry["avgA"]["disc"] is not None])
    all_avg_Cd = np.mean([avgCd_poly, avgCd_disc])
    all_avg_A = np.mean([avgA_poly, avgA_disc])

    row_stat_1 = [
        "Средние по всем выборкам",
        "—",
        f"{round(avgCd_poly, 4) if avgCd_poly is not None else '—'}",
        f"{round(avgCd_disc, 4) if avgCd_disc is not None else '—'}",
        f"{round(avgA_poly, 4) if avgA_poly is not None else '—'}",
        f"{round(avgA_disc, 4) if avgA_disc is not None else '—'}"
    ]
    table_data.append(row_stat_1)
    row_stat_2 = [
        f"Средние",
        f"—",
        f"{round(all_avg_Cd, 4) if all_avg_Cd is not None else '—'}",
        f"—",
        f"{round(all_avg_A, 4) if all_avg_A is not None else '—'}",
        f"—"
    ]
    table_data.append(row_stat_2)

    # Построение таблицы с matplotlib
    fig, ax = plt.subplots(figsize=(14, len(table_data) * 0.6 + 1))
    ax.axis('off')

    table = ax.table(
        cellText=table_data,
        colLabels=columns,
        loc='center',
        cellLoc='center'
    )

    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.5)

    plt.title('Результаты расчёта по выборкам', fontsize=14, pad=20)
    plt.tight_layout()
    plt.savefig('./_RESULTS_PLOTS/results_table.png', bbox_inches='tight')
    print(f'\033[92mТаблица результатов сохранена в ./_RESULTS_PLOTS/results_table.png\033[0m')

def plot_all_Cd_vs_time(selection_data, dt=0.001):
    """
    Строит графики Cd от времени для всех выборок на подграфиках,
    с расчётом, идентичным get_Cd_Re_A.
    """
    valid_bins = [bin_entry for bin_entry in selection_data 
                  if bin_entry['header']['average_diameter'] is not None 
                  and len(bin_entry['averaged_speeds']) > 3]

    bin_count = len(valid_bins)
    cols = 3
    rows = math.ceil(bin_count / cols)

    fig, axes = plt.subplots(rows, cols, figsize=(5 * cols, 4 * rows))
    axes = axes.flatten()

    for i, bin_entry in enumerate(valid_bins):
        ax = axes[i]

        m, S, D = get_mass_and_area(bin_entry)
        coeffs = get_velosity_polynom_coeffs_for_bin(bin_entry)
        if len(coeffs) == 0:
            ax.set_visible(False)
            continue

        times = []
        Cd_values = []

        for j in range(1, len(bin_entry['averaged_speeds'])):
            t = bin_entry['averaged_speeds'][j][0]
            t_prev = bin_entry['averaged_speeds'][j-1][0]

            u = np.polyval(coeffs, t) * 10**-2  # м/с
            u_prev = np.polyval(coeffs, t_prev) * 10**-2  # м/с

            if u == 0:
                continue

            Cd_temp = (m * ((u - u_prev) / dt) - m * g) * (-8 / (math.pi * D**2 * ro_g * u))

            times.append(t)
            Cd_values.append(Cd_temp)

        if len(Cd_values) == 0:
            ax.set_visible(False)
            continue

        ax.plot(times, Cd_values, marker='o', linestyle='-', color='blue')
        ax.set_title(f"Dср={bin_entry['header']['average_diameter']} мкм", fontsize=10)
        ax.set_xlabel("Время (с)")
        ax.set_ylabel("Cd")
        ax.grid(True)

    for j in range(i + 1, len(axes)):
        fig.delaxes(axes[j])

    fig.suptitle("Зависимость Cd от времени для всех выборок (по формуле get_Cd_Re_A)", fontsize=16)
    plt.tight_layout(pad=2.0, rect=[0.03, 0.03, 0.97, 0.95])

def main(input_file='selections.json', output_file='results.json'):
    with open(input_file, 'r', encoding='utf-8') as f:
        selection_data = json.load(f)

    solve_eq(selection_data, dt_poly=0.001, output_filename=output_file)
    plot_results_table(filename=output_file)


    ##plt.show()

if __name__ == "__main__":
    main()