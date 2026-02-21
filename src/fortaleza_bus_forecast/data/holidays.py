"""
Holiday definitions for Fortaleza, Ceará, Brazil.

Includes Brazilian national holidays + Ceará/Fortaleza local holidays for
2015, 2018, and 2020. Format: list of [name, day, month].
"""

# ── 2015 ──
FERIADOS_2015 = [
    ["Ano Novo", 1, 1],
    ["Carnaval", 16, 2],
    ["Carnaval", 17, 2],
    ["Dia de São José", 19, 3],
    ["Data Magna", 25, 3],
    ["Sexta-Feira Santa", 3, 4],
    ["Aniversário de Fortaleza", 13, 4],
    ["Tiradentes", 21, 4],
    ["Dia do Trabalho", 1, 5],
    ["Corpus Christi", 4, 6],
    ["N. Senhora da Assunção", 27, 5],
    ["Independência do Brasil", 7, 9],
    ["N. Senhora de Aparecida", 12, 10],
    ["Dia de Finados", 2, 11],
    ["Proclamação da Republica", 15, 11],
    ["Natal", 25, 12],
]

VESPERAS_2015 = [
    ["Ano Novo", 31, 12],
    ["Carnaval", 11, 2],
    ["Dia de São José", 18, 3],
    ["Data Magna", 24, 3],
    ["Sexta-Feira Santa", 9, 4],
    ["Aniversário de Fortaleza", 12, 4],
    ["Tiradentes", 20, 4],
    ["Dia do Trabalho", 30, 4],
    ["N. Senhora da Assunção", 26, 5],
    ["Independência do Brasil", 6, 9],
    ["N. Senhora de Aparecida", 11, 10],
    ["Dia de Finados", 1, 11],
    ["Proclamação da Republica", 14, 11],
    ["Natal", 24, 12],
]

# ── 2018 ──
FERIADOS_2018 = [
    ["Ano Novo", 1, 1],
    ["Carnaval", 12, 2],
    ["Carnaval", 13, 2],
    ["Dia de São José", 19, 3],
    ["Data Magna", 25, 3],
    ["Paixao de Cristo", 30, 3],
    ["Sexta-Feira Santa", 10, 4],
    ["Aniversário de Fortaleza", 13, 4],
    ["Tiradentes", 21, 4],
    ["Dia do Trabalho", 1, 5],
    ["Corpus Christi", 28, 5],
    ["N. Senhora da Assunção", 27, 5],
    ["Independência do Brasil", 7, 9],
    ["N. Senhora de Aparecida", 12, 10],
    ["Dia de Finados", 2, 11],
    ["Proclamação da Republica", 15, 11],
    ["Natal", 25, 12],
]

VESPERAS_2018 = [
    ["Ano Novo", 31, 12],
    ["Carnaval", 11, 2],
    ["Dia de São José", 18, 3],
    ["Data Magna", 24, 3],
    ["Sexta-Feira Santa", 9, 4],
    ["Aniversário de Fortaleza", 12, 4],
    ["Tiradentes", 20, 4],
    ["Dia do Trabalho", 30, 4],
    ["N. Senhora da Assunção", 26, 5],
    ["Independência do Brasil", 6, 9],
    ["N. Senhora de Aparecida", 11, 10],
    ["Dia de Finados", 1, 11],
    ["Proclamação da Republica", 14, 11],
    ["Natal", 24, 12],
]

# ── 2020 ──
FERIADOS_2020 = [
    ["Ano Novo", 1, 1],
    ["Carnaval", 24, 2],
    ["Carnaval", 25, 2],
    ["Carnaval", 26, 2],
    ["Dia de São José", 19, 3],
    ["Data Magna", 25, 3],
    ["Sexta-Feira Santa", 10, 4],
    ["Aniversário de Fortaleza", 13, 4],
    ["Tiradentes", 21, 4],
    ["Dia do Trabalho", 1, 5],
    ["Corpus Christi", 28, 5],
    ["N. Senhora da Assunção", 27, 5],
    ["Independência do Brasil", 7, 9],
    ["N. Senhora de Aparecida", 12, 10],
    ["Dia de Finados", 2, 11],
    ["Proclamação da Republica", 15, 11],
    ["Natal", 25, 12],
]

VESPERAS_2020 = [
    ["Ano Novo", 31, 12],
    ["Carnaval", 23, 2],
    ["Dia de São José", 18, 3],
    ["Data Magna", 24, 3],
    ["Sexta-Feira Santa", 9, 4],
    ["Aniversário de Fortaleza", 12, 4],
    ["Tiradentes", 20, 4],
    ["Dia do Trabalho", 30, 4],
    ["N. Senhora da Assunção", 26, 5],
    ["Independência do Brasil", 6, 9],
    ["N. Senhora de Aparecida", 11, 10],
    ["Dia de Finados", 1, 11],
    ["Proclamação da Republica", 14, 11],
    ["Natal", 24, 12],
]

# ── Registry ──
_HOLIDAYS = {2015: FERIADOS_2015, 2018: FERIADOS_2018, 2020: FERIADOS_2020}
_EVES = {2015: VESPERAS_2015, 2018: VESPERAS_2018, 2020: VESPERAS_2020}

DAY_OF_WEEK_PT = {
    0: "Domingo",
    1: "Segunda",
    2: "Terca",
    3: "Quarta",
    4: "Quinta",
    5: "Sexta",
    6: "Sabado",
}


def get_holidays(year: int) -> list:
    """Return holiday list [[name, day, month], ...] for a given year."""
    if year not in _HOLIDAYS:
        raise ValueError(f"No holiday data for year {year}. Available: {list(_HOLIDAYS.keys())}")
    return _HOLIDAYS[year]


def get_holiday_eves(year: int) -> list:
    """Return holiday-eve list [[name, day, month], ...] for a given year."""
    if year not in _EVES:
        raise ValueError(f"No holiday-eve data for year {year}. Available: {list(_EVES.keys())}")
    return _EVES[year]


def is_holiday(day: int, month: int, year: int) -> bool:
    """Check if a specific date is a holiday."""
    return any(d == day and m == month for _, d, m in get_holidays(year))


def is_holiday_eve(day: int, month: int, year: int) -> bool:
    """Check if a specific date is a holiday eve."""
    return any(d == day and m == month for _, d, m in get_holiday_eves(year))
