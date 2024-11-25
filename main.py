from flask import Flask, render_template, request, jsonify
from datetime import datetime
import requests
import sqlite3
import os

app = Flask(__name__)

# Инициализация базы данных
def init_db():
    conn = sqlite3.connect('visits.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS visits
        (timestamp TEXT, ip TEXT, country TEXT, region TEXT, 
         city TEXT, isp TEXT, referrer TEXT, user_agent TEXT)
    ''')
    conn.commit()
    conn.close()

def get_ip():
    try:
        if request.headers.get('X-Forwarded-For'):
            return request.headers.get('X-Forwarded-For').split(',')[0]
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
    
    # Сохраняем в базу данных
    conn = sqlite3.connect('visits.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO visits (timestamp, ip, country, region, city, isp, referrer, user_agent)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        visit_data['timestamp'],
        visit_data['ip'],
        visit_data['country'],
        visit_data['region'],
        visit_data['city'],
        visit_data['isp'],
        visit_data['referrer'],
        visit_data['user_agent']
    ))
    conn.commit()
    conn.close()
    
    return jsonify({'status': 'success'})

@app.route('/visits')
def visits():
    # Получаем все визиты из базы данных
    conn = sqlite3.connect('visits.db')
    c = conn.cursor()
    c.execute('SELECT * FROM visits ORDER BY timestamp DESC')
    visits_data = c.fetchall()
    conn.close()
    
    # Преобразуем в список словарей
    visits = []
    for visit in visits_data:
        visits.append({
            'timestamp': visit[0],
            'ip': visit[1],
            'country': visit[2],
            'region': visit[3],
            'city': visit[4],
            'isp': visit[5],
            'referrer': visit[6],
            'user_agent': visit[7]
        })
    
    return render_template('visits.html', visits=visits)

# Инициализируем базу данных при запуске
init_db()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
