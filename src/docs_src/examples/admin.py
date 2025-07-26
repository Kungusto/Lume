add_genre_example = {
    "1": {"summary": "Фэнтези", "value": {"title": "Фэнтези"}},
    "2": {"summary": "Стимпанк", "value": {"title": "Стимпанк"}},
    "3": {"summary": "Кринж-литература", "value": {"title": "Кринж-литература"}},
}

edit_tag_example = {
    "1": {"summary": "Программирование", "value": {"title_tag": "Программирование"}},
    "2": {"summary": "Путешествия", "value": {"title_tag": "Путешествия"}},
    "3": {"summary": "Психология", "value": {"title_tag": "Психология"}},
    "4": {"summary": "Музыка", "value": {"title_tag": "Музыка"}},
}

add_reason_example = {
    "1": {"summary": "Плагиат", "value": {"title": "Плагиат"}},
    "2": {"summary": "Спам", "value": {"title": "Спам"}},
    "3": {"summary": "Нарушение правил", "value": {"title": "Нарушение правил"}},
}

ban_user_by_id_example = {
    "1": {
        "summary": "Забанить до 2030 года",
        "value": {
            "ban_until": "2030-01-01T00:00:00.000000Z",
            "comment": "Вы забанены до 2030 года :o",
        },
    },
    "2": {
        "summary": "Забанить до 2050 года",
        "value": {
            "ban_until": "2050-01-01T00:00:00.000000Z",
            "comment": "Вы забанены до 2050 года :O",
        },
    },
}

get_statements_by_date_example = {
    "1": {"summary": "1 день", "value": {"interval": "P1D"}},
    "2": {"summary": "3 дня", "value": {"interval": "P3D"}},
    "3": {"summary": "7 дней (неделя)", "value": {"interval": "P7D"}},
    "4": {"summary": "14 дней (2 недели)", "value": {"interval": "P14D"}},
    "5": {"summary": "30 дней (месяц)", "value": {"interval": "P30D"}},
    "6": {"summary": "90 дней (3 месяца)", "value": {"interval": "P90D"}},
    "7": {"summary": "180 дней (полгода)", "value": {"interval": "P180D"}},
    "8": {"summary": "365 дней (год)", "value": {"interval": "P365D"}},
    "9": {"summary": "1 год (альтернативная запись)", "value": {"interval": "P1Y"}},
    "10": {"summary": "2 года", "value": {"interval": "P2Y"}},
    "11": {"summary": "1 месяц", "value": {"interval": "P1M"}},
    "12": {"summary": "6 месяцев", "value": {"interval": "P6M"}},
    "13": {"summary": "1 неделя (альтернативная запись)", "value": {"interval": "P1W"}},
    "14": {"summary": "2 недели", "value": {"interval": "P2W"}},
}
