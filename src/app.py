from flask import Flask, render_template, jsonify
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
                <div class="col-md-4">
                    <div class="card">
                        <div class="card-body text-center">
                            <h5 class="card-title">📈 Дашборд</h5>
                            <p>Интерактивная визуализация данных</p>
                            <a href="/dashboard" class="btn btn-primary">Открыть</a>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-4">
                    <div class="card">
                        <div class="card-body text-center">
                            <h5 class="card-title">📁 Проверка данных</h5>
                            <p>Посмотреть собранные файлы</p>
                            <a href="/check" class="btn btn-success">Проверить</a>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-4">
                    <div class="card">
                        <div class="card-body text-center">
                            <h5 class="card-title">🔄 Сбор данных</h5>
                            <p>Запустить сборщик VK</p>
                            <a href="/collect" class="btn btn-warning">Собрать</a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

@app.route('/check')
def check_data():
    """Проверка наличия данных (ЧЕЛОВЕКО-ЧИТАЕМАЯ)"""
    import glob
    import os
    import pandas as pd
    
    # Находим все CSV файлы
    csv_files = glob.glob("data/*.csv")
    
    # Формируем HTML
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
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📁 Проверка данных</h1>
            <a href="/" class="btn btn-primary mb-3">← На главную</a>
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
        html += f"<p>Найдено файлов: {len(csv_files)}</p>"
        
        for file in csv_files:
            filename = os.path.basename(file)
            df = pd.read_csv(file, encoding='utf-8-sig')
            
            html += f"""
            <div class="file-card">
                <h3>📄 {filename}</h3>
                <p><strong>Записей:</strong> {len(df)}</p>
                <p><strong>Колонки:</strong> {', '.join(df.columns)}</p>
                <p><strong>Пример текста:</strong><br>{df['text'].iloc[0][:200]}...</p>
            </div>
            """
    
    html += "</div></body></html>"
    return html

@app.route('/dashboard')
def dashboard():
    """Дашборд с визуализацией"""
    
    # Загружаем все CSV файлы
    csv_files = glob.glob("data/*.csv")
    
    # ЕСЛИ НЕТ ФАЙЛОВ - ПОКАЗЫВАЕМ СООБЩЕНИЕ
    if not csv_files:
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Дашборд</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        </head>
        <body>
            <div class="container mt-4">
                <div class="alert alert-warning">
                    <h2>⚠️ Нет данных для отображения</h2>
                    <p>Сначала соберите данные:</p>
                    <pre>python src/vk_collector.py</pre>
                    <a href="/check" class="btn btn-primary">Проверить данные</a>
                    <a href="/" class="btn btn-secondary">На главную</a>
                </div>
            </div>
        </body>
        </html>
        """
    
    # Собираем статистику по всем темам
    data = []
    for file in csv_files:
        try:
            df = pd.read_csv(file, encoding='utf-8-sig')
            topic = os.path.basename(file).replace('vk_', '').replace('.csv', '')
            
            # Основная статистика
            stats = {
                'Тема': topic,
                'Посты': len(df),
                'Лайки': float(df['likes'].mean()) if 'likes' in df.columns and len(df) > 0 else 0,
                'Репосты': float(df['reposts'].mean()) if 'reposts' in df.columns and len(df) > 0 else 0,
                'Комментарии': float(df['comments'].mean()) if 'comments' in df.columns and len(df) > 0 else 0,
                'Всего_лайков': int(df['likes'].sum()) if 'likes' in df.columns and len(df) > 0 else 0
            }
            data.append(stats)
        except Exception as e:
            print(f"Ошибка чтения файла {file}: {e}")
    
    # СОЗДАЕМ DataFrame (даже если данные пустые)
    if data:
        df_stats = pd.DataFrame(data)
    else:
        # Создаем пустой DataFrame с правильными колонками
        df_stats = pd.DataFrame(columns=['Тема', 'Посты', 'Лайки', 'Репосты', 'Комментарии', 'Всего_лайков'])
    
    # Генерируем графики
    graphs = {}
    
    # 1. График количества постов (только если есть данные)
    if not df_stats.empty and 'Посты' in df_stats.columns:
        fig1 = px.bar(df_stats, 
                     x='Тема', 
                     y='Посты',
                     title='Количество постов по темам',
                     color='Тема')
        graphs['posts'] = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)
        
        # 2. График средних лайков
        fig2 = px.bar(df_stats,
                     x='Тема',
                     y='Лайки',
                     title='Среднее количество лайков',
                     color='Тема')
        graphs['likes'] = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)
        
        # 3. Круговая диаграмма
        fig3 = px.pie(df_stats,
                     values='Посты',
                     names='Тема',
                     title='Распределение постов по темам')
        graphs['pie'] = json.dumps(fig3, cls=plotly.utils.PlotlyJSONEncoder)
    
    # Возвращаем шаблон
    return render_template('dashboard.html', 
                         graphs=graphs, 
                         data=df_stats.to_dict('records') if not df_stats.empty else [])

@app.route('/collect')
def collect_data():
    """Запуск сбора данных (упрощенная версия)"""
    import subprocess
    import sys
    
    try:
        # Запускаем сборщик данных
        result = subprocess.run([sys.executable, 'src/vk_collector.py'], 
                               capture_output=True, text=True)
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Сбор данных</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        </head>
        <body>
            <div class="container mt-4">
                <h1>Результат сбора данных</h1>
                <pre>{result.stdout}</pre>
                <a href="/check" class="btn btn-primary">Проверить данные</a>
                <a href="/" class="btn btn-secondary">На главную</a>
            </div>
        </body>
        </html>
        """
    except Exception as e:
        return f"Ошибка: {e}"

