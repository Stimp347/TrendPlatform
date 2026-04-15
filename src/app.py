from flask import Flask, render_template, jsonify, request
from forecast_ml import MLForecast
import pandas as pd
import plotly
import plotly.express as px
import json
import os
import glob

app = Flask(__name__)

@app.route('/')
def index():
    """Главная страница"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Анализ трендов</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body { padding: 20px; background: #f5f5f5; }
            .header { 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                color: white; 
                padding: 2rem; 
                border-radius: 10px; 
                margin-bottom: 2rem; 
            }
            .card { 
                margin: 10px; 
                box-shadow: 0 4px 6px rgba(0,0,0,0.1); 
                transition: transform 0.3s; 
            }
            .card:hover { transform: translateY(-5px); }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📊 Платформа анализа трендов</h1>
                <p class="lead">Анализ социальных медиа на Python + Flask</p>
            </div>
            
            <div class="row">
                <div class="col-md-3">
                    <div class="card">
                        <div class="card-body text-center">
                            <h5 class="card-title">📈 Дашборд</h5>
                            <p>Интерактивная визуализация</p>
                            <a href="/dashboard" class="btn btn-primary">Открыть</a>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-3">
                    <div class="card">
                        <div class="card-body text-center">
                            <h5 class="card-title">📁 Проверка данных</h5>
                            <p>Посмотреть собранные файлы</p>
                            <a href="/check" class="btn btn-success">Проверить</a>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-3">
                    <div class="card">
                        <div class="card-body text-center">
                            <h5 class="card-title">🔄 Сбор данных</h5>
                            <p>Запустить сборщик VK</p>
                            <a href="/collect" class="btn btn-warning">Собрать</a>
                        </div>
                    </div>
                </div>
                
                <!-- НОВАЯ КАРТОЧКА ДЛЯ ПРОГНОЗОВ -->
                <div class="col-md-3">
                    <div class="card">
                        <div class="card-body text-center">
                            <h5 class="card-title">🔮 ML Прогнозы</h5>
                            <p>Предсказание популярности</p>
                            <a href="/forecast" class="btn btn-info">Открыть</a>
                        </div>
                    </div>
                </div>
                <!-- КОНЕЦ НОВОЙ КАРТОЧКИ -->
            </div>
        </div>
    </body>
    </html>
    """

