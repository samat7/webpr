#!/usr/bin/env python3
"""
Chat Server - Лабораторная работа 6
Простой чат-сервер с WebSocket поддержкой
"""

import asyncio
import json
import uuid
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import websockets
from urllib.parse import unquote

# Хранилище комнат и подключений
rooms = {}  # room_id -> {clients: set, messages: list}
users = {}  # token -> {username, room_id, websocket}


class ChatRoom:
    """Комната чата"""
    
    def __init__(self, room_id: str):
        self.room_id = room_id
        self.clients = set()  # Множество WebSocket соединений
        self.messages = []    # История сообщений
    
    def add_client(self, websocket, username: str):
        """Добавить клиента в комнату"""
        self.clients.add(websocket)
        # Отправляем историю сообщений новому клиенту
        for msg in self.messages[-50:]:  # Последние 50 сообщений
            asyncio.create_task(websocket.send(json.dumps(msg)))
    
    def remove_client(self, websocket):
        """Удалить клиента из комнаты"""
        self.clients.discard(websocket)
    
    async def broadcast(self, message: dict, exclude=None):
        """Отправить сообщение всем клиентам в комнате"""
        self.messages.append(message)
        # Ограничиваем историю 1000 сообщений
        if len(self.messages) > 1000:
            self.messages = self.messages[-1000:]
        
        # Отправляем всем подключенным клиентам
        disconnected = set()
        for client in self.clients:
            if client != exclude:
                try:
                    await client.send(json.dumps(message))
                except Exception:
                    disconnected.add(client)
        
        # Удаляем отключенных клиентов
        for client in disconnected:
            self.remove_client(client)


def get_or_create_room(room_id: str) -> ChatRoom:
    """Получить или создать комнату"""
    if room_id not in rooms:
        rooms[room_id] = ChatRoom(room_id)
    return rooms[room_id]


def generate_token() -> str:
    """Генерация токена для пользователя"""
    return str(uuid.uuid4())


async def handle_websocket(websocket, path):
    """Обработчик WebSocket соединений"""
    # Параметры подключения из URL
    query_string = path.split('?')[1] if '?' in path else ''
    params = dict(param.split('=') for param in query_string.split('&') if '=' in param)
    
    # Декодируем URL-кодированные параметры
    room_id_raw = params.get('room', 'general')
    username_raw = params.get('username', f'User_{uuid.uuid4().hex[:6]}')
    
    room_id = unquote(room_id_raw)
    username = unquote(username_raw)
    
    # Генерируем токен
    token = generate_token()
    
    # Получаем или создаем комнату
    room = get_or_create_room(room_id)
    
    # Сохраняем информацию о пользователе
    users[token] = {
        'username': username,
        'room_id': room_id,
        'websocket': websocket
    }
    
    # Добавляем клиента в комнату
    room.add_client(websocket, username)
    
    # Отправляем токен клиенту
    await websocket.send(json.dumps({
        'type': 'auth',
        'token': token,
        'username': username,
        'room': room_id
    }))
    
    # Уведомляем всех о новом пользователе
    await room.broadcast({
        'type': 'system',
        'message': f'{username} присоединился к комнате',
        'timestamp': datetime.now().isoformat()
    }, exclude=websocket)
    
    print(f"[+] {username} подключился к комнате {room_id}")
    
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                await handle_message(websocket, token, data, room)
            except json.JSONDecodeError:
                await websocket.send(json.dumps({
                    'type': 'error',
                    'message': 'Неверный формат JSON'
                }))
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        # Удаляем клиента при отключении
        room.remove_client(websocket)
        if token in users:
            username = users[token]['username']
            del users[token]
            
            # Уведомляем всех об отключении
            await room.broadcast({
                'type': 'system',
                'message': f'{username} покинул комнату',
                'timestamp': datetime.now().isoformat()
            })
            
            print(f"[-] {username} отключился от комнаты {room_id}")


async def handle_message(websocket, token: str, data: dict, room: ChatRoom):
    """Обработка сообщений от клиента"""
    if token not in users:
        await websocket.send(json.dumps({
            'type': 'error',
            'message': 'Не авторизован'
        }))
        return
    
    user = users[token]
    username = user['username']
    
    msg_type = data.get('type', 'message')
    
    if msg_type == 'message':
        # Обычное сообщение в чат
        content = data.get('content', '')
        if not content.strip():
            return
        
        message = {
            'type': 'message',
            'username': username,
            'content': content,
            'timestamp': datetime.now().isoformat()
        }
        
        # Отправляем всем в комнате
        await room.broadcast(message)
        print(f"[{room.room_id}] {username}: {content}")
    
    elif msg_type == 'ping':
        # Проверка соединения
        await websocket.send(json.dumps({'type': 'pong'}))


class HTTPRequestHandler(BaseHTTPRequestHandler):
    """HTTP обработчик"""
    
    def do_GET(self):
        """Обработка GET запросов"""
        if self.path == '/' or self.path == '/info':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {
                'status': 'running',
                'rooms': list(rooms.keys()),
                'total_users': len(users),
                'endpoints': {
                    'websocket': 'ws://localhost:8765?room=<room_id>&username=<username>',
                    'info': '/info',
                    'rooms': '/rooms'
                }
            }
            self.wfile.write(json.dumps(response, indent=2).encode())
        
        elif self.path == '/rooms':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            rooms_info = {}
            for room_id, room in rooms.items():
                rooms_info[room_id] = {
                    'clients': len(room.clients),
                    'messages': len(room.messages)
                }
            self.wfile.write(json.dumps(rooms_info, indent=2).encode())
        
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        """Отключаем логирование HTTP запросов"""
        pass


def run_http_server():
    """Запуск HTTP сервера в отдельном потоке"""
    server = HTTPServer(('localhost', 8080), HTTPRequestHandler)
    print("HTTP сервер запущен на http://localhost:8080")
    server.serve_forever()


async def main():
    """Главная функция"""
    print("=" * 50)
    print("Chat Server - Лабораторная работа 6")
    print("=" * 50)
    
    # Запускаем HTTP сервер в отдельном потоке
    http_thread = threading.Thread(target=run_http_server, daemon=True)
    http_thread.start()
    
    # Запускаем WebSocket сервер
    print("WebSocket сервер запущен на ws://localhost:8765")
    print("=" * 50)
    
    try:
        async with websockets.serve(handle_websocket, "localhost", 8765):
            await asyncio.Future()  # Работаем бесконечно
    except OSError as e:
        if "10048" in str(e) or "Address already in use" in str(e):
            print("\n[!] Порт 8765 уже используется.")
            print("[!] Возможно, сервер уже запущен в другом терминале.")
            print("[!] Закройте другие экземпляры сервера или подождите несколько секунд.")
        else:
            print(f"\n[!] Ошибка: {e}")


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nСервер остановлен")
    except Exception as e:
        print(f"\nОшибка: {e}")
