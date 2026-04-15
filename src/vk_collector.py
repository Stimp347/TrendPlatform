import vk_api
import pandas as pd
from datetime import datetime
import json
import os
import time

class VKDataCollector:
    def __init__(self, access_token):
        """Инициализация VK API"""
        print("Инициализация VK коллектора...")
        self.vk_session = vk_api.VkApi(token=access_token)
        self.vk = self.vk_session.get_api()
        print("[OK] Успешно подключено к VK API")
    
    def get_posts_from_community(self, owner_id, count=50):
        """Получение постов из конкретного сообщества по ID"""
        try:
            response = self.vk.wall.get(
                owner_id=owner_id,
                count=min(count, 100),
                filter='owner'
            )
            
            posts = []
            for item in response.get('items', []):
                if item.get('text'):
                    posts.append({
                        'id': f"{owner_id}_{item['id']}",
                        'text': item.get('text', '')[:500],
                        'date': datetime.fromtimestamp(item['date']).strftime('%Y-%m-%d %H:%M:%S'),
                        'likes': item.get('likes', {}).get('count', 0),
                        'reposts': item.get('reposts', {}).get('count', 0),
                        'comments': item.get('comments', {}).get('count', 0),
                        'views': item.get('views', {}).get('count', 0),
                        'url': f"https://vk.com/wall{owner_id}_{item['id']}"
                    })
            
            return posts
            
        except Exception as e:
            print(f"    Ошибка получения постов: {e}")
            return []
    
    def collect_posts_by_topic(self, topic, posts_per_topic=50):
        """Сбор постов по теме из популярных сообществ"""
        print(f"\nСбор данных по теме: '{topic.upper()}'")
        print("-" * 50)
        
        # ID популярных сообществ по новым темам
        communities_by_topic = {
            "новости": [
                -15755094,   # РИА Новости
                -179925889,   # Мировые новости
                -149802835,    # Новости России
                -58053864,   # ГОрячие новости
                -40316705,   # Новости RT
            ],
            "животные": [
                -196446229,   # Животные Котики
                -199741490,   # Веселые животные
                -44042424,   # Москва - провавшие животные
                -196446214, # Смешные животные
                -199794190,  # Удивительные животные
            ],
            "игры": [
                -387766,   # Игромания
                -78616012,  # Игры ВК
                -79637473,    # Новости Кс
                -67281773,   # Dota 2
                -148506755,   # Хатаб
            ],
            "творчество": [
                -95898540,  # Творчество с детьми
                -220736078,  # Полка чудес
                -102945113,  # Детское творчество
                -220751482,  # Самоделкин
                -211522250,  # Дом твор Передел
            ]
        }
        
        community_ids = communities_by_topic.get(topic, [])
        
        if not community_ids:
            print(f"  Нет сообществ для темы '{topic}'")
            return pd.DataFrame()
        
        all_posts = []
        posts_per_community = max(10, posts_per_topic // len(community_ids))
        
        for community_id in community_ids:
            if len(all_posts) >= posts_per_topic:
                break
                
            print(f"  Парсинг сообщества ID: {community_id}")
            posts = self.get_posts_from_community(community_id, posts_per_community)
            
            for post in posts:
                post['topic'] = topic
                all_posts.append(post)
            
            print(f"    Получено постов: {len(posts)}")
            time.sleep(0.34)
        
        if all_posts:
            print(f"\n  Итого по теме '{topic}': {len(all_posts)} постов")
            avg_likes = sum(p['likes'] for p in all_posts) / len(all_posts) if all_posts else 0
            print(f"  Средний лайк: {avg_likes:.1f}")
            print(f"  Максимум лайков: {max(p['likes'] for p in all_posts)}")
        
        return pd.DataFrame(all_posts)
    
    def save_to_csv(self, df, topic, data_dir='data'):
        """Сохранение данных в CSV"""
        os.makedirs(data_dir, exist_ok=True)
        filename = os.path.join(data_dir, f"vk_{topic}.csv")
        df.to_csv(filename, index=False, encoding='utf-8-sig', sep=';')
        print(f"  Данные сохранены в {filename}")
        return filename

def collect_all_topics():
    """Сбор данных по всем темам"""
    print("=" * 60)
    print("СБОР ДАННЫХ ИЗ ПОПУЛЯРНЫХ СООБЩЕСТВ VK")
    print("=" * 60)
    
    # ВАШ СЕРВИСНЫЙ ТОКЕН
    ACCESS_TOKEN = "daf3d228daf3d228daf3d228b5d9cccd14ddaf3daf3d228b32fd1efd2e79cf2c93639a0"
    
    if len(ACCESS_TOKEN) < 50:
        print("\n[WARNING] Некорректный токен!")
        print("Вставьте ваш сервисный токен из настроек VK приложения")
        return
    
    collector = VKDataCollector(ACCESS_TOKEN)
    
    topics = ["животные", "игры", "новости", "творчество"]
    
    for topic in topics:
        print(f"\n{'='*50}")
        df = collector.collect_posts_by_topic(topic, posts_per_topic=50)
        
        if not df.empty:
            collector.save_to_csv(df, topic)
        else:
            print(f"  Не удалось собрать данные по теме '{topic}'")
        
        time.sleep(1)
    
    print("\n" + "=" * 60)
    print("СБОР ДАННЫХ ЗАВЕРШЕН")
    print("=" * 60)
    print("\nФайлы сохранены в папке 'data':")
    for topic in topics:
        print(f"   - vk_{topic}.csv")

if __name__ == "__main__":
    collect_all_topics()