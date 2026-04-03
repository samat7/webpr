"""
Genderize CLI - пакет для определения пола по именам
"""

from .genderize import (
    GenderizeClient,
    GenderPrediction,
    Pipeline,
    ParseNamesStage,
    FetchGenderStage,
    FormatResultsStage
)

__all__ = [
    'GenderizeClient',
    'GenderPrediction',
    'Pipeline',
    'ParseNamesStage',
    'FetchGenderStage',
    'FormatResultsStage'
]