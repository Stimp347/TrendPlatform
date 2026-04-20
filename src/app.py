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
    return render_template('index.html')

@app.route('/check')
def check_data():
    """Проверка наличия данных"""
    import pandas as pd
    import glob
    import os
    
    # VK данные
    vk_files = []
    vk_csv_files = glob.glob("data/vk_*.csv")
    
    topic_names_vk = {
        'животные': '🐾 Животные',
        'игры': '🎮 Игры',
        'новости': '📰 Новости',
        'творчество': '🎨 Творчество'
    }
    
    for file in vk_csv_files:
        try:
            df = pd.read_csv(file, encoding='utf-8-sig', sep=';')
            filename = os.path.basename(file)
            topic = filename.replace('vk_', '').replace('.csv', '')
            display_name = topic_names_vk.get(topic, topic)
            
            text_preview = ""
            if 'text' in df.columns and len(df) > 0:
                first_text = df['text'].iloc[0]
                if pd.notna(first_text) and str(first_text).strip():
                    text_preview = str(first_text)[:200] + "..."
                else:
                    text_preview = "(Пост без текста)"
            else:
                text_preview = "(Нет текста в данных)"
            
            vk_files.append({
                'name': filename,
                'display_name': display_name,
                'preview': text_preview,
                'stats': {
                    'rows': len(df),
                    'avg_likes': round(df['likes'].mean(), 1) if 'likes' in df.columns else None,
                    'max_likes': df['likes'].max() if 'likes' in df.columns else None,
                    'total_views': int(df['views'].sum()) if 'views' in df.columns else None
                }
            })
        except Exception as e:
            print(f"Ошибка VK {file}: {e}")
    
    return render_template('check.html', vk_files=vk_files)


@app.route('/check/vk')
def check_vk():
    """Проверка данных VK"""
    import pandas as pd
    import glob
    import os
    
    csv_files = glob.glob("data/vk_*.csv")
    files = []
    
    topic_names = {
        'животные': '🐾 Животные',
        'игры': '🎮 Игры',
        'новости': '📰 Новости',
        'творчество': '🎨 Творчество'
    }
    
    for file in csv_files:
        try:
            df = pd.read_csv(file, encoding='utf-8-sig', sep=';')
            filename = os.path.basename(file)
            topic = filename.replace('vk_', '').replace('.csv', '')
            display_name = topic_names.get(topic, topic)
            
            text_preview = ""
            if 'text' in df.columns and len(df) > 0:
                first_text = df['text'].iloc[0]
                if pd.notna(first_text) and str(first_text).strip():
                    text_preview = str(first_text)[:200] + "..."
                else:
                    text_preview = "(Пост без текста)"
            else:
                text_preview = "(Нет текста в данных)"
            
            files.append({
                'name': filename,
                'display_name': display_name,
                'preview': text_preview,
                'stats': {
                    'rows': len(df),
                    'avg_likes': round(df['likes'].mean(), 1) if 'likes' in df.columns else None,
                    'max_likes': df['likes'].max() if 'likes' in df.columns else None,
                    'total_views': int(df['views'].sum()) if 'views' in df.columns else None
                }
            })
        except Exception as e:
            print(f"Ошибка {file}: {e}")
    
    return render_template('check_vk.html', files=files)


