import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from datetime import datetime, timedelta
import glob
import os

class MLForecast:
    """Прогнозирование частоты упоминаний на 7 дней вперед"""
    
    def __init__(self, data_dir='data'):
        self.data_dir = data_dir
        self.model = RandomForestRegressor(n_estimators=50, random_state=42)
        self.is_fitted = False
    
    def prepare_time_series(self, df):
        """Подготовка временного ряда по дням"""
        df['date_obj'] = pd.to_datetime(df['date'])
        daily_mentions = df.groupby(df['date_obj'].dt.date).size().reset_index(name='mentions')
        daily_mentions.columns = ['date', 'mentions']
        daily_mentions['date'] = pd.to_datetime(daily_mentions['date'])
        daily_mentions = daily_mentions.sort_values('date')
        return daily_mentions
    
    def create_features(self, daily_mentions):
        """Создание признаков для прогноза"""
        if len(daily_mentions) < 6:
            return None, None
        
        features = []
        targets = []
        
        for i in range(5, len(daily_mentions)):
            last_5 = daily_mentions['mentions'].iloc[i-5:i].values
            features.append([
                last_5[0], last_5[1], last_5[2], last_5[3], last_5[4],
                np.mean(last_5), np.std(last_5), last_5[-1] - last_5[0], np.median(last_5)
            ])
            targets.append(daily_mentions['mentions'].iloc[i])
        
        return np.array(features), np.array(targets)
    
    def simple_forecast(self, daily_mentions):
        """Простой прогноз без ML (на случай недостатка данных)"""
        last_5 = daily_mentions['mentions'].tail(5).values
        if len(last_5) < 3:
            last_5 = daily_mentions['mentions'].values
        
        # Используем среднее и тренд
        avg = np.mean(last_5)
        trend = last_5[-1] - last_5[0] if len(last_5) > 1 else 0
        daily_change = trend / len(last_5) if len(last_5) > 0 else 0
        
        predictions = []
        current_avg = avg
        
        for day in range(7):
            pred = max(0, round(current_avg + daily_change * (day + 1)))
            predictions.append(pred)
            current_avg = pred
        
        last_date = daily_mentions['date'].max()
        next_dates = [last_date + timedelta(days=i+1) for i in range(7)]
        
        return {
            'success': True,
            'predictions': predictions,
            'dates': [d.strftime('%d.%m') for d in next_dates],
            'avg_prediction': round(np.mean(predictions), 1),
            'total_prediction': sum(predictions),
            'avg_historical': round(daily_mentions['mentions'].mean(), 1),
            'accuracy': 50,  # Оценка точности для простого прогноза
            'trend': 'Растёт 📈' if predictions[-1] > predictions[0] else 'Падает 📉' if predictions[-1] < predictions[0] else 'Стабилен ➡️',
            'method': 'simple'  # Помечаем, что использован простой метод
        }
    
    def ml_forecast(self, daily_mentions):
        """ML прогноз (если данных достаточно)"""
        X, y = self.create_features(daily_mentions)
        
        if X is None or len(X) < 3:
            return None
        
        # Обучаем модель
        self.model.fit(X, y)
        self.is_fitted = True
        
        # Берем последние 5 дней для прогноза
        last_5 = daily_mentions['mentions'].tail(5).values
        
        predictions = []
        current_window = list(last_5)
        
        for day in range(7):
            features = np.array([[
                current_window[0], current_window[1], current_window[2], current_window[3], current_window[4],
                np.mean(current_window), np.std(current_window), current_window[4] - current_window[0], np.median(current_window)
            ]])
            
            pred = self.model.predict(features)[0]
            predictions.append(max(0, round(pred)))
            current_window.pop(0)
            current_window.append(pred)
        
        # Оценка точности
        y_pred = self.model.predict(X)
        mae = np.mean(np.abs(y_pred - y))
        accuracy = max(0, 100 - (mae / (np.mean(y) + 1) * 100))
        
        last_date = daily_mentions['date'].max()
        next_dates = [last_date + timedelta(days=i+1) for i in range(7)]
        
        return {
            'success': True,
            'predictions': predictions,
            'dates': [d.strftime('%d.%m') for d in next_dates],
            'avg_prediction': round(np.mean(predictions), 1),
            'total_prediction': sum(predictions),
            'avg_historical': round(daily_mentions['mentions'].mean(), 1),
            'accuracy': round(accuracy, 1),
            'trend': 'Растёт 📈' if predictions[-1] > predictions[0] else 'Падает 📉' if predictions[-1] < predictions[0] else 'Стабилен ➡️',
            'method': 'ml'
        }
    
    def predict_7_days(self, daily_mentions):
        """Прогноз на 7 дней вперед (автовыбор метода)"""
        
        if len(daily_mentions) < 5:
            return {
                'error': f'Недостаточно данных (есть {len(daily_mentions)} дней, нужно минимум 5)',
                'need_more': 5 - len(daily_mentions)
            }
        
        # Пробуем ML, если не получается - используем простой метод
        ml_result = self.ml_forecast(daily_mentions)
        
        if ml_result is None:
            print("  → Использую простой метод прогноза (недостаточно данных для ML)")
            return self.simple_forecast(daily_mentions)
        else:
            print("  → Использую ML метод прогноза (Random Forest)")
            return ml_result
    
    def forecast_all_topics(self):
        """Прогноз для всех тем"""
        results = {}
        csv_files = glob.glob(f"{self.data_dir}/vk_*.csv")
        
        topic_names = {
            'животные': '🐾 Животные',
            'игры': '🎮 Игры',
            'новости': '📰 Новости',
            'творчество': '🎨 Творчество'
        }
        
        print("\n" + "=" * 60)
        print("🔮 ЗАПУСК ПРОГНОЗИРОВАНИЯ")
        print("=" * 60)
        
        for file in csv_files:
            filename = os.path.basename(file)
            topic = filename.replace('vk_', '').replace('.csv', '')
            display_name = topic_names.get(topic, topic)
            
            print(f"\n📊 Обработка: {display_name}")
            df = pd.read_csv(file, encoding='utf-8-sig', sep=';')
            daily_mentions = self.prepare_time_series(df)
            
            print(f"   Дней в данных: {len(daily_mentions)}")
            result = self.predict_7_days(daily_mentions)
            results[display_name] = result
            
            if 'success' in result:
                print(f"   ✅ Прогноз: {result['total_prediction']} упоминаний за 7 дней")
                print(f"   📈 Метод: {'ML (Random Forest)' if result.get('method') == 'ml' else 'Простой (среднее + тренд)'}")
            else:
                print(f"   ❌ {result.get('error', 'Ошибка')}")
        
        print("\n" + "=" * 60)
        return results

# Тест
def test_forecast():
    print("=" * 60)
    print("🔮 ПРОГНОЗ УПОМИНАНИЙ НА 7 ДНЕЙ")
    print("=" * 60)
    
    forecast = MLForecast()
    results = forecast.forecast_all_topics()
    
    for topic, result in results.items():
        print(f"\n📊 {topic}")
        if 'success' in result:
            print(f"   📈 Прогноз: {result['predictions']}")
            print(f"   📅 Дни: {result['dates']}")
            print(f"   📊 Всего упоминаний: {result['total_prediction']}")
            print(f"   🎯 Метод: {'ML' if result.get('method') == 'ml' else 'Простой'}")
            print(f"   🔄 Тренд: {result['trend']}")
        else:
            print(f"   ❌ {result['error']}")

if __name__ == "__main__":
    test_forecast()