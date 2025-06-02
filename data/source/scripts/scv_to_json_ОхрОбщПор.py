import json
from pathlib import Path

def process_security_data():
    # Настройка путей
    base_dir = Path(__file__).parent
    input_file = base_dir / 'Организация охраны общественного порядка.csv'
    output_file = base_dir / 'sorted' / 'regions_data.json'
    
    # Создаем папку для результатов
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Все административные единицы
    target_regions = {
        # Городские округа
        "Сыктывкар": "Городской округ",
        "Воркута": "Муниципальный округ",
        "Вуктыл": "Муниципальный округ", 
        "Инта": "Муниципальный округ",
        "Усинск": "Муниципальный округ",
        "Ухта": "Муниципальный округ",
        
        # Муниципальные районы
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
        years = [str(y) for y in range(2006, 2018)]
        indicators = set()  # Для сбора всех уникальных показателей

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
                full_name = f"{region_type} {region}"
                
                # Для муниципальных районов
                if region_type == "Муниципальный район" and f"Муниципальный район {region}" in row_name:
                    current_region = full_name
                    region_found = True
                    break
                # Для городских округов
                elif region_type in ["Городской округ", "Муниципальный округ"] and region in row_name:
                    current_region = full_name
                    region_found = True
                    break
            
            if region_found:
                if current_region not in result:
                    result[current_region] = {}
                i += 1
                continue
            
            # Если это показатель и у нас есть текущий регион
            if current_region and ('Число' in row_name or 'Количество' in row_name):
                indicator = row_name.split('(')[0].strip()
                indicators.add(indicator)
                
                # Обрабатываем данные для всех годов
                for year_idx, year in enumerate(years):
                    if year_idx + 1 < len(parts):
                        value = parts[year_idx + 1].strip()
                        if value:
                            try:
                                # Пробуем преобразовать в int, затем в float
                                clean_value = int(value) if value.isdigit() else float(value.replace(',', '.'))
                                if year not in result[current_region]:
                                    result[current_region][year] = {}
                                result[current_region][year][indicator] = clean_value
                            except ValueError:
                                # Если не удалось преобразовать в число, сохраняем как строку
                                if year not in result[current_region]:
                                    result[current_region][year] = {}
                                result[current_region][year][indicator] = value
            
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
        if len(result) == 20:
            print("Все 20 административных единиц найдены!")
        else:
            print(f"Найдено данных для {len(result)} из 20 административных единиц")
        
    except Exception as e:
        print(f"Ошибка обработки: {str(e)}")

if __name__ == '__main__':
    process_security_data()