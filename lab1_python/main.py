#!/usr/bin/env python3
"""
Genderize CLI - программа для определения пола по именам
Использует API https://genderize.io/
"""

import sys
import argparse
import signal
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Optional
from dataclasses import dataclass

from src.genderize.client import GenderizeClient
from src.genderize.models import GenderPrediction
from src.genderize.pipeline import Pipeline, ParseNamesStage, FetchGenderStage, FormatResultsStage


# Коды ошибок
ERR_INCORRECT_USAGE = 1
ERR_INTERNAL = 2
ERR_NETWORK = 3


@dataclass
class ProcessingResult:
    """Результат обработки имени"""
    index: int
    prediction: Optional[GenderPrediction] = None
    error: Optional[str] = None


def create_names_channel(names: List[str]):
    """
    Fan-out: Создает генератор для отправки имен в обработку
    Аналог CreateActivities из Go примера
    """
    for idx, name in enumerate(names):
        yield (idx, name)


def process_names_fan_out_fan_in(names: List[str], max_workers: int = 5) -> List[ProcessingResult]:
    """
    Fan-out/Fan-in: Параллельная обработка имен
    Аналог ParseActivities из Go примера
    
    Fan-out: распределяем имена между воркерами
    Fan-in: собираем результаты обратно
    """
    client = GenderizeClient()
    results = [None] * len(names)
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Fan-out: отправляем задачи на выполнение
        future_to_index = {}
        for idx, name in create_names_channel(names):
            future = executor.submit(client.get_gender, name)
            future_to_index[future] = idx
        
        # Fan-in: собираем результаты
        for future in as_completed(future_to_index):
            idx = future_to_index[future]
            try:
                prediction = future.result()
                results[idx] = ProcessingResult(index=idx, prediction=prediction)
            except Exception as e:
                results[idx] = ProcessingResult(index=idx, error=str(e))
    
    return results


def format_result(result: ProcessingResult) -> str:
    """
    Форматирование результата для вывода
    Аналог Print из Go примера
    """
    if result.error:
        return f"[ОШИБКА] {result.error}"
    
    pred = result.prediction
    age_str = str(pred.age) if pred.age else "неизвестен"
    reliability = "✓" if pred.is_reliable() else "⚠"
    
    return (
        f"Имя: {pred.name}\n"
        f"  Предсказанный возраст: {age_str} лет\n"
        f"  Количество в выборке: {pred.count:,}\n"
        f"  Надежность: {reliability}"
    )


def main():
    """Главная функция - точка входа в программу"""
    
    # Парсинг аргументов командной строки
    parser = argparse.ArgumentParser(
        description="Определение пола по именам с использованием API genderize.io",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python main.py John Mary Anna
  python main.py --workers 10 Ivan Olga Pierre
  python main.py --file names.txt
        """
    )
    
    parser.add_argument(
        'names',
        nargs='*',
        help='Имена для обработки'
    )
    
    parser.add_argument(
        '-f', '--file',
        type=str,
        help='Файл с именами (по одному на строку)'
    )
    
    parser.add_argument(
        '-w', '--workers',
        type=int,
        default=5,
        help='Количество параллельных воркеров (по умолчанию: 5)'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Подробный вывод с отладочной информацией'
    )
    
    args = parser.parse_args()
    
    # Получаем список имен
    names = []
    
    if args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                names = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print(f"Ошибка: файл '{args.file}' не найден", file=sys.stderr)
            sys.exit(ERR_INCORRECT_USAGE)
        except IOError as e:
            print(f"Ошибка чтения файла: {e}", file=sys.stderr)
            sys.exit(ERR_INTERNAL)
    elif args.names:
        names = args.names
    else:
        print("Ошибка: укажите имена или файл с именами", file=sys.stderr)
        parser.print_help(sys.stderr)
        sys.exit(ERR_INCORRECT_USAGE)
    
    if not names:
        print("Ошибка: список имен пуст", file=sys.stderr)
        sys.exit(ERR_INCORRECT_USAGE)
    
    # Обработка сигнала прерывания (Ctrl+C)
    interrupted = False
    
    def signal_handler(sig, frame):
        nonlocal interrupted
        interrupted = True
        print("\nПрерывание... завершаем работу.", file=sys.stderr)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        if args.verbose:
            print(f"Обработка {len(names)} имен с {args.workers} воркерами...")
            print("-" * 50)
        
        # Создаем и запускаем pipeline
        pipeline = Pipeline([
            ParseNamesStage(),
            FetchGenderStage(workers=args.workers),
            FormatResultsStage()
        ])
        
        results = pipeline.run(names)
        
        # Выводим результаты
        print("\n" + "=" * 50)
        print("РЕЗУЛЬТАТЫ ОПРЕДЕЛЕНИЯ ПОЛА")
        print("=" * 50 + "\n")
        
        for idx, result in enumerate(results):
            print(f"{idx + 1}.")
            print(format_result(result))
            print()
        
        # Статистика
        successful = sum(1 for r in results if r.error is None)
        failed = len(results) - successful
        
        print("-" * 50)
        print(f"Обработано: {len(results)} | Успешно: {successful} | Ошибок: {failed}")
        
    except KeyboardInterrupt:
        sys.exit(ERR_INTERNAL)
    except Exception as e:
        print(f"Внутренняя ошибка: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(ERR_INTERNAL)


if __name__ == "__main__":
    main()