from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# MongoDB connection
client = MongoClient(os.getenv('MONGODB_URI'))
db = client.music

# Collections
music_tracks = db.music_tracks
playlists = db.playlists
users = db.users
playlists_tracks = db.playlists_tracks

@app.route('/')
def index():
    return render_template('index.html')

# Music Tracks CRUD
@app.route('/tracks')
def list_tracks():
    all_tracks = list(music_tracks.find())
    return render_template('tracks/list.html', tracks=all_tracks)

@app.route('/tracks/add', methods=['GET', 'POST'])
def add_track():
    if request.method == 'POST':
        track = {
            'title': request.form['title'],
            'artist': request.form['artist'],
            'album': request.form['album'],
            'genre': request.form['genre'],
            'duration': int(request.form['duration']),
            'release_date': datetime.strptime(request.form['release_date'], '%Y-%m-%d')
        }
        music_tracks.insert_one(track)
        return redirect(url_for('list_tracks'))
    return render_template('tracks/add.html')

@app.route('/tracks/edit/<id>', methods=['GET', 'POST'])
def edit_track(id):
    if request.method == 'POST':
        music_tracks.update_one(
            {'_id': ObjectId(id)},
            {'$set': {
                'title': request.form['title'],
                'artist': request.form['artist'],
                'album': request.form['album'],
                'genre': request.form['genre'],
                'duration': int(request.form['duration']),
                'release_date': datetime.strptime(request.form['release_date'], '%Y-%m-%d')
            }}
        )
        return redirect(url_for('list_tracks'))
    track = music_tracks.find_one({'_id': ObjectId(id)})
    return render_template('tracks/edit.html', track=track)

@app.route('/tracks/delete/<id>')
def delete_track(id):
    music_tracks.delete_one({'_id': ObjectId(id)})
    return redirect(url_for('list_tracks'))

# Playlists CRUD
@app.route('/playlists')
@app.route('/playlists', methods=['GET'])
def list_playlists():
    all_playlists = list(playlists.find())
    
    for playlist in all_playlists:
        user = users.find_one({'_id': playlist['user_id']})
        playlist['user_first_name'] = user['first_name'] if user else 'Не призначено'
    
    return render_template('playlists/list.html', playlists=all_playlists)

@app.route('/playlists/add', methods=['GET', 'POST'])
def add_playlist():
    if request.method == 'POST':
        playlist = {
            'name': request.form['name'],
            'description': request.form['description'],
            'user_id': ObjectId(request.form['user_id']),
            'created_at': datetime.now(),
            'tracks': [ObjectId(track_id) for track_id in request.form.getlist('tracks')]
        }
        playlists.insert_one(playlist)
        return redirect(url_for('list_playlists'))
    
    all_users = list(users.find())
    all_tracks = list(music_tracks.find())
    return render_template('playlists/add.html', users=all_users, tracks=all_tracks)

@app.route('/playlists/edit/<id>', methods=['GET', 'POST'])
def edit_playlist(id):
    if request.method == 'POST':
        playlists.update_one(
            {'_id': ObjectId(id)},
            {'$set': {
                'name': request.form['name'],
                'description': request.form['description'],
                'user_id': ObjectId(request.form['user_id']),
                'tracks': [ObjectId(track_id) for track_id in request.form.getlist('tracks')]
            }}
        )
        return redirect(url_for('list_playlists'))
    playlist = playlists.find_one({'_id': ObjectId(id)})
    all_users = list(users.find())
    all_tracks = list(music_tracks.find())
    return render_template('playlists/edit.html', playlist=playlist, users=all_users, tracks=all_tracks)

@app.route('/playlists/delete/<id>')
def delete_playlist(id):
    playlists.delete_one({'_id': ObjectId(id)})
    return redirect(url_for('list_playlists'))

# Users CRUD
@app.route('/users')
def list_users():
    all_users = list(users.find())
    return render_template('users/list.html', users=all_users)

@app.route('/users/add', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        user = {
            'first_name': request.form['first_name'],
            'last_name': request.form['last_name'],
            'contact': request.form['contact']
        }
        users.insert_one(user)
        return redirect(url_for('list_users'))
    return render_template('users/add.html')

@app.route('/users/edit/<id>', methods=['GET', 'POST'])
def edit_user(id):
    if request.method == 'POST':
        users.update_one(
            {'_id': ObjectId(id)},
            {'$set': {
                'first_name': request.form['first_name'],
                'last_name': request.form['last_name'],
                'contact': request.form['contact']
            }}
        )
        return redirect(url_for('list_users'))
    user = users.find_one({'_id': ObjectId(id)})
    return render_template('users/edit.html', user=user)

@app.route('/users/delete/<id>')
def delete_user(id):
    users.delete_one({'_id': ObjectId(id)})
    return redirect(url_for('list_users'))

# playlist_track CRUD
@app.route('/playlists_tracks', methods=['GET'])
def list_playlists_tracks():
    all_playlist_tracks = list(playlists_tracks.find())
    
    for playlist_track in all_playlist_tracks:
        playlist = playlists.find_one({'_id': playlist_track['playlist_id']})
        track = music_tracks.find_one({'_id': playlist_track['track_id']})
        playlist_track['playlist_name'] = playlist['name'] if playlist else 'Невідомий плейлист'
        playlist_track['track_title'] = track['title'] if track else 'Невідомий трек'
    
    return render_template('playlists_tracks/list.html', playlists_tracks=all_playlist_tracks)

@app.route('/playlists_tracks/add', methods=['GET', 'POST'])
def add_playlist_track():
    if request.method == 'POST':
        playlist_track = {
            "playlist_id": ObjectId(request.form['playlist_id']),
            "track_id": ObjectId(request.form['track_id'])
        }
        playlists_tracks.insert_one(playlist_track)
        return redirect(url_for('list_playlists_tracks'))
    
    all_playlists = list(playlists.find())
    all_tracks = list(music_tracks.find())
    return render_template('playlists_tracks/add.html', playlists=all_playlists, music_tracks=all_tracks)


@app.route('/playlists_tracks/edit/<id>', methods=['GET', 'POST'])
def edit_playlist_track(id):
    if request.method == 'POST':
        playlists_tracks.update_one(
            {'_id': ObjectId(id)},
            {'$set': {
                "playlist_id": ObjectId(request.form['playlist_id']),
                "track_id": ObjectId(request.form['track_id']),
            }}
        )

        return redirect(url_for('list_playlists_tracks'))
    playlist_track = playlists_tracks.find_one({'_id': ObjectId(id)})
    return render_template('playlists_tracks/edit.html', playlist_track=playlist_track)

@app.route('/playlists_tracks/delete/<id>')
def delete_playlist_track(id):
    playlists_tracks.delete_one({'_id': ObjectId(id)})
    return redirect(url_for('list_playlists_tracks'))


if __name__ == '__main__':
    app.run(debug=True)
