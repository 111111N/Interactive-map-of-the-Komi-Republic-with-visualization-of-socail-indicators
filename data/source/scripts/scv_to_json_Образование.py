import json
from pathlib import Path

def process_education_data():
    # Настройка путей
    base_dir = Path(__file__).parent
    input_file = base_dir / 'Образование.csv'
    output_file = base_dir / 'sorted' / 'education_data.json'
    
    # Создаем папку для результатов
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Все административные единицы
    target_regions = {
        # Городские округа (обратите внимание - только названия городов)
        "Сыктывкар": "Городской округ",
        "Воркута": "Городской округ",
        "Вуктыл": "Городской округ", 
        "Инта": "Городской округ",
        "Усинск": "Городской округ",
        "Ухта": "Городской округ",
        
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
        indicator_name = "Численность обучающихся"
        
        i = 0
        while i < len(lines):
            line = lines[i]
            parts = line.split(';')
            row_name = parts[0].strip()
            
            # Пропускаем заголовки
            if not row_name or 'значение показателя за год' in row_name:
                i += 1
                continue
                
            # Ищем название региона (для муниципальных районов и городских округов)
            for region, region_type in target_regions.items():
                # Для муниципальных районов ищем "Муниципальный район"
                if region_type == "Муниципальный район" and f"Муниципальный район {region}" in row_name:
                    current_region = f"{region_type} {region}"
                    if current_region not in result:
                        result[current_region] = {}
                    break
                # Для городских округов ищем просто название города
                elif region_type == "Городской округ" and region in row_name and "Городской округ" not in row_name:
                    current_region = f"{region_type} {region}"
                    if current_region not in result:
                        result[current_region] = {}
                    break
            
            # Если нашли регион, ищем данные
            if current_region:
                # Ищем строку с показателем
                if "Численность обучающихся" in row_name and "организациях" in row_name:
                    # Ищем следующую строку, начинающуюся с ';' и содержащую данные
                    j = i + 1
                    while j < len(lines):
                        data_line = lines[j]
                        if data_line.startswith(';'):
                            data_values = [v.strip() for v in data_line.split(';')[1:13]]  # 2006-2017
                            
                            # Проверяем, что это действительно данные (содержат числа)
                            if any(v.isdigit() for v in data_values if v):
                                for year_idx, year in enumerate(years):
                                    if year_idx < len(data_values) and data_values[year_idx] and data_values[year_idx].isdigit():
                                        value = int(data_values[year_idx])
                                        if year not in result[current_region]:
                                            result[current_region][year] = {}
                                        result[current_region][year][indicator_name] = value
                                break
                        j += 1
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
        if len(result) == 20:
            print("Все 20 административных единиц найдены!")
        else:
            print(f"Найдено данных для {len(result)} из 20 административных единиц")
        
    except Exception as e:
        print(f"Ошибка обработки: {str(e)}")

if __name__ == '__main__':
    process_education_data()