@app.route('/check/habr')
def check_habr():
    """Проверка данных Habr"""
    import pandas as pd
    import glob
    import os
    
    csv_files = glob.glob("data/habr_*.csv")
    files = []
    
    topic_names = {
        'программирование': '💻 Программирование',
        'игры': '🎮 Игры',
        'it_новости': '📰 IT-новости'
    }
    
    for file in csv_files:
        try:
            df = pd.read_csv(file, encoding='utf-8-sig', sep=';')
            filename = os.path.basename(file)
            topic = filename.replace('habr_', '').replace('.csv', '')
            display_name = topic_names.get(topic, topic)
            
            title_preview = ""
            if 'title' in df.columns and len(df) > 0:
                first_title = df['title'].iloc[0]
                if pd.notna(first_title) and str(first_title).strip():
                    title_preview = str(first_title)[:200] + "..."
                else:
                    title_preview = "(Нет заголовка)"
            else:
                title_preview = "(Нет данных)"
            
            files.append({
                'name': filename,
                'display_name': display_name,
                'preview': title_preview,
                'stats': {
                    'rows': len(df),
                    'total_authors': df['author'].nunique() if 'author' in df.columns else None,
                    'total_hubs': df['hub'].nunique() if 'hub' in df.columns else None
                }
            })
        except Exception as e:
            print(f"Ошибка {file}: {e}")
    
    return render_template('check_habr.html', files=files)

@app.route('/dashboard/vk')
def dashboard_vk():
    """Дашборд для VK данных"""
    import pandas as pd
    import glob
    import os
    
    csv_files = glob.glob("data/vk_*.csv")
    data = []
    
    topic_names = {
        'животные': '🐾 Животные',
        'игры': '🎮 Игры',
        'новости': '📰 Новости',
        'творчество': '🎨 Творчество'
    }
    
    for file in csv_files:
        try:
            df = pd.read_csv(file, encoding='utf-8-sig', sep=';')
            filename = os.path.basename(file)
            topic = filename.replace('vk_', '').replace('.csv', '')
            display_name = topic_names.get(topic, topic)
            
            data.append({
                'Тема': display_name,
                'Посты': len(df),
                'Лайки': float(df['likes'].mean()) if 'likes' in df.columns else 0,
                'Репосты': float(df['reposts'].mean()) if 'reposts' in df.columns else 0,
                'Комментарии': float(df['comments'].mean()) if 'comments' in df.columns else 0,
                'Всего_лайков': int(df['likes'].sum()) if 'likes' in df.columns else 0
            })
        except Exception as e:
            print(f"Ошибка VK {file}: {e}")
    
    return render_template('dashboard_vk.html', data=data, source='VK')


@app.route('/forecast/vk')
def forecast_vk():
    """Страница прогнозов для VK"""
    from forecast_ml import MLForecast
    
    forecast = MLForecast()
    predictions = forecast.forecast_all_topics()
    
    return render_template('forecast_vk.html', predictions=predictions, source='VK')

@app.route('/dashboard/habr')
def dashboard_habr():
    """Дашборд для Habr данных"""
    import pandas as pd
    import glob
    import os
    
    csv_files = glob.glob("data/habr_*.csv")
    data = []
    
    # Соответствие тем красивым названиям
    topic_names = {
        'программирование': '💻 Программирование',
        'игры': '🎮 Игры',
        'it_новости': '📰 IT-новости'
    }
    
    for file in csv_files:
        try:
            df = pd.read_csv(file, encoding='utf-8-sig', sep=';')
            filename = os.path.basename(file)
            topic = filename.replace('habr_', '').replace('.csv', '')
            display_name = topic_names.get(topic, topic)
            
            # Анализируем частоту слов для облака тегов
            all_text = ' '.join(df['title'].fillna('') + ' ' + df['text'].fillna(''))
            
            data.append({
                'Тема': display_name,
                'Посты': len(df),
                'Авторов': df['author'].nunique(),
                'Хабов': df['hub'].nunique(),
                'Средняя_длина_заголовка': round(df['title'].str.len().mean(), 1),
                'Самый_активный_автор': df['author'].mode().iloc[0] if not df['author'].mode().empty else '—',
                'Популярный_хаб': df['hub'].mode().iloc[0] if not df['hub'].mode().empty else '—'
            })
        except Exception as e:
            print(f"Ошибка {file}: {e}")
    
    return render_template('dashboard_habr.html', data=data, source='Habr')

@app.route('/forecast/habr')
def forecast_habr():
    """Страница прогнозов для Habr"""
    from habr_analyzer import HabrAnalyzer
    
    analyzer = HabrAnalyzer()
    results = analyzer.analyze_all_topics()
    
    return render_template('forecast_habr.html', predictions=results, source='Habr')

