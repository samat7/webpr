#!/usr/bin/env python3
"""
Chat Client - Лабораторная работа 6
Простой клиент для подключения к чат-серверу
"""

import asyncio
import json
import sys
import websockets


class ChatClient:
    """Простой клиент для чата"""
    
    def __init__(self, server_url: str, room: str, username: str):
        self.server_url = server_url
        self.room = room
        self.username = username
        self.token = None
        self.websocket = None
        self.running = False
    
    async def connect(self):
        """Подключение к серверу"""
        uri = f"{self.server_url}/ws?room={self.room}&username={self.username}"
        
        try:
            self.websocket = await websockets.connect(uri)
            self.running = True
            print(f"Подключено к комнате '{self.room}' как '{self.username}'")
            print("=" * 50)
            
            # Запускаем задачи на чтение и отправку сообщений
            await asyncio.gather(
                self.receive_messages(),
                self.send_messages()
            )
        except Exception as e:
            print(f"Ошибка подключения: {e}")
    
    async def receive_messages(self):
        """Получение сообщений от сервера"""
        try:
            async for message in self.websocket:
                data = json.loads(message)
                await self.handle_message(data)
        except websockets.exceptions.ConnectionClosed:
            print("\nСоединение закрыто")
            self.running = False
        except Exception as e:
            print(f"\nОшибка получения сообщения: {e}")
            self.running = False
    
    async def handle_message(self, data: dict):
        """Обработка сообщения от сервера"""
        msg_type = data.get('type')
        
        if msg_type == 'auth':
            # Получили токен авторизации
            self.token = data.get('token')
            print(f"Авторизован. Токен: {self.token[:8]}...")
        
        elif msg_type == 'message':
            # Обычное сообщение от пользователя
            username = data.get('username', 'Unknown')
            content = data.get('content', '')
            timestamp = data.get('timestamp', '')
            
            # Форматируем время
            if timestamp:
                time_str = timestamp.split('T')[1][:8]
            else:
                time_str = ''
            
            print(f"[{time_str}] {username}: {content}")
        
        elif msg_type == 'system':
            # Системное сообщение
            message = data.get('message', '')
            print(f"[СИСТЕМА] {message}")
        
        elif msg_type == 'error':
            # Ошибка
            message = data.get('message', '')
            print(f"[ОШИБКА] {message}")
        
        elif msg_type == 'pong':
            # Ответ на ping
            pass
    
    async def send_messages(self):
        """Отправка сообщений на сервер"""
        loop = asyncio.get_event_loop()
        
        while self.running:
            try:
                # Читаем ввод пользователя в отдельном потоке
                message = await loop.run_in_executor(None, sys.stdin.readline)
                message = message.strip()
                
                if not message:
                    continue
                
                if message.lower() == '/quit':
                    print("Выход из чата...")
                    self.running = False
                    break
                
                if message.lower() == '/ping':
                    # Проверка соединения
                    await self.websocket.send(json.dumps({'type': 'ping'}))
                    continue
                
                # Отправляем сообщение
                await self.websocket.send(json.dumps({
                    'type': 'message',
                    'content': message
                }))
            
            except Exception as e:
                print(f"Ошибка отправки: {e}")
                self.running = False
                break
    
    async def disconnect(self):
        """Отключение от сервера"""
        if self.websocket:
            await self.websocket.close()
        print("Отключено от сервера")


async def main():
    """Главная функция"""
    print("=" * 50)
    print("Chat Client - Лабораторная работа 6")
    print("=" * 50)
    
    # Параметры подключения
    server = "ws://localhost:8765"
    room = "general"
    username = "User"
    
    # Парсим аргументы командной строки
    if len(sys.argv) > 1:
        username = sys.argv[1]
    if len(sys.argv) > 2:
        room = sys.argv[2]
    if len(sys.argv) > 3:
        server = sys.argv[3]
    
    print(f"Сервер: {server}")
    print(f"Комната: {room}")
    print(f"Имя пользователя: {username}")
    print("=" * 50)
    print("Команды:")
    print("  /quit - выход")
    print("  /ping - проверка соединения")
    print("=" * 50)
    
    # Создаем и подключаем клиента
    client = ChatClient(server, room, username)
    
    try:
        await client.connect()
    except KeyboardInterrupt:
        print("\nПрерывание...")
    finally:
        await client.disconnect()


if __name__ == '__main__':
    asyncio.run(main())