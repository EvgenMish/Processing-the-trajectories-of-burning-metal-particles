## Группировка объектов по диаметрам и вычисление статистики для каждой группы вывод в selections.json
## Приеимает на вход файл particles_dist_final.json, в котором находятся данные о частицах уже обрезанные по времени удара
import json
import matplotlib.pyplot as plt

def histogram_D(data, bins_count=10, include_hitted=True, include_NOT_hitted=True):
    plt.figure()
    diameters = []
    filtered_particles = []

    # Фильтрация частиц и сбор диаметров
    for particle in data['particles']:
        hit = particle.get('hit', None)

        if hit is True and not include_hitted:
            continue
        if (hit is False or hit is None) and not include_NOT_hitted:
            continue

        diameters.append(particle['diameter'])
        filtered_particles.append(particle)

    counts, bins, _ = plt.hist(diameters, bins=bins_count, color='blue', alpha=0.7)

    # Группировка отфильтрованных частиц по bin'ам
    bin_objects = [[] for _ in range(len(bins) - 1)]
    for particle in filtered_particles:
        d = particle['diameter']
        for i in range(len(bins) - 1):
            if bins[i] <= d < bins[i + 1] or (i == len(bins) - 2 and d == bins[-1]):
                bin_objects[i].append(particle)
                break

    plt.title('Гистограмма распределения диаметров частиц')
    plt.xlabel('D (мкм)')
    plt.ylabel('Частота')
    plt.grid(True)
    plt.xticks(bins, rotation=0)
    plt.savefig('./_RESULTS_PLOTS/histogram.png', bbox_inches='tight')

    return bin_objects

def get_bin_stats(bin_objects):
    stats_per_bin = []

    for bin_list in bin_objects:
        if not bin_list:
            stats_per_bin.append((None, None, None, 0))
        else:
            diameters = [p['diameter'] for p in bin_list]
            minD = min(diameters)
            maxD = max(diameters)
            averageD = round(sum(diameters) / len(diameters), 2)
            count = len(diameters)
            stats_per_bin.append((minD, maxD, averageD, count))

    return stats_per_bin

def average_distances_for_bin(bin_list):
    # Проверяем, что есть хотя бы одна частица с данными о расстоянии
    if not bin_list:
        return []  # Если в бине нет частиц, возвращаем пустой список

    # Определяем максимальную длину расстояний среди всех частиц в текущем бине
    max_length = max(len(p['distance']) for p in bin_list if p['distance'])  # Игнорируем пустые списки

    # Инициализируем список для хранения среднего расстояния на каждом шаге времени
    averaged_distances = [(i * 0.04, 0) for i in range(max_length)]  # Список кортежей (время, среднее расстояние)
    count_at_time = [0] * max_length  # Счётчик количества частиц, имеющих данные для этого времени

    # Проходим по каждой частице в бине
    for particle in bin_list:
        distances = particle.get('distance', [])
        if distances:  # Если есть данные о расстоянии
            for i in range(len(distances)):
                averaged_distances[i] = (averaged_distances[i][0], averaged_distances[i][1] + distances[i])
                count_at_time[i] += 1

    # Теперь вычисляем среднее расстояние для каждого времени, деля на количество частиц
    for i in range(max_length):
        if count_at_time[i] > 0:
            averaged_distances[i] = (averaged_distances[i][0],  round(averaged_distances[i][1] / count_at_time[i], 4))

    return averaged_distances

def average_speeds_for_bin(bin_list):
    """
    Для каждой выборки (набора частиц) вычисляет осреднённые скорости на каждом шаге времени.
    """
    # Инициализация словаря для накопления скоростей по времени
    time_speeds = {}

    # Проходим по каждой частице
    for particle in bin_list:
        speeds = particle["speed"]
        
        # Проходим по каждой скорости частицы
        for t, v in speeds:
            if t not in time_speeds:
                time_speeds[t] = []
            time_speeds[t].append(v)
    
    # Теперь для каждого времени считаем среднее значение скорости
    averaged_speeds = []
    for t in sorted(time_speeds.keys()):
        avg_speed = sum(time_speeds[t]) / len(time_speeds[t])
        averaged_speeds.append([round(t, 5), round(avg_speed, 5)])

    return averaged_speeds

def compute_particle_speeds(particles, dt=0.04):
    """
    Вычисляет скорости для каждой частицы и записывает их в поле 'speed'.
    Скорость считается как разность расстояний между соседними точками, делённая на dt.
    """
    for particle in particles:
        distances = particle["distance"]
        speeds = []

        for i in range(len(distances) - 1):
            v = (distances[i+1] - distances[i]) / dt
            t = i * dt
            speeds.append([round(t, 5), round(v, 5)])

        particle["speed"] = speeds

def main(input_file='particles_dist_final.json', output_file='selections.json', USE_HITTED_PARTICLES=True, USE_NOT_HITTED_PARTICLES=True, BINS=20):

    print(f'Обработка файла {input_file}...')

    data = json.load(open(input_file, 'r', encoding='utf-8'))

    bin_objects = histogram_D(data, bins_count=BINS, include_hitted=USE_HITTED_PARTICLES, include_NOT_hitted=USE_NOT_HITTED_PARTICLES)  # Группировка объектов по диаметрам
    #гистрограмма распределения диаметров частиц будет сохранена в ./_RESULTS_PLOTS/histogram.png

    stats_per_bin = get_bin_stats(bin_objects)
    
    # Вычисление общего количества частиц
    allCount = sum(stats[3] for stats in stats_per_bin)
    print(f"Количество частиц для обработки: {allCount}")

    # Вывод статистики по каждой выборке
    for i, stats in enumerate(stats_per_bin):
        print(f"Bin {i+1}: ({stats[0]} - {stats[1]}), {stats[2]} | Count: {stats[3]}")

    # Сохранение объектов в JSON файл
    bin_data = []
    for i, (bin_list, stats) in enumerate(zip(bin_objects, stats_per_bin)):

        compute_particle_speeds(bin_list, dt=0.04)  # Вычисляем скорости для каждой частицы в бине

        averaged_distances = average_distances_for_bin(bin_list)
        average_speeds = average_speeds_for_bin(bin_list)

    # Создание структуры с данными для каждой выборки
        bin_entry = {
        'header': {
            'min_diameter': stats[0],
            'max_diameter': stats[1],
            'average_diameter': stats[2],
            'particle_count': stats[3]
        },
        'averaged_distances': averaged_distances, # Усреднённые расстояния для каждого шага времени для этой выборки
        'averaged_speeds': average_speeds,  # Усреднённые скорости для каждого шага времени для этой выборки
        'particles': bin_list  # Список частиц для этой выборки
        }
        bin_data.append(bin_entry)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(bin_data, f, ensure_ascii=False, indent=4)

    print(f'Выборки сохранены в {output_file}')
    print(f'Гистограмма распределения диаметров частиц сохранена в ./_RESULTS_PLOTS/histogram.png')
    print("--"*20)

if __name__ == "__main__":
    main()