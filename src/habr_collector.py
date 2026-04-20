import feedparser
import pandas as pd
import time
import os
from datetime import datetime

class HabrCollector:
    def __init__(self):
        self.base_url = "https://habr.com/ru/rss/hub/"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    def get_posts_by_hub(self, hub_name, posts_limit=50):
        """Получает посты из конкретного хаба Habr по RSS"""
        rss_url = f"{self.base_url}{hub_name}/"
        print(f"  Загрузка RSS: {rss_url}")

        try:
            feed = feedparser.parse(rss_url)
            posts = []

            for i, entry in enumerate(feed.entries):
                if i >= posts_limit:
                    break

                # Получаем дату
                pub_date = entry.get('published', '')
                try:
                    date_obj = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %Z')
                    formatted_date = date_obj.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    formatted_date = pub_date

                posts.append({
                    'id': entry.get('id', '').split('/')[-2] if '/' in entry.get('id', '') else '',
                    'title': entry.get('title', ''),
                    'text': entry.get('summary', '')[:500],
                    'date': formatted_date,
                    'link': entry.get('link', ''),
                    'author': entry.get('author', ''),
                    'hub': hub_name
                })

            return pd.DataFrame(posts)

        except Exception as e:
            print(f" Ошибка при загрузке хаба {hub_name}: {e}")
            return pd.DataFrame()

    def collect_posts_by_topic(self, topic, hubs_map, posts_per_topic=50):
        """Сбор постов по теме из соответствующих хабов"""
        print(f"\n Сбор данных из Habr по теме: '{topic.upper()}'")
        print("-" * 50)

        hub_list = hubs_map.get(topic, [])
        if not hub_list:
            print(f"  ✗ Нет хабов для темы '{topic}'")
            return pd.DataFrame()

        all_posts = []
        posts_per_hub = max(15, posts_per_topic // len(hub_list))

        for hub_name in hub_list:
            if len(all_posts) >= posts_per_topic:
                break

            print(f"  Парсинг хаба: {hub_name}")
            posts_df = self.get_posts_by_hub(hub_name, posts_per_hub)

            if not posts_df.empty:
                posts_df['topic'] = topic
                all_posts.append(posts_df)
                print(f"    Получено постов: {len(posts_df)}")

            time.sleep(0.5)

        if all_posts:
            result_df = pd.concat(all_posts, ignore_index=True)
            result_df = result_df.drop_duplicates(subset=['id'])
            print(f"\n  Итого по теме '{topic}': {len(result_df)} постов")
            return result_df

        return pd.DataFrame()

    def save_to_csv(self, df, topic, data_dir='data'):
        """Сохраняет DataFrame в CSV файл"""
        os.makedirs(data_dir, exist_ok=True)
        filename = os.path.join(data_dir, f"habr_{topic}.csv")
        df.to_csv(filename, index=False, encoding='utf-8-sig', sep=';')
        print(f" Данные сохранены в {filename}")
        return filename


def collect_all_topics():
    """Сбор данных по IT, играм и IT-новостям из Habr"""
    print("=" * 60)
    print(" СБОР ДАННЫХ ИЗ ХАБРА (HABR)")
    print("=" * 60)
    print(" Темы: ПРОГРАММИРОВАНИЕ, ИГРЫ, IT-НОВОСТИ")
    print("=" * 60)

    # Соответствие тем и хабов на Habr (только IT, игры, IT-новости)
    hubs_by_topic = {
        "программирование": [
            "python",           # Python
            "javascript",       # JavaScript
            "java",            # Java
            "csharp",          # C#
            "cpp",             # C++
            "go",              # Go
            "php",             # PHP
            "kotlin",          # Kotlin
            "swift",           # Swift
            "web",             # Веб-разработка
            "database",        # Базы данных
            "devops",          # DevOps
            "linux"            # Linux
        ],
        "игры": [
            "gamedev",         # Разработка игр
            "game",            # Игры
            "mobile_dev",      # Мобильная разработка (включая игры)
            "cybersport"       # Киберспорт
        ],
        "it_новости": [
            "news",            # Новости
            "technology",      # Технологии
            "startup",         # Стартапы
            "cryptocurrency",  # Криптовалюты
            "ai",              # Искусственный интеллект
            "machine_learning" # Машинное обучение
        ]
    }

    collector = HabrCollector()
    topics = ["программирование", "игры", "it_новости"]

    for topic in topics:
        print(f"\n{'='*50}")
        df = collector.collect_posts_by_topic(topic, hubs_by_topic, posts_per_topic=50)

        if not df.empty:
            collector.save_to_csv(df, topic)
        else:
            print(f"  Не удалось собрать данные по теме '{topic}'")

        time.sleep(1)

    print("\n" + "=" * 60)
    print(" СБОР ДАННЫХ ИЗ ХАБРА ЗАВЕРШЁН")
    print("=" * 60)
    print("\n Созданные файлы:")
    print("   - data/habr_программирование.csv")
    print("   - data/habr_игры.csv")
    print("   - data/habr_it_новости.csv")


if __name__ == "__main__":
    collect_all_topics()