import json
from pathlib import Path

def process_accommodation_data():
    base_dir = Path(__file__).parent
    input_file = base_dir / 'Коллективные средства размещения.csv'
    output_file = base_dir / 'sorted' / 'accommodation_data.json'
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Все административные единицы
    regions = {
        # Городские округа
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

    result = {f"{typ} {name}": {} for name, typ in regions.items()}

    try:
        with open(input_file, 'r', encoding='windows-1251') as f:
            lines = f.readlines()

        current_region = None
        current_indicator = None
        years = []
        header_processed = False

        for line in lines:
            line = line.strip()
            if not line:
                continue

            parts = line.split(';')
            parts = [p.strip() for p in parts if p.strip()]
            
            # Пропускаем строки с заголовками
            if "значение показателя за год" in line:
                header_processed = False
                continue
                
            # Обрабатываем заголовок с годами
            if not header_processed and line.startswith(';'):
                years = [year for year in parts[1:] if year and year.isdigit()]
                header_processed = True
                continue
            
            # Определяем регион
            for name, typ in regions.items():
                full_name = f"{typ} {name}"
                
                # Для муниципальных районов
                if typ == "Муниципальный район":
                    if f"Муниципальный район {name}" in parts[0]:
                        current_region = full_name
                        break
                
                # Для городских округов
                elif name in parts[0] and "Муниципальный район" not in parts[0]:
                    current_region = full_name
                    break
            
            # Определяем показатель
            indicators = [
                "Число коллективных средств размещения, единица",
                "Число мест в коллективных средствах размещения, единица",
                "Численность размещенных лиц в коллективных средствах размещения, единица",
                "Число ночевок в коллективных средствах размещения, единица",
                "Число номеров в коллективных средствах размещения, единица"
            ]
            
            for indicator in indicators:
                if indicator in parts[0]:
                    current_indicator = indicator
                    break
            
            # Обрабатываем данные
            if current_region and current_indicator and len(parts) > 1:
                for i, value in enumerate(parts[1:]):
                    if i < len(years) and value:
                        try:
                            year = years[i]
                            num_value = int(value) if value.isdigit() else value
                            if year not in result[current_region]:
                                result[current_region][year] = {}
                            result[current_region][year][current_indicator] = num_value
                        except ValueError:
                            pass
                current_indicator = None

        # Удаляем пустые записи
        result = {k: v for k, v in result.items() if v}

        # Проверяем результат
        found = set(result.keys())
        expected = set(f"{typ} {name}" for name, typ in regions.items())
        missing = expected - found
        
        if missing:
            print(f"Не найдены данные для {len(missing)} регионов:")
            for m in sorted(missing):
                print(f" - {m}")
        
        print(f"\nУспешно обработано: {len(result)} из {len(regions)} регионов")
        
        # Выводим пример данных
        print("\nПример извлеченных данных:")
        for region, data in list(result.items())[:3]:
            print(f"{region}:")
            print(json.dumps(data, ensure_ascii=False, indent=2))
            print()

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
            
    except Exception as e:
        print(f"Ошибка: {str(e)}")

if __name__ == '__main__':
    process_accommodation_data()