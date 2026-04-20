import pandas as pd
import numpy as np
import glob
import traceback
import os
from datetime import datetime, timedelta
from collections import Counter
import re
from sklearn.linear_model import LinearRegression
import warnings
warnings.filterwarnings('ignore')

class HabrAnalyzer:
    def __init__(self, data_dir='data'):
        self.data_dir = data_dir
        self.stop_words = {'это', 'все', 'как', 'для', 'на', 'по', 'с', 'и', 'не', 'или', 'если', 
                          'то', 'что', 'который', 'быть', 'весь', 'год', 'новый', 'также', 'ещё',
                          'уже', 'очень', 'можно', 'нужно', 'такой', 'только', 'без', 'до', 'из'}
    
    def load_hubr_data(self, topic):
        """Загружает данные по конкретной теме"""
        filename = os.path.join(self.data_dir, f"habr_{topic}.csv")
        if not os.path.exists(filename):
            print(f"❌ Файл {filename} не найден")
            return None
        df = pd.read_csv(filename, encoding='utf-8-sig', sep=';')
        df['date'] = pd.to_datetime(df['date'])
        return df
    
    # ==================== 1. ЧАСТОТНЫЙ АНАЛИЗ КЛЮЧЕВЫХ СЛОВ ====================
    def analyze_keywords(self, df, top_n=15):
        """Анализ самых популярных ключевых слов в заголовках и текстах"""
        # Объединяем заголовки и тексты
        all_text = ' '.join(df['title'].fillna('') + ' ' + df['text'].fillna(''))
        all_text = all_text.lower()
        
        # Находим все слова
        words = re.findall(r'[а-яёa-z][а-яёa-z-]{2,}', all_text, re.IGNORECASE)
        
        # Технологические ключевые слова для поиска
        tech_keywords = {
            'python': ['python', 'py', 'django', 'flask', 'fastapi'],
            'javascript': ['javascript', 'js', 'react', 'vue', 'angular', 'node', 'nodejs'],
            'java': ['java', 'spring', 'kotlin'],
            'c++': ['c++', 'cpp', 'qt'],
            'c#': ['c#', 'csharp', '.net', 'unity'],
            'go': ['go', 'golang'],
            'rust': ['rust', 'cargo'],
            'php': ['php', 'laravel', 'symfony'],
            'typescript': ['typescript', 'ts'],
            'ai': ['ai', 'ии', 'нейросеть', 'нейронная', 'gpt', 'chatgpt', 'llm', 'машинное обучение'],
            'data_science': ['data science', 'data mining', 'pandas', 'numpy', 'анализ данных'],
            'devops': ['devops', 'docker', 'kubernetes', 'k8s', 'ci/cd', 'gitlab'],
            'mobile': ['ios', 'android', 'flutter', 'swift', 'kotlin', 'react native'],
            'database': ['sql', 'postgresql', 'mysql', 'mongodb', 'redis', 'баз данных'],
            'cloud': ['cloud', 'aws', 'azure', 'gcp', 'облако', 'облачные'],
            'frontend': ['frontend', 'front-end', 'css', 'html', 'webpack', 'vite'],
            'backend': ['backend', 'back-end', 'server', 'сервер'],
            'security': ['security', 'безопасность', 'hack', 'кибербезопасность'],
            'blockchain': ['blockchain', 'крипт', 'bitcoin', 'эфир', 'web3']
        }
        
        # Считаем упоминания технологий
        tech_counts = {}
        for tech, keywords in tech_keywords.items():
            count = 0
            for word in keywords:
                count += all_text.count(word)
            if count > 0:
                tech_counts[tech] = count
        
        # Сортируем по популярности
        sorted_tech = sorted(tech_counts.items(), key=lambda x: x[1], reverse=True)[:top_n]
        
        # Обычные ключевые слова (без технологий)
        word_counts = Counter(words)
        for stop in self.stop_words:
            if stop in word_counts:
                del word_counts[stop]
        common_words = word_counts.most_common(top_n)
        
        return {
            'top_technologies': sorted_tech,
            'top_keywords': common_words,
            'total_words': len(words)
        }
    
    # ==================== 2. ПРОГНОЗ КОЛИЧЕСТВА ПУБЛИКАЦИЙ ====================
    def forecast_publications(self, df, days_ahead=7):
        """Прогнозирование количества публикаций на основе временного ряда"""
        # Группируем по дням
        daily_posts = df.groupby(df['date'].dt.date).size().reset_index(name='count')
        daily_posts.columns = ['date', 'count']
        daily_posts['date'] = pd.to_datetime(daily_posts['date'])
        daily_posts = daily_posts.sort_values('date')
        
        if len(daily_posts) < 7:
            return {'error': 'Недостаточно данных для прогноза (нужно минимум 7 дней)'}
        
        # Создаем признаки для прогноза
        days = (daily_posts['date'] - daily_posts['date'].min()).dt.days.values.reshape(-1, 1)
        counts = daily_posts['count'].values
        
        # Простая линейная регрессия
        model = LinearRegression()
        model.fit(days, counts)
        
        # Прогнозируем на days_ahead дней вперед
        last_day = days[-1][0]
        future_days = np.array(range(last_day + 1, last_day + days_ahead + 1)).reshape(-1, 1)
        predictions = model.predict(future_days)
        predictions = np.maximum(predictions, 0)  # Не может быть отрицательным
        
        # Генерируем даты для прогноза
        last_date = daily_posts['date'].max()
        future_dates = [last_date + timedelta(days=i+1) for i in range(days_ahead)]
        
        # Средняя ошибка модели
        from sklearn.metrics import mean_absolute_error
        y_pred = model.predict(days)
        mae = mean_absolute_error(counts, y_pred)
        accuracy = max(0, 100 - (mae / (np.mean(counts) + 1) * 100))
        
        # Тренд
        trend = 'Растёт 📈' if model.coef_[0] > 0 else 'Падает 📉' if model.coef_[0] < 0 else 'Стабилен ➡️'
        
        return {
            'success': True,
        'predictions': [int(round(p, 0)) for p in predictions],  # int()
        'dates': [d.strftime('%d.%m') for d in future_dates],
        'total_forecast': int(round(sum(predictions), 0)),  # int()
        'avg_daily': float(round(np.mean(predictions), 1)),  # float()
        'trend': trend,
        'trend_coefficient': float(round(model.coef_[0], 2)),  # float()
        'accuracy': float(round(accuracy, 1)),  # float()
        'historical_avg': float(round(np.mean(counts), 1)),  # float()
        'historical_total': int(sum(counts))  # int()
        }
    
    # ==================== 3. АНАЛИЗ АВТОРОВ ====================
    def analyze_authors(self, df, top_n=10):
        """Анализ самых активных авторов"""
        # Подсчет статей по авторам
        author_counts = df['author'].value_counts().head(top_n)
        
        # Дополнительная статистика по топ-авторам
        top_authors = []
        for author in author_counts.index[:top_n]:
            author_df = df[df['author'] == author]
            top_authors.append({
                'name': author,
                'articles': len(author_df),
                'avg_title_length': author_df['title'].str.len().mean(),
                'last_article': author_df['date'].max().strftime('%Y-%m-%d'),
                'main_hub': author_df['hub'].mode().iloc[0] if not author_df['hub'].mode().empty else 'unknown'
            })
        
        # Прогноз активности авторов (кто будет писать в ближайшее время)
        # На основе периодичности публикаций
        author_forecast = []
        for author in author_counts.index[:5]:  # Топ-5 авторов
            author_df = df[df['author'] == author].sort_values('date')
            if len(author_df) >= 3:
                # Средний интервал между публикациями
                date_diffs = author_df['date'].diff().dt.days.dropna()
                avg_interval = date_diffs.mean()
                last_date = author_df['date'].max()
                next_expected = last_date + timedelta(days=avg_interval)
                
                author_forecast.append({
                    'name': author,
                    'avg_interval_days': round(avg_interval, 1),
                    'last_publication': last_date.strftime('%Y-%m-%d'),
                    'next_expected': next_expected.strftime('%Y-%m-%d')
                })
        
        return {
            'top_authors': top_authors,
            'total_authors': df['author'].nunique(),
            'author_forecast': author_forecast,
            'most_prolific': author_counts.index[0] if len(author_counts) > 0 else None
        }
    
    # ==================== 4. ПОЛНЫЙ АНАЛИЗ ====================
    def analyze_all_topics(self):
        """Запускает все три анализа для всех тем"""
        topics = ["программирование", "игры", "it_новости"]
        results = {}
        
        for topic in topics:
            print(f"\n{'='*60}")
            print(f"📊 АНАЛИЗ ТЕМЫ: {topic.upper()}")
            print('='*60)
            
            df = self.load_hubr_data(topic)
            if df is None or df.empty:
                print(f"❌ Нет данных для темы {topic}")
                continue
            
            print(f"📁 Загружено {len(df)} постов")
            
            # 1. Частотный анализ
            print("\n📈 1. ЧАСТОТНЫЙ АНАЛИЗ КЛЮЧЕВЫХ СЛОВ")
            keywords = self.analyze_keywords(df)
            print(f"   Всего слов: {keywords['total_words']}")
            print(f"   Топ-5 технологий:")
            for tech, count in keywords['top_technologies'][:5]:
                print(f"     • {tech}: {count} упоминаний")
            
            # 2. Прогноз публикаций
            print("\n🔮 2. ПРОГНОЗ ПУБЛИКАЦИЙ НА 30 ДНЕЙ")
            forecast = self.forecast_publications(df)
            if 'error' in forecast:
                print(f"   ❌ {forecast['error']}")
            else:
                print(f"   📊 Историческое среднее: {forecast['historical_avg']:.1f} постов/день")
                print(f"   📈 Тренд: {forecast['trend']} (коэф. {forecast['trend_coefficient']})")
                print(f"   🎯 Прогноз на месяц: {forecast['total_forecast']} постов")
                print(f"   ✅ Точность модели: {forecast['accuracy']}%")
            
            # 3. Анализ авторов
            print("\n👤 3. АНАЛИЗ АВТОРОВ")
            authors = self.analyze_authors(df)
            print(f"   Всего авторов: {authors['total_authors']}")
            print(f"   Самый активный: {authors['most_prolific']}")
            print(f"   Топ-3 автора:")
            for author in authors['top_authors'][:3]:
                print(f"     • {author['name']}: {author['articles']} статей (в основном хаб: {author['main_hub']})")
            
            results[topic] = {
            'keywords': {
                'top_technologies': [[str(tech), int(count)] for tech, count in keywords['top_technologies']],  # преобразуем
                'top_keywords': [[str(word), int(cnt)] for word, cnt in keywords['top_keywords']],
                'total_words': int(keywords['total_words'])
            },
            'forecast': forecast,
            'authors': {
                'top_authors': [
                    {
                        'name': str(author['name']),
                        'articles': int(author['articles']),
                        'avg_title_length': float(author['avg_title_length']),
                        'last_article': str(author['last_article']),
                        'main_hub': str(author['main_hub'])
                    } for author in authors['top_authors']
                ],
                'total_authors': int(authors['total_authors']),
                'most_prolific': str(authors['most_prolific']) if authors['most_prolific'] else None,
                'author_forecast': [
                    {
                        'name': str(af['name']),
                        'avg_interval_days': float(af['avg_interval_days']),
                        'last_publication': str(af['last_publication']),
                        'next_expected': str(af['next_expected'])
                    } for af in authors['author_forecast']
                ]
            },
            'total_posts': int(len(df))
        }
        
        return results

def print_full_report():
    """Выводит полный отчёт по анализу Habr"""
    analyzer = HabrAnalyzer()
    results = analyzer.analyze_all_topics()
    
    print("\n" + "="*60)
    print("📋 ИТОГОВЫЙ ОТЧЁТ ПО АНАЛИЗУ HABR")
    print("="*60)
    
    for topic, data in results.items():
        print(f"\n🔥 {topic.upper()}: {data['total_posts']} постов")
        
        # Технологии в топе
        techs = data['keywords']['top_technologies'][:3]
        if techs:
            print(f"   🏆 Популярные технологии: {', '.join([t[0] for t in techs])}")
        
        # Прогноз
        forecast = data['forecast']
        if 'success' in forecast:
            print(f"   📊 Прогноз на месяц: {forecast['total_forecast']} постов ({forecast['trend']})")
        
        # Топ-автор
        top_author = data['authors']['top_authors'][0] if data['authors']['top_authors'] else None
        if top_author:
            print(f"   ✍️ Лидер мнений: {top_author['name']} ({top_author['articles']} статей)")

if __name__ == "__main__":
    print_full_report()
    input("\n\nНажмите Enter для выхода...")