@app.route('/collect/habr')
def collect_habr():
    """Страница сбора данных из Habr"""
    return render_template('collect_habr.html')
    
@app.route('/run_collect/habr')
def run_collect_habr():
    """Запуск сбора данных из Habr"""
    import subprocess
    import sys
    import os
    
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        collector_path = os.path.join(base_dir, 'src', 'habr_collector.py')
        
        result = subprocess.run(
            [sys.executable, collector_path],
            capture_output=True,
            text=True,
            timeout=180
        )
        
        if result.returncode == 0:
            return render_template('collect_result_habr.html', success=True)
        else:
            return render_template('collect_result_habr.html',
                                 success=False,
                                 error=result.stderr if result.stderr else "Неизвестная ошибка")
    except subprocess.TimeoutExpired:
        return render_template('collect_result_habr.html',
                             success=False,
                             error="Превышено время ожидания (3 минуты)")
    except Exception as e:
        return render_template('collect_result_habr.html',
                             success=False,
                             error=str(e))

@app.route('/forecast')
def forecast_page():
    """Страница прогнозов VK"""
    from forecast_ml import MLForecast
    
    forecast = MLForecast()
    predictions = forecast.forecast_all_topics()
    
    return render_template('forecast.html', predictions=predictions)

# @app.route('/dashboard')
# def dashboard():
#     """Дашборд с визуализацией"""
    
#     import os
#     import glob
#     import pandas as pd
    
#     # Загружаем все CSV файлы
#     csv_files = glob.glob("data/vk_*.csv")
    
#     if not csv_files:
#         return render_template('dashboard.html', graphs={}, data=[])
    
#     # Собираем статистику
#     data = []
#     for file in csv_files:
#         try:
#             df = pd.read_csv(file, encoding='utf-8-sig', sep=';')
#             filename = os.path.basename(file)
#             topic = filename.replace('vk_', '').replace('.csv', '')
            
#             topic_names = {
#                 'животные': 'Животные',
#                 'игры': 'Игры',
#                 'новости': 'Новости',
#                 'творчество': 'Творчество'
#             }
#             display_name = topic_names.get(topic, topic)
            
#             stats = {
#                 'Тема': display_name,
#                 'Посты': len(df),
#                 'Лайки': float(df['likes'].mean()) if 'likes' in df.columns else 0,
#                 'Репосты': float(df['reposts'].mean()) if 'reposts' in df.columns else 0,
#                 'Комментарии': float(df['comments'].mean()) if 'comments' in df.columns else 0,
#                 'Всего_лайков': int(df['likes'].sum()) if 'likes' in df.columns else 0
#             }
#             data.append(stats)
#         except Exception as e:
#             print(f"Ошибка: {e}")
    
#     return render_template('dashboard.html', data=data)

@app.route('/collect', methods=['GET', 'POST'])
def collect_data():
    """Страница сбора данных VK"""
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
                return render_template('collect_result_vk.html', success=True)
            else:
                return render_template('collect_result_vk.html',
                                     success=False,
                                     error=result.stderr if result.stderr else "Неизвестная ошибка")
        except subprocess.TimeoutExpired:
            return render_template('collect_result_vk.html',
                                 success=False,
                                 error="Превышено время ожидания (3 минуты)")
        except Exception as e:
            return render_template('collect_result_vk.html',
                                 success=False,
                                 error=str(e))
    
    return render_template('collect_form.html')


if __name__ == '__main__':
    
    print("=" * 50)
    print("🚀 ПЛАТФОРМА АНАЛИЗА ТРЕНДОВ ЗАПУЩЕНА")
    print("=" * 50)
    print("📍 Главная страница: http://localhost:5000")
    print("=" * 50)
    print("Нажмите Ctrl+C для остановки")
    
    app.run(debug=True, port=5000)