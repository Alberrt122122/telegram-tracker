from flask import Flask, render_template, request, jsonify
from datetime import datetime
import requests
import json
import os

app = Flask(__name__)

# Путь к файлу с данными о посещениях
VISITS_FILE = 'visits.json'

def load_visits():
    try:
        if os.path.exists(VISITS_FILE):
            with open(VISITS_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading visits: {e}")
    return []

def save_visits(visits):
    try:
        with open(VISITS_FILE, 'w') as f:
            json.dump(visits, f, indent=2)
    except Exception as e:
        print(f"Error saving visits: {e}")

def get_ip():
    try:
        response = requests.get('https://api.ipify.org?format=json')
        return response.json()['ip']
    except:
        return request.remote_addr

def get_location_info(ip):
    try:
        response = requests.get(f'http://ip-api.com/json/{ip}')
        data = response.json()
        if data['status'] == 'success':
            return {
                'country': data['country'],
                'region': data['regionName'],
                'city': data['city'],
                'isp': data['isp']
            }
    except:
        pass
    return {
        'country': 'Unknown',
        'region': 'Unknown',
        'city': 'Unknown',
        'isp': 'Unknown'
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/track_visit')
def track_visit():
    ip = get_ip()
    location = get_location_info(ip)
    
    visit_data = {
        'timestamp': datetime.now().isoformat(),
        'ip': ip,
        'country': location['country'],
        'region': location['region'],
        'city': location['city'],
        'isp': location['isp'],
        'referrer': request.referrer or 'Direct',
        'user_agent': request.user_agent.string
    }
    
    # Загружаем существующие визиты
    visits = load_visits()
    # Добавляем новый визит
    visits.append(visit_data)
    # Сохраняем обновленный список
    save_visits(visits)
    
    return jsonify({'status': 'success'})

@app.route('/visits')
def visits():
    # Получаем все визиты из файла
    all_visits = load_visits()
    # Сортируем по времени в обратном порядке
    all_visits.sort(key=lambda x: x['timestamp'], reverse=True)
    return render_template('visits.html', visits=all_visits)

if __name__ == '__main__':
    app.run(debug=True)
