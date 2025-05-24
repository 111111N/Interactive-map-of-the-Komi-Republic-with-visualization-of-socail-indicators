import json
from pathlib import Path

def process_environmental_protection_data():
    # Настройка путей
    base_dir = Path(__file__).parent
    input_file = base_dir / 'Охрана окружающей среды.csv'
    output_file = base_dir / 'sorted' / 'environmental_protection_data.json'
    
    # Создаем папку для результатов
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Все административные единицы
    target_regions = {
        # Городские округа
        "Сыктывкар": "Городской округ",
        "Воркута": "Городской округ",
        "Вуктыл": "Городской округ", 
        "Инта": "Городской округ",
        "Усинск": "Городской округ",
        "Ухта": "Городской округ",
        
        # Муниципальные районы
        "Вуктыл": "Муниципальный район",
        "Ижемский": "Муниципальный район",
        "Княжпогостский": "Муниципальный район",
        "Койгородский": "Муниципальный район",
        "Корткеросский": "Муниципальный район",
        "Печора": "Муниципальный район",
        "Прилузский": "Муниципальный район",
        "Сосногорск": "Муниципальный район",
        "Сыктывдинский": "Муниципальный район",
        "Сысольский": "Муниципальный район",
        "Троицко-Печорский": "Муниципальный район",
        "Удорский": "Муниципальный район",
        "Усть-Вымский": "Муниципальный район",
        "Усть-Куломский": "Муниципальный район",
        "Усть-Цилемский": "Муниципальный район"
    }

    try:
        with open(input_file, 'r', encoding='windows-1251') as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]

        result = {}
        current_region = None
        current_category = None
        years = [str(y) for y in range(2008, 2024)]
        indicators = set()

        i = 0
        while i < len(lines):
            line = lines[i]
            parts = line.split(';')
            row_name = parts[0].strip()
            
            # Пропускаем заголовки
            if not row_name or 'значение показателя за год' in row_name:
                i += 1
                continue
                
            # Проверяем, является ли строка названием региона
            region_found = False
            for region, region_type in target_regions.items():
                if region_type == "Муниципальный район":
                    if (f"Муниципальный район {region}" in row_name or 
                        f"Муниципальный район {region} (" in row_name):
                        current_region = f"{region_type} {region}"
                        region_found = True
                        break
                elif region_type == "Городской округ":
                    if region in row_name and not any(x in row_name for x in ["Городской округ", "Городские округа"]):
                        current_region = f"{region_type} {region}"
                        region_found = True
                        break
            
            if region_found:
                if current_region not in result:
                    result[current_region] = {}
                i += 1
                continue
            
            # Обработка показателей
            if current_region:
                # Для заголовков категорий (например, "Выброшено в атмосферу...")
                if (row_name.startswith("Выброшено в атмосферу") or 
                    row_name.startswith("Текущие (эксплуатационные) затраты") or
                    row_name.startswith("Количество загрязняющих веществ") or
                    row_name.startswith("Уловлено и обезврежено")):
                    
                    # Если это заголовок "Выброшено... - всего", обрабатываем отдельно
                    if "Всего, тыс. тонн" in row_name:
                        indicator_name = "Выброшено в атмосферу загрязняющих веществ - Всего, тыс. тонн"
                    else:
                        indicator_name = row_name
                    
                    indicators.add(indicator_name)
                    
                    # Проверяем следующую строку на наличие данных
                    if i+1 < len(lines):
                        next_line = lines[i+1]
                        next_parts = next_line.split(';')
                        if not next_parts[0].strip():  # Если первая колонка пустая - данные в следующей строке
                            data_line = next_parts
                            i += 1  # Пропускаем строку с данными
                        else:
                            data_line = parts
                    else:
                        data_line = parts
                    
                    # Обрабатываем данные
                    for year_idx, year in enumerate(years):
                        if year_idx + 1 < len(data_line):
                            value = data_line[year_idx + 1].strip()
                            if value:
                                try:
                                    clean_value = int(value) if value.isdigit() else float(value.replace(',', '.'))
                                    if year not in result[current_region]:
                                        result[current_region][year] = {}
                                    result[current_region][year][indicator_name] = clean_value
                                except ValueError:
                                    if year not in result[current_region]:
                                        result[current_region][year] = {}
                                    result[current_region][year][indicator_name] = value
                    i += 1
                    continue
                
                # Для подкатегорий выбросов (диоксид серы, углеводороды и т.д.)
                elif (row_name in ["Твердые вещества, тыс. тонн", 
                                 "Газообразные и жидкие вещества, тыс. тонн",
                                 "Диоксид серы, тыс. тонн",
                                 "Оксид углерода, тыс. тонн",
                                 "Оксиды азота (в пересчете на NO2), тыс. тонн",
                                 "Углеводороды, тыс. тонн",
                                 "Летучие органические соединения (ЛОС), тонн",
                                 "Прочие газообразные и жидкие вещества, тыс. тонн"]):
                    
                    indicator_name = f"Выброшено в атмосферу - {row_name}"
                    indicators.add(indicator_name)
                    
                    # Проверяем следующую строку на наличие данных
                    if i+1 < len(lines):
                        next_line = lines[i+1]
                        next_parts = next_line.split(';')
                        if not next_parts[0].strip():  # Если первая колонка пустая - данные в следующей строке
                            data_line = next_parts
                            i += 1  # Пропускаем строку с данными
                        else:
                            data_line = parts
                    else:
                        data_line = parts
                    
                    for year_idx, year in enumerate(years):
                        if year_idx + 1 < len(data_line):
                            value = data_line[year_idx + 1].strip()
                            if value:
                                try:
                                    clean_value = int(value) if value.isdigit() else float(value.replace(',', '.'))
                                    if year not in result[current_region]:
                                        result[current_region][year] = {}
                                    result[current_region][year][indicator_name] = clean_value
                                except ValueError:
                                    if year not in result[current_region]:
                                        result[current_region][year] = {}
                                    result[current_region][year][indicator_name] = value
                    i += 1
                    continue
            
            i += 1

        # Проверяем результат
        found_units = set(result.keys())
        expected_units = set(f"{v} {k}" for k, v in target_regions.items())
        
        missing = expected_units - found_units
        if missing:
            print(f"Предупреждение: не найдены данные для {len(missing)} административных единиц:")
            for unit in sorted(missing):
                print(f" - {unit}")

        # Сохранение результатов
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        # Вывод информации
        print(f"Успешно обработано административных единиц: {len(result)}")
        print(f"Найдено показателей: {len(indicators)}")
        total_expected = len(target_regions)
        if len(result) == total_expected:
            print(f"Все {total_expected} административных единиц найдены!")
        else:
            print(f"Найдено данных для {len(result)} из {total_expected} административных единиц")
        
        # Дополнительная проверка данных
        empty_regions = [region for region in result if not result[region]]
        if empty_regions:
            print(f"\nПредупреждение: нет данных для следующих регионов:")
            for region in empty_regions:
                print(f" - {region}")
        
    except Exception as e:
        print(f"Ошибка обработки: {str(e)}")

if __name__ == '__main__':
    process_environmental_protection_data()