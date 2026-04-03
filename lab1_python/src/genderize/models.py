"""
Модели данных для Genderize API
Аналог internal/activity/types.go из Go примера
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class GenderPrediction:
    """
    Результат предсказания возраста по имени
    Соответствует ответу API agify.io
    """
    name: str
    age: Optional[int]  # предсказанный возраст или None
    count: int  # количество записей в выборке
    
    @classmethod
    def from_api_response(cls, data: dict) -> 'GenderPrediction':
        """
        Создает объект из ответа API
        
        Пример ответа API:
        {
            "name": "john",
            "age": 72,
            "count": 165344
        }
        """
        return cls(
            name=data.get('name', ''),
            age=data.get('age'),
            count=data.get('count', 0)
        )
    
    def is_reliable(self, min_count: int = 100) -> bool:
        """Проверяет, достаточно ли надежно предсказание"""
        return self.count >= min_count
    
    def __str__(self) -> str:
        age_str = str(self.age) if self.age else "неизвестен"
        return f"{self.name}: {age_str} лет (выборка: {self.count:,})"


@dataclass
class NameInput:
    """
    Входные данные - имя для обработки
    Аналог activity.Activity из Go примера
    """
    index: int
    name: str
    
    def validate(self) -> Optional[str]:
        """Валидация имени, возвращает ошибку или None"""
        if not self.name:
            return "Имя не может быть пустым"
        if len(self.name) > 100:
            return "Имя слишком длинное (максимум 100 символов)"
        if not all(c.isalpha() or c.isspace() or c in "'-" for c in self.name):
            return "Имя содержит недопустимые символы"
        return None


@dataclass
class ProcessingResult:
    """
    Результат обработки одного имени
    Аналог ParsedActivity из Go примера
    """
    index: int
    prediction: Optional[GenderPrediction] = None
    error: Optional[str] = None
    
    @property
    def success(self) -> bool:
        return self.error is None and self.prediction is not None