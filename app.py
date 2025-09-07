#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NICOLI TV's - Sistema de Gerenciamento de Filmes
Interface moderna para organizar filmes em HD externo
Otimizado para uso com controle remoto e funcionamento offline
"""

import os
import sqlite3
import json
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from werkzeug.utils import secure_filename
import requests
from PIL import Image
import logging

app = Flask(__name__)
app.secret_key = 'movie_manager_secret_key_2024'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Configurar logging
logging.basicConfig(level=logging.INFO)

# Criar diretórios necessários
os.makedirs('static/uploads', exist_ok=True)
os.makedirs('static/css', exist_ok=True)
os.makedirs('static/js', exist_ok=True)
os.makedirs('templates', exist_ok=True)

def init_db():
    """Inicializar banco de dados SQLite"""
    conn = sqlite3.connect('movies.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS themes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            color TEXT DEFAULT '#667eea',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            year INTEGER,
            genre TEXT,
            director TEXT,
            description TEXT,
            file_path TEXT,
            poster_path TEXT,
            source_drive TEXT,
            rating REAL,
            duration INTEGER,
            theme_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            watched BOOLEAN DEFAULT 0,
            FOREIGN KEY (theme_id) REFERENCES themes (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS external_drives (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            drive_name TEXT NOT NULL,
            mount_point TEXT,
            total_space INTEGER,
            free_space INTEGER,
            last_scan TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Inserir temas padrão se não existirem
    cursor.execute('''
        INSERT OR IGNORE INTO themes (name, description, color) VALUES 
        ('Ação', 'Filmes de ação e aventura', '#ff6b6b'),
        ('Comédia', 'Filmes de comédia e humor', '#feca57'),
        ('Drama', 'Dramas e filmes emocionantes', '#48dbfb'),
        ('Terror', 'Filmes de terror e suspense', '#5f27cd'),
        ('Ficção Científica', 'Sci-fi e fantasia', '#00d2d3'),
        ('Romance', 'Filmes românticos', '#ff9ff3'),
        ('Documentário', 'Documentários e educacionais', '#54a0ff'),
        ('Animação', 'Desenhos animados e anime', '#5f27cd'),
        ('Clássicos', 'Filmes clássicos antigos', '#ddd')
    ''')
    
    conn.commit()
    conn.close()

def get_db_connection():
    """Obter conexão com banco de dados"""
    conn = sqlite3.connect('movies.db')
    conn.row_factory = sqlite3.Row
    return conn

def scan_external_drives():
    """Escanear drives externos conectados"""
    drives = []
    try:
        # Escanear /media e /mnt para drives externos
        for mount_point in ['/media', '/mnt']:
            if os.path.exists(mount_point):
                for drive in os.listdir(mount_point):
                    drive_path = os.path.join(mount_point, drive)
                    if os.path.ismount(drive_path):
                        try:
                            stat = os.statvfs(drive_path)
                            total_space = stat.f_frsize * stat.f_blocks
                            free_space = stat.f_frsize * stat.f_bavail
                            drives.append({
                                'name': drive,
                                'path': drive_path,
                                'total_space': total_space,
                                'free_space': free_space
                            })
                        except Exception as e:
                            logging.warning(f"Erro ao acessar drive {drive_path}: {e}")
    except Exception as e:
        logging.error(f"Erro ao escanear drives: {e}")
    
    return drives

def scan_movies_in_drive(drive_path):
    """Escanear filmes em um drive específico"""
    movie_extensions = {'.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v'}
    movies = []
    
    try:
        for root, dirs, files in os.walk(drive_path):
            for file in files:
                if any(file.lower().endswith(ext) for ext in movie_extensions):
                    file_path = os.path.join(root, file)
                    file_size = os.path.getsize(file_path)
                    movies.append({
                        'filename': file,
                        'path': file_path,
                        'size': file_size,
                        'title': os.path.splitext(file)[0]
                    })
    except Exception as e:
        logging.error(f"Erro ao escanear filmes em {drive_path}: {e}")
    
    return movies

@app.route('/')
def index():
    """Página principal"""
    conn = get_db_connection()
    movies = conn.execute('SELECT * FROM movies ORDER BY created_at DESC LIMIT 10').fetchall()
    themes = conn.execute('SELECT * FROM themes ORDER BY name').fetchall()
    drives = scan_external_drives()
    conn.close()
    
    return render_template('index.html', movies=movies, drives=drives, themes=themes)

@app.route('/movies')
def list_movies():
    """Listar todos os filmes"""
    conn = get_db_connection()
    movies = conn.execute('SELECT * FROM movies ORDER BY title').fetchall()
    conn.close()
    
    return render_template('movies.html', movies=movies)

@app.route('/add_movie', methods=['GET', 'POST'])
def add_movie():
    """Adicionar novo filme"""
    if request.method == 'POST':
        title = request.form['title']
        year = request.form.get('year', type=int)
        genre = request.form['genre']
        director = request.form['director']
        description = request.form['description']
        rating = request.form.get('rating', type=float)
        duration = request.form.get('duration', type=int)
        
        # Sistema offline simplificado - não usa file_path, source_drive nem theme_id
        
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO movies (title, year, genre, director, description, rating, duration)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (title, year, genre, director, description, rating, duration))
        conn.commit()
        conn.close()
        
        flash('Filme adicionado com sucesso!', 'success')
        return redirect(url_for('list_movies'))
    
    conn = get_db_connection()
    drives = scan_external_drives()
    themes = conn.execute('SELECT * FROM themes ORDER BY name').fetchall()
    conn.close()
    return render_template('add_movie.html', drives=drives, themes=themes)

@app.route('/scan_drive/<path:drive_path>')
def scan_drive(drive_path):
    """Escanear filmes em um drive específico"""
    movies = scan_movies_in_drive(drive_path)
    return jsonify(movies)

@app.route('/movie/<int:movie_id>')
def movie_detail(movie_id):
    """Detalhes de um filme específico"""
    conn = get_db_connection()
    movie = conn.execute('SELECT * FROM movies WHERE id = ?', (movie_id,)).fetchone()
    conn.close()
    
    if movie is None:
        flash('Filme não encontrado!', 'error')
        return redirect(url_for('list_movies'))
    
    return render_template('movie_detail.html', movie=movie)

@app.route('/edit_movie/<int:movie_id>', methods=['GET', 'POST'])
def edit_movie(movie_id):
    """Editar filme existente"""
    conn = get_db_connection()
    movie = conn.execute('SELECT * FROM movies WHERE id = ?', (movie_id,)).fetchone()
    
    if movie is None:
        flash('Filme não encontrado!', 'error')
        return redirect(url_for('list_movies'))
    
    if request.method == 'POST':
        title = request.form['title']
        year = request.form.get('year', type=int)
        genre = request.form['genre']
        director = request.form['director']
        description = request.form['description']
        file_path = request.form['file_path']
        source_drive = request.form.get('source_drive', '')
        rating = request.form.get('rating', type=float)
        duration = request.form.get('duration', type=int)
        theme_id = request.form.get('theme_id', type=int)
        
        conn.execute('''
            UPDATE movies 
            SET title=?, year=?, genre=?, director=?, description=?, file_path=?, source_drive=?, rating=?, duration=?, theme_id=?
            WHERE id=?
        ''', (title, year, genre, director, description, file_path, source_drive, rating, duration, theme_id, movie_id))
        conn.commit()
        conn.close()
        
        flash('Filme atualizado com sucesso!', 'success')
        return redirect(url_for('movie_detail', movie_id=movie_id))
    
    themes = conn.execute('SELECT * FROM themes ORDER BY name').fetchall()
    conn.close()
    drives = scan_external_drives()
    return render_template('edit_movie.html', movie=movie, drives=drives, themes=themes)

@app.route('/delete_movie/<int:movie_id>', methods=['POST'])
def delete_movie(movie_id):
    """Deletar filme"""
    conn = get_db_connection()
    conn.execute('DELETE FROM movies WHERE id = ?', (movie_id,))
    conn.commit()
    conn.close()
    
    flash('Filme removido com sucesso!', 'success')
    return redirect(url_for('list_movies'))

@app.route('/toggle_watched/<int:movie_id>', methods=['POST'])
def toggle_watched(movie_id):
    """Marcar/desmarcar filme como assistido"""
    conn = get_db_connection()
    movie = conn.execute('SELECT watched FROM movies WHERE id = ?', (movie_id,)).fetchone()
    
    new_status = False
    if movie:
        new_status = not movie['watched']
        conn.execute('UPDATE movies SET watched = ? WHERE id = ?', (new_status, movie_id))
        conn.commit()
    
    conn.close()
    return jsonify({'success': True, 'watched': new_status})

@app.route('/api/drives')
def api_drives():
    """API para obter drives externos"""
    drives = scan_external_drives()
    return jsonify(drives)

@app.route('/themes')
def list_themes():
    """Listar todos os temas"""
    conn = get_db_connection()
    themes = conn.execute('SELECT * FROM themes ORDER BY name').fetchall()
    conn.close()
    
    return render_template('themes.html', themes=themes)

@app.route('/theme/<int:theme_id>')
def theme_movies(theme_id):
    """Listar filmes por tema"""
    conn = get_db_connection()
    theme = conn.execute('SELECT * FROM themes WHERE id = ?', (theme_id,)).fetchone()
    # Sistema simplificado - organização por gênero em vez de tema
    movies = conn.execute('''
        SELECT * FROM movies 
        ORDER BY title
    ''').fetchall()
    conn.close()
    
    return render_template('theme_movies.html', theme=theme, movies=movies)

@app.route('/add_theme', methods=['GET', 'POST'])
def add_theme():
    """Adicionar novo tema"""
    if request.method == 'POST':
        name = request.form['name']
        description = request.form.get('description', '')
        color = request.form.get('color', '#667eea')
        
        conn = get_db_connection()
        try:
            conn.execute('''
                INSERT INTO themes (name, description, color)
                VALUES (?, ?, ?)
            ''', (name, description, color))
            conn.commit()
            flash('Tema adicionado com sucesso!', 'success')
        except sqlite3.IntegrityError:
            flash('Tema já existe!', 'error')
        finally:
            conn.close()
        
        return redirect(url_for('list_themes'))
    
    return render_template('add_theme.html')

@app.route('/api/movies')
def api_movies():
    """API para obter lista de filmes"""
    conn = get_db_connection()
    movies = conn.execute('''
        SELECT * FROM movies 
        ORDER BY created_at DESC
    ''').fetchall()
    conn.close()
    
    movies_list = []
    for movie in movies:
        movies_list.append({
            'id': movie['id'],
            'title': movie['title'],
            'year': movie['year'],
            'genre': movie['genre'],
            'director': movie['director'],
            'description': movie['description'],
            'file_path': movie['file_path'],
            'source_drive': movie['source_drive'],
            'poster_path': movie['poster_path'],
            'rating': movie['rating'],
            'duration': movie['duration'],
            'watched': movie['watched'],
            'theme_name': movie['theme_name'],
            'theme_color': movie['theme_color']
        })
    
    return jsonify(movies_list)

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)