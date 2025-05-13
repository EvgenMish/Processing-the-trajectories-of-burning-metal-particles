import handler
import plotter
import solver

## "particles_dist_clear.json" отладочный файл с расстояниями и временем как particle.json только другой формат distance
## "ВСЕ.txt" костыльный файл с сырыми данными каторые отпрявлял ВА, нужен только потому что я сразу не писал комментарии в particles.json, а только в тхт
## "particles_dist_final.json" файл с образанными расстояниями и временем, получен обработкой сырого "particles.json" -> вытяныл данные из "ВСЕ.txt" -> "particles_dist_clear.json" -> "particles_dist_final.json"
## "selections.json" файл с выборками, получен обработкой "particles_dist_final.json" -> "selections.json"
## "results.json" файл с результатами, получен решением уравнений для каждой выборки "selections.json" -> "results.json"
## TODO: все графики в один файл

def full_processing(
        particles_intup_file='particles_dist_final.json',
        selections_file='selections.json', solver_results_file='results.json',
        use_hitted_particles=True,
        use_not_hitted_particles=True,
        bins=20,
        show_plots=True
        ):
    if use_hitted_particles and use_not_hitted_particles:
        print('\033[92mИспользуются все частицы\033[0m')
    elif use_hitted_particles:
        print('\033[92mИспользуются только частицы с ударами о поддон\033[0m')
    elif use_not_hitted_particles:
        print('\033[92mИспользуются только частицы без ударов о поддон\033[0m')
    elif not use_hitted_particles and not use_not_hitted_particles:
        print('\033[91mОшибка! Не используется ни одна частица!\033[0m')
        return
    
    handler.main(
        input_file=particles_intup_file,
        output_file=selections_file,
        USE_HITTED_PARTICLES=use_hitted_particles,
        USE_NOT_HITTED_PARTICLES=use_not_hitted_particles,
        BINS=bins
    ) ##Создание файла с выборками
    ## selections.json уже содержит скорсости для каждой частицы, а так же осреднённые скорости и расстояния для каждой выборки

    solver.main(
        input_file=selections_file,
        output_file=solver_results_file
    ) ##Расчёт всех выборок и создание файла с результатами

    plotter.main(input_file='selections.json', show_plots=show_plots) ##Графики для всех выборок


if __name__ == "__main__":
    full_processing( 
        particles_intup_file='particles_dist_final.json',
        selections_file='selections.json',
        solver_results_file='results.json',
        use_hitted_particles=False, ## True - использовать частицы с ударами, False - не использовать
        use_not_hitted_particles=True, ## True - использовать частицы без ударов, False - не использовать
        bins=10, ## Количество выборок (интервалов по диаметрам частиц),
        show_plots=True ## True - показывать графики, False - не показывать (только сохранять в файл) 
    )
