"""
Genderize API Client Package
Пакет для работы с API genderize.io
"""

from .client import GenderizeClient
from .models import GenderPrediction
from .pipeline import Pipeline, ParseNamesStage, FetchGenderStage, FormatResultsStage

__all__ = [
    'GenderizeClient',
    'GenderPrediction',
    'Pipeline',
    'ParseNamesStage',
    'FetchGenderStage',
    'FormatResultsStage'
]