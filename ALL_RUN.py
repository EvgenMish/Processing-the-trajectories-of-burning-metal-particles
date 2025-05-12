import handler
import plotter
import solver

## "particles_dist_clear.json" отладочный файл с расстояниями и временем как particle.json только другой формат distance
## "particles_dist_final.json" файл с образанными расстояниями и временем, получен обработкой сырого "particles.json" -> вытяныл данные из "ВСЕ.txt" -> "particles_dist_clear.json" -> "particles_dist_final.json"
## "selections.json" файл с выборками, получен обработкой "particles_dist_final.json" -> "selections.json"
## "results.json" файл с результатами, получен решением уравнений для каждой выборки "selections.json" -> "results.json"
## TODO: выбоки делить по тому, догорели ли в полёте

def full_processing():
    # Параметры
    input_file = 'particles_dist_final.json'
    
    handler.main(input_file=input_file, output_file='selections.json') ##Создание файла с выборками
    ## selections.json уже содержит скорсости для каждой частицы, а так же осреднённые скорости и расстояния для каждой выборки

    plotter.main(input_file='selections.json') ##Графики для всех выборок
    solver.main(input_file='selections.json', output_file='results.json') ##Расчёт всех выборок и создание файла с результатами

fuke = full_processing

