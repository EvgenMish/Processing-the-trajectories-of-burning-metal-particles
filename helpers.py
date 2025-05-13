import json
import re

##  to distance = [t, distance] from []
def convert_distances(input_filename='particles.json', output_filename='particles_dist_clear.json'):
    with open(input_filename, 'r', encoding='utf-8') as f:
        data = json.load(f)

    spf = data['description']['spf']

    for particle in data['particles']:
        distances = particle['distance']
        converted = [(round(i * spf, 5), dist) for i, dist in enumerate(distances)]
        particle['distance'] = converted

    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(f'Конвертация завершена. Данные сохранены в {output_filename}')

def convert_distances_to_short(input_filename='particles_dist_final.json', output_filename='particles_dist_final.json'):
    with open(input_filename, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for particle in data['particles']:
        # Конвертируем в значения расстояний
        particle["distance"] = [d[1] for d in particle["distance"]]
    
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f'Обратная Конвертация завершена. Данные сохранены в {output_filename}')

def find_hits_from_txt(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()

    particles_raw = content.strip().split('\n\n')
    hits = []

    for particle_data in particles_raw:
        lines = particle_data.strip().split('\n')
        if not lines:
            continue

        name = re.sub(r'_+', '_', lines[0].strip()).strip('_')

        # найти первую строчку таблицы (первое появление)
        first_time = None
        for line in lines:
            if "(первое появление)" in line.lower():
                parts = line.strip().split()
                if len(parts) >= 2:
                    first_time = float(parts[0])
                break

        if first_time is None:
            continue

        # найти строку с ударом
        for line in lines:
            if "(удар о поддон)" in line.lower() or "(удар о поддон, отскочила)" in line.lower():
                parts = line.strip().split()
                if len(parts) >= 2:
                    hit_time = float(parts[0])
                    distance = parts[1]
                    json_time = round(hit_time - first_time, 5)

                    hits.append({
                        "particle": name,
                        "hit": [json_time, distance]
                    })
                break  # только первый удар
    print(f'Найдено {len(hits)} ударов о поддон в {filename}')
    print('Список частиц с ударами:\n' + '\n'.join(hit["particle"] for hit in hits))    
    return hits


def cut_distances_by_hits_and_convert(input_json, hits, output_json):
    with open(input_json, 'r', encoding='utf-8') as f:
        data = json.load(f)

    particles = data["particles"]
    changed_count = 0
    not_changed_count = 0

    for hit in hits:
        name = hit["particle"]
        hit_time = float(hit["hit"][0])

        for particle in particles:
            ## если частица с таким именем
            if particle["name"] == name:
                old_len = len(particle["distance"])
                particle["hit"] = True
                # Обрезаем distance по времени удара
                particle["distance"] = [d for d in particle["distance"] if d[0] <= hit_time]
                new_len = len(particle["distance"])
                if new_len != old_len:
                    changed_count += 1
                else: 
                    not_changed_count += 1
                    print(f'Частица {name} потухла от удара')
                break

    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(f'\033[92mГотово! Обрезаны траектории {changed_count} частиц с ударом, {not_changed_count} частиц потухли от удара. Данные сохранены в {output_json}\033[0m')


def main():
    txt_filename = "ВСЕ.txt"
    particles_json_filename = "particles_dist_clear.json" ## это файл с расстояниями и временем как particle.json только другой формат distance
    output_json_filename = "particles_dist_final.json" ## это образанный файл с расстояниями и временем как particle.json

    convert_distances('particles.json', particles_json_filename) # конвертируем в [t, distance]
    hits = find_hits_from_txt(txt_filename) # находим удары из файла
    cut_distances_by_hits_and_convert(particles_json_filename, hits, output_json_filename) # обрезаем по времени удара и сохраняем в новый файл
    convert_distances_to_short(output_json_filename, output_json_filename) # конвертируем обратно в distance только

if __name__ == "__main__":
    main()