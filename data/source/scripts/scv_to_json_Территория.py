import json
from pathlib import Path

def process_territory_data():
    base_dir = Path(__file__).parent
    input_file = base_dir / 'Территория.csv'
    output_file = base_dir / 'sorted' / 'territory_data.json'
    output_file.parent.mkdir(parents=True, exist_ok=True)

    target_regions = {
        "Сыктывкар": "Городской округ",
        "Воркута": "Городской округ",
        "Инта": "Городской округ",
        "Усинск": "Городской округ",
        "Ухта": "Городской округ",
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

    indicators = [
        "Общая площадь земель муниципального образования, гектар",
        "Общая площадь застроенных земель, гектар",
        "Общая протяженность освещенных частей улиц, проездов, набережных (на конец года), километр",
        "Общая площадь улично-дорожной сети (улиц, проездов, набережных и т.п.), тысяча метров квадратных",
        "Протяженность автодорог общего пользования местного значения, на конец года, километр",
        "Площадь земель сельхозугодий муниципального образования, гектар, гектар",
        "Общая протяженность улиц, проездов, набережных (на конец года), километр",
        "Протяженность автодорог общего пользования местного значения, находящихся в собственности муниципальных образований на начало года, километр",
        "Количество автозаправочных станций (АЗС), расположенных на автомобильных дорогах общего пользования местного значения на конец года, единица",
        "Протяженность мостов, путепроводов и эстакад, расположенных на автомобильных дорогах общего пользования местного значения на конец года, погонный метр"
    ]

    result = {}

    try:
        with open(input_file, 'r', encoding='windows-1251') as f:
            content = f.read()

        sections = content.split('значение показателя за год')

        for section in sections[1:]:
            lines = [line.strip() for line in section.split('\n') if line.strip()]
            years = [y.strip() for y in lines[0].split(';')[1:] if y.strip()]

            current_region = None
            current_indicator = None

            i = 1
            while i < len(lines):
                line = lines[i]
                parts = [p.strip() for p in line.split(';')]

                if not parts:
                    i += 1
                    continue

                # Поиск региона
                found_region = None
                for name, typ in target_regions.items():
                    if name.lower() in parts[0].lower():
                        current_region = f"{typ} {name}"
                        found_region = current_region
                        break

                if found_region:
                    if current_region not in result:
                        result[current_region] = {}
                    i += 1
                    continue

                # Поиск индикатора
                matched = False
                for indicator in indicators:
                    if indicator in parts[0]:
                        current_indicator = indicator
                        matched = True
                        break

                # Попытка объединить со следующей строкой, если индикатор не найден
                if not matched and i + 1 < len(lines):
                    next_line_parts = [p.strip() for p in lines[i + 1].split(';')]
                    if next_line_parts:
                        combined = parts[0] + ' ' + next_line_parts[0]
                        for indicator in indicators:
                            if indicator in combined:
                                current_indicator = indicator
                                matched = True
                                i += 1
                                break

                # Сохраняем значения по годам
                if current_region and current_indicator:
                    for j, value in enumerate(parts[1:]):
                        if j < len(years) and value:
                            try:
                                year = years[j]
                                try:
                                    num_value = int(value) if value.isdigit() else float(value.replace(',', '.'))
                                except ValueError:
                                    num_value = value

                                if year not in result[current_region]:
                                    result[current_region][year] = {}

                                if current_indicator not in result[current_region][year]:
                                    result[current_region][year][current_indicator] = num_value
                            except Exception as e:
                                print(f"Ошибка обработки значения '{value}': {str(e)}")

                i += 1

        # Отфильтровать только регионы с данными
        result = {k: v for k, v in result.items() if v}

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
    process_territory_data()