# Создаем шаблон dashboard.html если его нет
def create_template():
    """Создает шаблон dashboard.html если он отсутствует"""
    template_dir = 'templates'
    template_file = os.path.join(template_dir, 'dashboard.html')
    
    if not os.path.exists(template_dir):
        os.makedirs(template_dir)
    
    if not os.path.exists(template_file):
        with open(template_file, 'w', encoding='utf-8') as f:
            f.write('''
<!DOCTYPE html>
<html>
<head>
    <title>Дашборд</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background: #f8f9fa; padding: 20px; }
        .chart-container {
            background: white;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .stats-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="stats-card">
            <h1>📊 Дашборд анализа трендов</h1>
            <p>Данные из VK по различным темам</p>
            <a href="/" class="btn btn-light btn-sm">На главную</a>
            <a href="/check" class="btn btn-light btn-sm">Проверить данные</a>
        </div>
        
        {% if data %}
        <div class="row mb-4">
            <div class="col-md-3">
                <div class="chart-container">
                    <h5>Всего тем</h5>
                    <h2>{{ data|length }}</h2>
                </div>
            </div>
            <div class="col-md-3">
                <div class="chart-container">
                    <h5>Всего постов</h5>
                    <h2>{{ data|sum(attribute='Посты') }}</h2>
                </div>
            </div>
            <div class="col-md-3">
                <div class="chart-container">
                    <h5>Всего лайков</h5>
                    <h2>{{ data|sum(attribute='Всего_лайков') }}</h2>
                </div>
            </div>
            <div class="col-md-3">
                <div class="chart-container">
                    <h5>Средний лайков</h5>
                    <h2>{% if data|sum(attribute='Посты') > 0 %}
                        {{ (data|sum(attribute='Всего_лайков') / data|sum(attribute='Посты'))|round(1) }}
                    {% else %}0{% endif %}</h2>
                </div>
            </div>
        </div>
        
        <div class="row">
            <div class="col-md-6">
                <div class="chart-container">
                    <div id="chart-posts"></div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="chart-container">
                    <div id="chart-likes"></div>
                </div>
            </div>
        </div>
        
        <div class="row">
            <div class="col-md-6">
                <div class="chart-container">
                    <div id="chart-pie"></div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="chart-container">
                    <h5>Детальная статистика</h5>
                    <table class="table table-striped">
                        <thead>
                            <tr>
                                <th>Тема</th>
                                <th>Посты</th>
                                <th>Лайки (сред.)</th>
                                <th>Репосты (сред.)</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for row in data %}
                            <tr>
                                <td><b>{{ row.Тема }}</b></td>
                                <td>{{ row.Посты }}</td>
                                <td>{{ "%.1f"|format(row.Лайки) }}</td>
                                <td>{{ "%.1f"|format(row.Репосты) }}</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        
        <script>
            {% if graphs.posts %}
            var postsGraph = {{ graphs.posts | safe }};
            Plotly.newPlot('chart-posts', postsGraph.data, postsGraph.layout);
            {% endif %}
            
            {% if graphs.likes %}
            var likesGraph = {{ graphs.likes | safe }};
            Plotly.newPlot('chart-likes', likesGraph.data, likesGraph.layout);
            {% endif %}
            
            {% if graphs.pie %}
            var pieGraph = {{ graphs.pie | safe }};
            Plotly.newPlot('chart-pie', pieGraph.data, pieGraph.layout);
            {% endif %}
        </script>
        {% else %}
        <div class="alert alert-info">
            <h4>ℹ️ Нет данных для отображения</h4>
            <p>Соберите данные через <a href="/collect">сборщик</a> или проверьте <a href="/check">наличие файлов</a>.</p>
        </div>
        {% endif %}
    </div>
</body>
</html>
            ''')
    return template_file

if __name__ == '__main__':
    # Создаем шаблон при запуске
    create_template()
    
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