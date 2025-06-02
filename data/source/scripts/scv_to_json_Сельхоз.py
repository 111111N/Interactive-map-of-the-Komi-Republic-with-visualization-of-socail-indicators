from pathlib import Path
import json

def process_agriculture_csv():
    base_dir = Path(__file__).parent
    input_file = base_dir / 'Сельское хозяйство.csv'
    output_file = base_dir / 'ф_data.json'
    output_file.parent.mkdir(parents=True, exist_ok=True)

    target_regions = {
        "Сыктывкар": "Городской округ",
        "Воркута": "Городской округ",
        "Вуктыл": "Городской округ",
        "Инта": "Городской округ",
        "Усинск": "Городской округ",
        "Ухта": "Городской округ",

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

    skip_indicators = {
        "Поголовье скота и птицы на конец года, голова",
        "Производство продуктов животноводства, тонна",
        "Скот и птица на убой (в живом весе)"
    }

    # Индикаторы, которым надо добавить суффикс ", тонна"
    indicators_tonna_suffix = {
        "Скот и птица в живой массе",
        "Молоко"
    }

    extra_indicators = [
        "Скот и птица в живой массе",
        "Молоко",
        "Яйца, тысяча штук"
    ]

    result = {}
    current_region = None
    current_indicator = None
    years = []

    try:
        with open(input_file, encoding='windows-1251') as f:
            lines = [line.strip() for line in f if line.strip()]

        # Найдем строку с годами (начинается с ;2008;)
        for idx, line in enumerate(lines):
            if line.startswith(";2008;"):
                years = line.strip(';').split(';')
                data_start = idx + 1
                break
        else:
            raise ValueError("Не найдена строка с годами")

        i = data_start
        while i < len(lines):
            row = lines[i].split(';')
            first_col = row[0].strip()

            # Проверка на регион
            if any(reg in first_col for reg in target_regions.keys()):
                # Определяем регион
                for reg_name in target_regions.keys():
                    if reg_name in first_col:
                        current_region = f"{target_regions[reg_name]} {reg_name}"
                        current_indicator = None
                        break
                i += 1
                continue

            # Обработка дополнительных категорий, которые идут с названием и сразу значениями
            if current_region and first_col in extra_indicators:
                # Пропускаем, если показатель в skip_indicators
                if first_col in skip_indicators:
                    i += 1
                    continue

                data_values = row[1:]

                # При необходимости добавить суффикс ", тонна" к названию
                indicator_name = first_col
                if first_col in indicators_tonna_suffix:
                    indicator_name = first_col + ", тонна"

                for idx_year, val in enumerate(data_values):
                    if idx_year >= len(years):
                        break
                    year = years[idx_year]
                    val = val.strip()
                    if val == "":
                        val = None
                    else:
                        try:
                            val_num = float(val.replace(',', '.'))
                            if val_num.is_integer():
                                val_num = int(val_num)
                            val = val_num
                        except:
                            pass

                    if year not in result:
                        result[year] = {}
                    if current_region not in result[year]:
                        result[year][current_region] = {}
                    result[year][current_region][indicator_name] = val
                i += 1
                continue

            # Проверка на показатель (название)
            if first_col and not first_col[0].isdigit() and first_col != "" and not first_col.startswith('значение показателя за год'):
                current_indicator = first_col
                if current_indicator in skip_indicators:
                    i += 1
                    while i < len(lines):
                        nxt = lines[i].split(';')[0].strip()
                        if any(reg in nxt for reg in target_regions.keys()) or (nxt and not nxt[0].isdigit() and not nxt.startswith('значение')):
                            break
                        i += 1
                    continue
                i += 1
                continue

            # Если пустая первая колонка — это строки с данными для текущего показателя
            if current_region and current_indicator and first_col == "":
                data_values = row[1:]

                # Пропускаем, если показатель в skip_indicators
                if current_indicator in skip_indicators:
                    i += 1
                    continue

                # При необходимости добавить суффикс ", тонна" к названию
                indicator_name = current_indicator
                if current_indicator in indicators_tonna_suffix:
                    indicator_name = current_indicator + ", тонна"

                for idx_year, val in enumerate(data_values):
                    if idx_year >= len(years):
                        break
                    year = years[idx_year]
                    val = val.strip()
                    if val == "":
                        val = None
                    else:
                        try:
                            val_num = float(val.replace(',', '.'))
                            if val_num.is_integer():
                                val_num = int(val_num)
                            val = val_num
                        except:
                            pass

                    if year not in result:
                        result[year] = {}
                    if current_region not in result[year]:
                        result[year][current_region] = {}
                    result[year][current_region][indicator_name] = val
                i += 1
                continue

            i += 1

        # Транспонируем: из year->region->indicator в region->year->indicator
        transformed = {}
        for year, regions in result.items():
            for region, indicators in regions.items():
                if region not in transformed:
                    transformed[region] = {}
                if year not in transformed[region]:
                    transformed[region][year] = {}
                for indicator, val in indicators.items():
                    if (val is not None) and (not indicator.startswith("свеклоуборочные")):  # Добавляем проверку на None
                        transformed[region][year][indicator] = val

        # Сохраняем
        with open(output_file, 'w', encoding='utf-8') as f_out:
            json.dump(transformed, f_out, ensure_ascii=False, indent=2)

        print(f"✅ Данные успешно сохранены в {output_file}")
        return transformed

    except Exception as e:
        print(f"❌ Ошибка при обработке: {e}")
        return {}

if __name__ == "__main__":
    process_agriculture_csv()
