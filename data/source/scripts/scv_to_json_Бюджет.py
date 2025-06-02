from pathlib import Path
import json
import re

def clean_region_name(name: str) -> str:
    # Удаляет скобки с содержимым, включая пробел перед скобкой
    return re.sub(r"\s*\(.*?\)", "", name).strip()

def process_budget_data():
    base_dir = Path(__file__).parent
    input_file = base_dir / 'Бюджет.csv'
    output_file = base_dir / 'sorted' / 'Бюджет_data.json'
    output_file.parent.mkdir(parents=True, exist_ok=True)

    target_regions = {
        "Сыктывкар": "Городской округ",
        "Воркута": "Городской округ",
        "Вуктыл": "Городской округ",
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

    indicators_to_extract = {
        "Расходы местного бюджета, фактически исполненные, тысяча рублей",
        "Доходы местного бюджета, фактически исполненные, тысяча рублей",
        "Расходы на развитие и поддержку малого предпринимательства, тысяча рублей",
        "Общий объем расходов консолидированного бюджета муниципального района, тысяча рублей"
    }

    result = {}
    current_region = None
    current_indicator = None
    years = []

    try:
        with open(input_file, 'r', encoding='windows-1251') as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]

        # Найти строку с годами
        for idx, line in enumerate(lines):
            parts = [p.strip() for p in line.split(';')]
            if any(p.isdigit() for p in parts):
                years = parts[1:]
                data_lines = lines[idx+1:]
                break

        i = 0
        while i < len(data_lines):
            line = data_lines[i]
            parts = [p.strip() for p in line.split(';')]

            # Если строка — регион (одна непустая ячейка и не показатель)
            if len([p for p in parts if p]) == 1 and parts[0] not in indicators_to_extract:
                region_candidate = parts[0]
                if region_candidate.strip().lower() != "всего" and region_candidate.strip() != "":
                    current_region = region_candidate
                i += 1
                continue

            # Если строка — название показателя
            if parts[0] in indicators_to_extract:
                current_indicator = parts[0]

                i += 1
                if i >= len(data_lines):
                    break
                values_line = data_lines[i]
                values_parts = [p.strip() for p in values_line.split(';')]

                if current_region:
                    region_name = current_region.strip()
                    if region_name in target_regions:
                        region_key = f"{target_regions[region_name]} {region_name}"
                    else:
                        region_key = region_name

                    # Очистка названия региона от скобок
                    region_key = clean_region_name(region_key)

                    vals_to_process = values_parts[1:] if values_parts[0] == "" else values_parts

                    for idx_y, val in enumerate(vals_to_process):
                        if idx_y >= len(years):
                            continue
                        year = years[idx_y]
                        val_clean = val.replace(",", ".").strip()
                        # Пропускаем пустые или нечисловые значения (пустая строка, дефис и т.п.)
                        if val_clean in ("", "-", "—", None):
                            continue
                        try:
                            parsed_val = float(val_clean) if '.' in val_clean else int(val_clean)
                        except ValueError:
                            continue  # Если не парсится — пропускаем

                        result.setdefault(region_key, {}).setdefault(year, {})[current_indicator] = parsed_val

            i += 1

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        print("✅ Успешно сохранено:", output_file)
        return result

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return {}

if __name__ == "__main__":
    process_budget_data()
