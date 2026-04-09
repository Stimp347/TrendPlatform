import vk_api
import pandas as pd
from datetime import datetime
import json

class VKDataCollector:
    def __init__(self, access_token):
        """Инициализация VK API"""
        print("Инициализация VK коллектора...")
        self.vk_session = vk_api.VkApi(token=access_token)
        self.vk = self.vk_session.get_api()
        print("✓ Успешно подключено к VK API")
    
    def collect_posts(self, query, count=100):
        """Сбор постов по запросу"""
        print(f"Сбор данных по запросу: '{query}'")
        
        try:
            response = self.vk.newsfeed.search(
                q=query,
                count=min(count, 200),
                extended=1,
                fields='id,first_name,last_name'
            )
            
            posts_data = []
            
            for i, item in enumerate(response.get('items', [])):
                # Прогресс
                if i % 10 == 0:
                    print(f"  Обработано {i+1}/{len(response['items'])} постов")
                
                post_info = {
                    'id': f"{item['owner_id']}_{item['id']}",
                    'text': item.get('text', '')[:500],
                    'date': datetime.fromtimestamp(item['date']).strftime('%Y-%m-%d %H:%M:%S'),
                    'likes': item.get('likes', {}).get('count', 0),
                    'reposts': item.get('reposts', {}).get('count', 0),
                    'comments': item.get('comments', {}).get('count', 0),
                    'views': item.get('views', {}).get('count', 0)
                }
                
                # Ищем автора
                author = "Неизвестно"
                for profile in response.get('profiles', []):
                    if profile['id'] == abs(item['owner_id']):
                        author = f"{profile['first_name']} {profile['last_name']}"
                        break
                
                post_info['author'] = author
                posts_data.append(post_info)
            
            df = pd.DataFrame(posts_data)
            print(f"✓ Собрано {len(df)} постов")
            return df
            
        except Exception as e:
            print(f"✗ Ошибка: {e}")
            return pd.DataFrame()

# Тестовая функция
def test_collector():
    """Тестирование коллектора"""
    print("=" * 50)
    print("ТЕСТ СБОРЩИКА ДАННЫХ VK")
    print("=" * 50)
    
    # ВАШ ТОКЕН (замените на реальный)
    ACCESS_TOKEN = "dc7d4a92dc7d4a92dc7d4a921ddf4255aeddc7ddc7d4a92b5d8c9e69bf9e9d6dfc1c5a6"
    
    if ACCESS_TOKEN == "ваш_токен_здесь":
        print("\n⚠️  ВНИМАНИЕ: Замените ACCESS_TOKEN на реальный токен VK!")
        print("Как получить токен:")
        print("1. Откройте https://vk.com/dev")
        print("2. Создайте Standalone приложение")
        print("3. Получите токен через OAuth")
        return
    
    collector = VKDataCollector(ACCESS_TOKEN)
    
    # Тестовые запросы
    test_queries = ["кофе", "чай"]
    
    for query in test_queries:
        print(f"\n{'='*30}")
        print(f"Сбор данных: {query}")
        print('='*30)
        
        df = collector.collect_posts(query, count=30)
        
        if not df.empty:
            # Сохраняем в CSV
            filename = f"C:\\Users\\User\\trend_platform\\data\\vk_{query}.csv"
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            print(f"✓ Данные сохранены в {filename}")
            
            # Показываем статистику
            print(f"\nСтатистика по '{query}':")
            print(f"  Всего постов: {len(df)}")
            print(f"  Среднее лайков: {df['likes'].mean():.1f}")
            print(f"  Среднее репостов: {df['reposts'].mean():.1f}")
            print(f"  Самый популярный пост: {df['likes'].max()} лайков")
            
            # Пример поста
            if len(df) > 0:
                print(f"\nПример поста:")
                print(f"  Текст: {df.iloc[0]['text'][:100]}...")
                print(f"  Автор: {df.iloc[0]['author']}")
                print(f"  Дата: {df.iloc[0]['date']}")
        else:
            print(f"✗ Не удалось собрать данные по запросу '{query}'")
    
    print("\n" + "="*50)
    print("ТЕСТ ЗАВЕРШЕН")

if __name__ == "__main__":
    test_collector()