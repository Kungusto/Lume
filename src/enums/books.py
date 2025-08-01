from enum import Enum as pyEnum


class LanguagesEnum(pyEnum):
    ENGLISH = "English"
    RUSSIAN = "Russian"
    SPANISH = "Spanish"
    FRENCH = "French"
    GERMAN = "German"
    CHINESE = "Chinese"
    JAPANESE = "Japanese"
    KOREAN = "Korean"
    PORTUGUESE = "Portuguese"
    ITALIAN = "Italian"
    ARABIC = "Arabic"
    HINDI = "Hindi"
    TURKISH = "Turkish"
    POLISH = "Polish"
    UKRAINIAN = "Ukrainian"


class RenderStatus(pyEnum):
    UPLOADED = "uploaded"  # Контент загружен, но ещё не рендерился
    RENDERING = "rendering"  # Идёт рендеринг
    READY = "ready"  # Успешно отрендерено
    FAILED = "failed"  # Ошибка рендеринга