@app.route('/check')
def check_data():
    """Проверка наличия данных (человеко-читаемая)"""
    import glob
    import os
    import pandas as pd
    
    # Находим все CSV файлы
    csv_files = glob.glob("data/*.csv")
    
    # Словарь для красивых названий
    topic_names = {
        'новости': '📰 Новости (ВК)',
        'животные': '🐾 Животные (ВК)',
        'игры': '🎮 Игры (ВК)',
        'творчество': '🤖 Творчество (ВК)'

    }
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Проверка данных</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body { background: #f5f5f5; padding: 20px; }
            .file-card { 
                background: white; 
                border-radius: 10px; 
                padding: 20px; 
                margin: 15px 0;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                transition: transform 0.3s;
            }
            .file-card:hover {
                transform: translateY(-5px);
            }
            .error-card {
                background: #fff3cd;
                border-left: 4px solid #ffc107;
            }
            .stats-badge {
                background: #667eea;
                color: white;
                padding: 5px 10px;
                border-radius: 20px;
                font-size: 12px;
                display: inline-block;
                margin: 2px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h1>📁 Проверка собранных данных</h1>
                <a href="/" class="btn btn-primary">← На главную</a>
            </div>
    """
    
    if not csv_files:
        html += """
        <div class="alert alert-danger">
            <h4>❌ Данные не найдены!</h4>
            <p>Запустите сбор данных:</p>
            <pre>python src/vk_collector.py</pre>
        </div>
        """
    else:
        # Группируем файлы по темам
        files_by_topic = {}
        for file in csv_files:
            filename = os.path.basename(file)
            # Извлекаем тему из имени файла (убираем vk_ и .csv)
            if filename.startswith('vk_'):
                topic = filename.replace('vk_', '').replace('.csv', '')
            else:
                topic = filename.replace('.csv', '')
            
            if topic not in files_by_topic:
                files_by_topic[topic] = []
            files_by_topic[topic].append(file)
        
        html += f'<p class="text-muted mb-4">📊 Найдено тем: {len(files_by_topic)}</p>'
        
        # Отображаем каждую тему
        for topic, files in files_by_topic.items():
            # Красивое название темы
            display_name = topic_names.get(topic, f'📌 {topic.capitalize()} (ВК)')
            
            html += f"""
            <div class="file-card">
                <h3>{display_name}</h3>
                <hr>
            """
            
            for file in files:
                try:
                    df = pd.read_csv(file, encoding='utf-8-sig', sep=';')
                    filename = os.path.basename(file)
                    
                    # Статистика по теме
                    total_posts = len(df)
                    avg_likes = df['likes'].mean() if 'likes' in df.columns else 0
                    max_likes = df['likes'].max() if 'likes' in df.columns else 0
                    total_views = df['views'].sum() if 'views' in df.columns else 0
                    
                    # Безопасное получение текста
                    text_preview = ""
                    if 'text' in df.columns and len(df) > 0:
                        first_text = df['text'].iloc[0]
                        if pd.notna(first_text) and str(first_text).strip():
                            text_preview = str(first_text)[:200]
                        else:
                            text_preview = "(Пост без текста)"
                    else:
                        text_preview = "(Нет текста в данных)"
                    
                    html += f"""
                    <div class="row">
                        <div class="col-md-12">
                            <div class="mb-3">
                                <span class="stats-badge">📝 Постов: {total_posts}</span>
                                <span class="stats-badge">❤️ Средний лайк: {avg_likes:.1f}</span>
                                <span class="stats-badge">⭐ Макс. лайк: {max_likes}</span>
                                <span class="stats-badge">👁️ Всего просмотров: {total_views:,}</span>
                            </div>
                            <p><strong>📄 Пример поста:</strong></p>
                            <div class="alert alert-secondary">
                                <small>{text_preview}...</small>
                            </div>
                            <small class="text-muted">📁 Файл: {filename}</small>
                        </div>
                    </div>
                    """
                except Exception as e:
                    html += f"""
                    <div class="alert alert-warning">
                        <strong>⚠️ Ошибка чтения файла:</strong> {str(e)}
                    </div>
                    """
            
            html += "</div>"
    
    html += """
        </div>
    </body>
    </html>
    """
    return html

@app.route('/forecast')
def forecast_page():
    """Страница с ML прогнозами"""
    forecast = MLForecast()
    predictions = forecast.forecast_all_topics()
    
    return render_template('forecast.html', predictions=predictions)

@app.route('/dashboard')
def dashboard():
    """Дашборд с визуализацией"""
    
    import os
    import glob
    import pandas as pd
    
    # Загружаем все CSV файлы
    csv_files = glob.glob("data/vk_*.csv")
    
    if not csv_files:
        return render_template('dashboard.html', graphs={}, data=[])
    
    # Собираем статистику
    data = []
    for file in csv_files:
        try:
            df = pd.read_csv(file, encoding='utf-8-sig', sep=';')
            filename = os.path.basename(file)
            topic = filename.replace('vk_', '').replace('.csv', '')
            
            topic_names = {
                'животные': 'Животные',
                'игры': 'Игры',
                'новости': 'Новости',
                'творчество': 'Творчество'
            }
            display_name = topic_names.get(topic, topic)
            
            stats = {
                'Тема': display_name,
                'Посты': len(df),
                'Лайки': float(df['likes'].mean()) if 'likes' in df.columns else 0,
                'Репосты': float(df['reposts'].mean()) if 'reposts' in df.columns else 0,
                'Комментарии': float(df['comments'].mean()) if 'comments' in df.columns else 0,
                'Всего_лайков': int(df['likes'].sum()) if 'likes' in df.columns else 0
            }
            data.append(stats)
        except Exception as e:
            print(f"Ошибка: {e}")
    
    return render_template('dashboard.html', data=data)

@app.route('/collect', methods=['GET', 'POST'])
def collect_data():
    """Страница сбора данных с формой"""
    
    if request.method == 'POST':
        import subprocess
        import sys
        import os
        
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            collector_path = os.path.join(base_dir, 'src', 'vk_collector.py')
            
            result = subprocess.run(
                [sys.executable, collector_path],
                capture_output=True,
                text=True,
                timeout=180
            )
            
            if result.returncode == 0:
                # Успех - не показываем лог, просто красивую страницу
                return render_template('collect_result.html', success=True)
            else:
                return render_template('collect_result.html',
                                     success=False,
                                     error=result.stderr if result.stderr else "Неизвестная ошибка")
        except subprocess.TimeoutExpired:
            return render_template('collect_result.html',
                                 success=False,
                                 error="Превышено время ожидания (3 минуты)")
        except Exception as e:
            return render_template('collect_result.html',
                                 success=False,
                                 error=str(e))
    
    return render_template('collect_form.html')


if __name__ == '__main__':
    
    print("=" * 50)
    print("🚀 ПЛАТФОРМА АНАЛИЗА ТРЕНДОВ ЗАПУЩЕНА")
    print("=" * 50)
    print("📍 Главная страница: http://localhost:5000")
    print("📍 Проверка данных: http://localhost:5000/check")
    print("📍 Дашборд: http://localhost:5000/dashboard")
    print("📍 Сбор данных: http://localhost:5000/collect")
    print("=" * 50)
    print("Нажмите Ctrl+C для остановки")
    
    app.run(debug=True, port=5000)