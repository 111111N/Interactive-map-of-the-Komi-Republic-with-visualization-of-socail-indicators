import json
from pathlib import Path

def process_municipal_property_data():
    # Настройка путей
    base_dir = Path(__file__).parent
    input_file = base_dir / 'Муниципальная собственность.csv'
    output_file = base_dir / 'sorted' / 'municipal_property_data.json'
    
    # Создаем папку для результатов
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Все административные единицы
    target_regions = {
        # Городские округа
        "Сыктывкар": "Городской округ",
        "Воркута": "Городской округ",
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
        years = [str(y) for y in range(2008, 2024)]  # Годы с 2008 по 2023
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
                # Для муниципальных районов
                if region_type == "Муниципальный район":
                    # Проверяем разные варианты написания
                    if (f"Муниципальный район {region}" in row_name or 
                        f"Муниципальный район {region} (" in row_name):
                        current_region = f"{region_type} {region}"
                        region_found = True
                        break
                # Для городских округов
                elif region_type == "Городской округ":
                    if region in row_name and "Городской округ" not in row_name:
                        current_region = f"{region_type} {region}"
                        region_found = True
                        break
            
            if region_found:
                if current_region not in result:
                    result[current_region] = {}
                i += 1
                continue
            
            # Если это категория основных фондов (например, "Здания", "Сооружения")
            if row_name and not any(x in row_name for x in ["Муниципальный район", "Городской округ"]):
                current_category = row_name.split('(')[0].strip()
                indicators.add(current_category)
                i += 1
                continue
            
            # Если это данные для текущего региона и категории
            if current_region and current_category and ("Муниципальный район" in row_name or "Городской округ" in row_name):
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
                                result[current_region][year][current_category] = clean_value
                            except ValueError:
                                # Если не удалось преобразовать в число, сохраняем как строку
                                if year not in result[current_region]:
                                    result[current_region][year] = {}
                                result[current_region][year][current_category] = value
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
        print(f"Найдено категорий основных фондов: {len(indicators)}")
        total_expected = len(target_regions)
        if len(result) == total_expected:
            print(f"Все {total_expected} административных единиц найдены!")
        else:
            print(f"Найдено данных для {len(result)} из {total_expected} административных единиц")
        
    except Exception as e:
        print(f"Ошибка обработки: {str(e)}")

if __name__ == '__main__':
    process_municipal_property_data()