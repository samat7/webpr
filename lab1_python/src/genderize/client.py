"""
HTTP клиент для Genderize API
Аналог internal/github/client.go из Go примера
"""

import urllib.request
import urllib.parse
import urllib.error
import json
from typing import Optional
from .models import GenderPrediction


class GenderizeAPIError(Exception):
    """Базовое исключение для ошибок API"""
    pass


class GenderizeNetworkError(GenderizeAPIError):
    """Ошибка сети при запросе к API"""
    pass


class GenderizeClient:
    """
    Клиент для работы с Agify API
    https://agify.io/
    
    Аналог GithubClient из Go примера
    """
    
    BASE_URL = "https://api.agify.io/"
    TIMEOUT = 10  # Увеличили таймаут до 10 секунд
    
    def __init__(self, timeout: int = TIMEOUT):
        self.timeout = timeout
    
    def get_gender(self, name: str) -> GenderPrediction:
        """
        Получает предсказание пола по имени
        
        Args:
            name: Имя для определения пола
            
        Returns:
            GenderPrediction с результатом
            
        Raises:
            GenderizeNetworkError: При ошибке сети или API
        """
        if not name or not name.strip():
            raise GenderizeNetworkError("Имя не может быть пустым")
        
        encoded_name = urllib.parse.quote(name.strip())
        url = f"{self.BASE_URL}?name={encoded_name}"
        
        try:
            request = urllib.request.Request(
                url,
                headers={
                    'User-Agent': 'GenderizeCLI/1.0',
                    'Accept': 'application/json'
                }
            )
            
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                if response.status != 200:
                    raise GenderizeNetworkError(
                        f"API вернул статус {response.status}"
                    )
                
                data = response.read().decode('utf-8')
                json_data = json.loads(data)
                
                return GenderPrediction.from_api_response(json_data)
                
        except urllib.error.HTTPError as e:
            raise GenderizeNetworkError(
                f"HTTP ошибка {e.code}: {e.reason}"
            )
        except urllib.error.URLError as e:
            raise GenderizeNetworkError(
                f"Ошибка соединения: {e.reason}"
            )
        except json.JSONDecodeError as e:
            raise GenderizeNetworkError(
                f"Ошибка парсинга JSON: {e}"
            )
        except Exception as e:
            raise GenderizeNetworkError(
                f"Неожиданная ошибка: {e}"
            )
    
    def get_genders_batch(self, names: list) -> list:
        """
        Получает предсказания для нескольких имен за один запрос
        API поддерживает batch запросы: /?name[]=john&name[]=maria
        """
        if not names:
            return []
        
        params = [('name[]', name.strip()) for name in names if name.strip()]
        query_string = urllib.parse.urlencode(params)
        url = f"{self.BASE_URL}?{query_string}"
        
        try:
            request = urllib.request.Request(
                url,
                headers={
                    'User-Agent': 'GenderizeCLI/1.0',
                    'Accept': 'application/json'
                }
            )
            
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                if response.status != 200:
                    raise GenderizeNetworkError(
                        f"API вернул статус {response.status}"
                    )
                
                data = response.read().decode('utf-8')
                json_data = json.loads(data)
                
                if isinstance(json_data, list):
                    return [GenderPrediction.from_api_response(item) for item in json_data]
                else:
                    return [GenderPrediction.from_api_response(json_data)]
                    
        except urllib.error.HTTPError as e:
            raise GenderizeNetworkError(f"HTTP ошибка {e.code}: {e.reason}")
        except urllib.error.URLError as e:
            raise GenderizeNetworkError(f"Ошибка соединения: {e.reason}")
        except json.JSONDecodeError as e:
            raise GenderizeNetworkError(f"Ошибка парсинга JSON: {e}")
        except Exception as e:
            raise GenderizeNetworkError(f"Неожиданная ошибка: {e}")