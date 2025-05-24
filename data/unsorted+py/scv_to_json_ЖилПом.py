import json
from pathlib import Path

def process_housing_data():
    base_dir = Path(__file__).parent
    input_file = base_dir / 'Жилые помещения.csv'
    output_file = base_dir / 'sorted' / 'housing_data.json'
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Все административные единицы верхнего уровня
    target_regions = {
        # Городские округа (исключаем Вуктыл)
        "Сыктывкар": "Городской округ",
        "Воркута": "Городской округ",
        "Инта": "Городской округ",
        "Усинск": "Городской округ",
        "Ухта": "Городской округ",
        
        # Муниципальные районы (включаем Вуктыл только здесь)
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

    result = {}

    try:
        with open(input_file, 'r', encoding='windows-1251') as f:
            content = f.read()

        # Разделяем на секции по показателям
        sections = content.split('значение показателя за год')
        
        for section in sections[1:]:  # Первая секция - заголовок
            lines = [line.strip() for line in section.split('\n') if line.strip()]
            
            # Получаем годы из первой строки
            years = [year.strip() for year in lines[0].split(';')[1:] if year.strip()]
            
            current_region = None
            current_indicator = None
            
            for line in lines[1:]:
                parts = [p.strip() for p in line.split(';') if p.strip()]
                if not parts:
                    continue
                
                # Проверяем, является ли строка регионом верхнего уровня
                found_region = None
                
                # Проверяем муниципальные районы
                if parts[0].startswith('Муниципальный район '):
                    name = parts[0][20:]  # Убираем "Муниципальный район "
                    name = name.split(' (')[0]  # Убираем возможные дополнения в скобках
                    if name in target_regions and target_regions[name] == "Муниципальный район":
                        current_region = f"Муниципальный район {name}"
                        found_region = current_region
                
                # Проверяем городские округа (кроме Вуктыла)
                elif not parts[0].startswith('Вуктыл') and any(
                    parts[0].startswith(name) for name in target_regions 
                    if target_regions[name] == "Городской округ"
                ):
                    name = parts[0].split(' (')[0]  # Убираем возможные дополнения в скобках
                    if name in target_regions and target_regions[name] == "Городской округ":
                        current_region = f"Городской округ {name}"
                        found_region = current_region
                
                if found_region:
                    if current_region not in result:
                        result[current_region] = {}
                    continue
                
                # Проверяем показатели
                indicators = [
                    "Переселено из ветхих жилых домов за отчетный год, человек",
                    "Общая площадь жилых помещений, тыс. кв.м, тысяча метров квадратных"
                ]
                
                for indicator in indicators:
                    if indicator in parts[0]:
                        current_indicator = indicator
                        break
                
                # Обрабатываем данные
                if current_region and current_indicator:
                    # Проверяем, что это строка с данными для региона (начинается с типа региона)
                    if parts[0] in ["Муниципальный район", "Городской округ", "Городской округ, городской округ с внутригородским делением"]:
                        for i, value in enumerate(parts[1:]):
                            if i < len(years) and value:
                                try:
                                    year = years[i]
                                    try:
                                        num_value = int(value) if value.isdigit() else float(value.replace(',', '.'))
                                    except ValueError:
                                        num_value = value
                                    
                                    if year not in result[current_region]:
                                        result[current_region][year] = {}
                                    result[current_region][year][current_indicator] = num_value
                                except Exception as e:
                                    print(f"Ошибка обработки значения '{value}': {str(e)}")
                                    pass

        # Удаляем пустые записи
        result = {k: v for k, v in result.items() if v}
        
        # Проверяем результат
        found = set(result.keys())
        expected = set(f"{typ} {name}" for name, typ in target_regions.items())
        
        missing = expected - found
        
        if missing:
            print(f"Не найдены данные для {len(missing)} регионов:")
            for m in sorted(missing):
                print(f" - {m}")
        
        print(f"\nУспешно обработано: {len(result)} из {len(expected)} регионов")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
            
    except Exception as e:
        print(f"Ошибка: {str(e)}")

if __name__ == '__main__':
    process_housing_data()