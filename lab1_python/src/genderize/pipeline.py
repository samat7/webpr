"""
Pipeline для обработки имен
Реализует паттерн Pipeline с Fan-out/Fan-in

Аналог ParseActivities и CreateActivities из Go примера
"""

from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, List, Optional
from .client import GenderizeClient, GenderizeNetworkError
from .models import GenderPrediction, ProcessingResult


class PipelineStage(ABC):
    """Базовый класс для этапа pipeline"""
    
    @abstractmethod
    def process(self, data: Any) -> Any:
        """Обработка данных на этом этапе"""
        pass


class ParseNamesStage(PipelineStage):
    """
    Этап 1: Парсинг и валидация имен
    Преобразует список строк в структурированные данные
    """
    
    def process(self, names: List[str]) -> List[dict]:
        """
        Парсинг имен
        
        Args:
            names: Список имен (строки)
            
        Returns:
            Список словарей с индексом и именем
        """
        result = []
        for idx, name in enumerate(names):
            if name and name.strip():
                result.append({
                    'index': idx,
                    'name': name.strip()
                })
        return result


class FetchGenderStage(PipelineStage):
    """
    Этап 2: Получение данных из API (Fan-out/Fan-in)
    
    Fan-out: распределяем запросы между воркерами
    Fan-in: собираем результаты обратно в правильном порядке
    """
    
    def __init__(self, workers: int = 5):
        """
        Args:
            workers: Количество параллельных воркеров
        """
        self.workers = workers
    
    def process(self, names_data: List[dict]) -> List[ProcessingResult]:
        """
        Параллельное получение предсказаний пола
        
        Args:
            names_data: Список словарей с индексом и именем
            
        Returns:
            Список результатов обработки
        """
        if not names_data:
            return []
        
        client = GenderizeClient()
        results = [None] * len(names_data)
        
        # Fan-out: создаем пул воркеров и распределяем задачи
        with ThreadPoolExecutor(max_workers=self.workers) as executor:
            # Отправляем все задачи на выполнение
            future_to_data = {}
            for data in names_data:
                future = executor.submit(
                    self._fetch_single,
                    client,
                    data['index'],
                    data['name']
                )
                future_to_data[future] = data
            
            # Fan-in: собираем результаты по мере завершения
            for future in as_completed(future_to_data):
                data = future_to_data[future]
                idx = data['index']
                
                try:
                    result = future.result()
                    results[idx] = result
                except Exception as e:
                    results[idx] = ProcessingResult(
                        index=idx,
                        error=str(e)
                    )
        
        return results
    
    def _fetch_single(
        self,
        client: GenderizeClient,
        index: int,
        name: str
    ) -> ProcessingResult:
        """
        Получение предсказания для одного имени
        
        Args:
            client: Клиент API
            index: Индекс имени в исходном списке
            name: Имя для обработки
            
        Returns:
            Результат обработки
        """
        try:
            prediction = client.get_gender(name)
            return ProcessingResult(
                index=index,
                prediction=prediction
            )
        except GenderizeNetworkError as e:
            return ProcessingResult(
                index=index,
                error=f"Ошибка API: {e}"
            )
        except Exception as e:
            return ProcessingResult(
                index=index,
                error=f"Неожиданная ошибка: {e}"
            )


class FormatResultsStage(PipelineStage):
    """
    Этап 3: Форматирование результатов
    Преобразует сырые данные в отформатированный вывод
    """
    
    def process(self, results: List[ProcessingResult]) -> List[ProcessingResult]:
        """
        Форматирование результатов
        
        На этом этапе результаты уже готовы,
        но можно добавить дополнительную обработку
        
        Args:
            results: Список результатов обработки
            
        Returns:
            Отформатированный список результатов
        """
        # В данном случае просто возвращаем результаты как есть
        # Можно добавить сортировку, фильтрацию и т.д.
        return results


class Pipeline:
    """
    Конвейер обработки данных
    
    Реализует паттерн Pipeline:
    1. Данные проходят через последовательность этапов
    2. Каждый этап выполняет свою задачу
    3. Результат одного этапа передается на следующий
    
    Этапы:
    - ParseNamesStage: парсинг и валидация имен
    - FetchGenderStage: получение данных из API (с fan-out/fan-in)
    - FormatResultsStage: форматирование результатов
    """
    
    def __init__(self, stages: List[PipelineStage]):
        """
        Args:
            stages: Список этапов pipeline
        """
        self.stages = stages
    
    def run(self, input_data: Any) -> Any:
        """
        Запуск pipeline
        
        Args:
            input_data: Входные данные
            
        Returns:
            Результат обработки после всех этапов
        """
        data = input_data
        
        for stage in self.stages:
            data = stage.process(data)
        
        return data
    
    def add_stage(self, stage: PipelineStage) -> 'Pipeline':
        """
        Добавление этапа в pipeline
        
        Args:
            stage: Новый этап
            
        Returns:
            self для цепочки вызовов
        """
        self.stages.append(stage)
        return self