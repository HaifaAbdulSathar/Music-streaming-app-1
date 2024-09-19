from flask_sqlalchemy import SQLAlchemy

db=SQLAlchemy()

class users(db.Model):
    user_id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(50), unique=True, nullable=False)
    email_id=db.Column(db.String(50),unique=True, nullable=False)
    password=db.Column(db.String(50), nullable=False)
    creator=db.Column(db.Boolean)
    creators=db.relationship('creators',backref='users',uselist=False)
    playlists=db.relationship('playlists',backref='users')

class creators(db.Model):
    creator_id=db.Column(db.Integer,primary_key=True)
    user_id=db.Column(db.Integer,db.ForeignKey('users.user_id'))
    blacklist=db.Column(db.Boolean)
    songs=db.relationship('songs',backref='creators', cascade='all, delete-orphan')
    albums=db.relationship('albums',backref='creators', cascade='all, delete-orphan')

class songs(db.Model):
    song_id=db.Column(db.Integer,primary_key=True)
    song_title=db.Column(db.String(120), unique=True, nullable=False) 
    artist=db.Column(db.String(50), nullable=False)
    release_date=db.Column(db.String(50))
    flag=db.Column(db.Boolean)
    creator_id=db.Column(db.Integer,db.ForeignKey('creators.creator_id'))
    album_id=db.Column(db.Integer,db.ForeignKey('albums.album_id'))
    average_rating = db.Column(db.Float)  
    ratings = db.relationship('rating', backref='song', cascade='all, delete-orphan')

class albums(db.Model):
    album_id=db.Column(db.Integer,primary_key=True)
    album_title=db.Column(db.String(50), unique=True, nullable=False)
    creator_id=db.Column(db.Integer,db.ForeignKey('creators.creator_id'))
    genre=db.Column(db.String(50), nullable=False)
    songs=db.relationship('songs',backref='albums')
    albumsong=db.relationship('albumsong',backref='albums', cascade='all, delete-orphan')

class playlists(db.Model):
    playlist_id=db.Column(db.Integer,primary_key=True)   
    playlist_name=db.Column(db.String(50), nullable=False)
    user_id=db.Column(db.Integer,db.ForeignKey('users.user_id'))
    playlistsong=db.relationship('playlistsong',backref='playlists', cascade='all, delete-orphan')
    songs=db.relationship('songs',backref='playlists',secondary='playlistsong')


class playlistsong(db.Model):
    song_id=db.Column(db.Integer,db.ForeignKey('songs.song_id'),primary_key=True)    
    playlist_id=db.Column(db.Integer,db.ForeignKey('playlists.playlist_id'),primary_key=True)

class albumsong(db.Model):
    song_id=db.Column(db.Integer,db.ForeignKey('songs.song_id'),primary_key=True)  
    album_id=db.Column(db.Integer,db.ForeignKey('albums.album_id'),primary_key=True)  

class admin(db.Model):
    admin_id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(50), unique=True, nullable=False)
    password=db.Column(db.String(50), nullable=False)


class rating(db.Model):
    rating_id=db.Column(db.Integer,primary_key=True)
    value=db.Column(db.Integer)
    user_id=db.Column(db.Integer,db.ForeignKey('users.user_id'))
    song_id=db.Column(db.Integer,db.ForeignKey('songs.song_id'))  



