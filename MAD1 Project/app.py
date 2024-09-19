from flask import Flask,render_template,redirect,url_for,request
from model import * 
from model import db
import os
from sqlalchemy import or_,func

app=Flask(__name__)
app.config['UPLOAD_FOLDER']='static/audios'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///musicdatabase.sqlite3'
db.init_app(app)
app.app_context().push()

@app.route('/', methods=['GET','POST'])
def userlogin():
    if request.method=='POST':
        login_username=request.form.get('login_username')
        login_password=request.form.get('login_password')
        this_user=users.query.filter_by(username=login_username).first()
        if not this_user:
            return '<p>Please Enter Valid Credentials or Register as a new user</p><br><a href="/">Go Back</a>'
        elif this_user.password==login_password and this_user.creator==False:
            return redirect(url_for('userhome',user_id=this_user.user_id))
        elif this_user.password==login_password and this_user.creator==True:
            this_creator=creators.query.filter_by(user_id=this_user.user_id).first()
            song_list=songs.query.filter_by(flag=False)
            my_song_list=songs.query.filter_by(creator_id=this_creator.creator_id)
            myplaylists=playlists.query.filter_by(user_id=this_user.user_id).all()
            myalbums=albums.query.filter_by(creator_id=this_creator.creator_id).all()
            all_albums=albums.query.all()
            return render_template('creatorhome.html',this_user=this_user,song_list=song_list,this_creator=this_creator,my_song_list=my_song_list,myplaylists=myplaylists,myalbums=myalbums,all_albums=all_albums)
        else:
            return '<p>Enter Valid Credentials or Register as a new user</p><br><a href="/">Go Back</a>'

    return render_template('userlogin.html')        


@app.route('/register', methods=['GET','POST'])
def register():
    if request.method=='POST':
        register_email=request.form.get('register_email')
        register_username=request.form.get('register_username')
        register_password=request.form.get('register_password')
        new_user=users(email_id=register_email, username=register_username,password=register_password,creator=False)
        db.session.add(new_user)
        db.session.commit()
        return redirect('/')
    return render_template('registerpage.html')

@app.route('/userhome/<int:user_id>', methods=['GET','POST'])
def userhome(user_id):
    this_user=users.query.get(user_id)
    song_list=songs.query.filter_by(flag=False)
    myplaylists=playlists.query.filter_by(user_id=this_user.user_id).all()
    all_albums=albums.query.all()
    return render_template('userhome.html',song_list=song_list,this_user=this_user,myplaylists=myplaylists,all_albums=all_albums)  


@app.route('/creatorhome/<int:user_id>/<int:creator_id>')
def creatorhome(user_id,creator_id):
    this_creator=creators.query.get(creator_id)
    this_user=creators.query.filter_by(user_id=user_id).first()
    song_list=songs.query.filter_by(flag=False)
    my_song_list=songs.query.filter_by(creator_id=creator_id)
    myplaylists=playlists.query.filter_by(user_id=this_user.user_id).all()
    myalbums=albums.query.filter_by(creator_id=this_creator.creator_id).all()
    all_albums=albums.query.all()
    return render_template('creatorhome.html',this_user=this_user,song_list=song_list,this_creator=this_creator,my_song_list=my_song_list,myplaylists=myplaylists,myalbums=myalbums,all_albums=all_albums)

@app.route('/creatorregister', methods=['GET','POST'])        
def creatorregister():
    if request.method=='POST':
        login_username=request.form.get('login_username')
        login_password=request.form.get('login_password')
        this_user=users.query.filter_by(username=login_username).first()
        if this_user.password==login_password:
            this_user.creator=True
            db.session.commit()         
            new_creator=creators(user_id=this_user.user_id,blacklist=False)
            db.session.add(new_creator)
            db.session.commit()
            return redirect(url_for('userlogin'))
        return f"<p>Registration Failed.Enter valid credentials</p><a href='/userhome/{this_user.user_id}'>Go to Home</a>"
    return render_template('creatorregister.html')

@app.route('/uploadsong/<int:user_id>/<int:creator_id>', methods=['GET','POST'])
def uploadsong(user_id,creator_id):
    if request.method=='POST':
        song_file=request.files['song_file']
        file_name=song_file.filename
        song_file.save(os.path.join(app.config['UPLOAD_FOLDER'],file_name))
        new_song=songs(song_title=file_name,artist=request.form.get('artist_name'),release_date=request.form.get('release_date'),creator_id=creator_id,flag=False)
        db.session.add(new_song)
        db.session.commit()
        return redirect(url_for('creatorhome', creator_id=creator_id,user_id=user_id))
    return render_template('uploadsong.html',this_creator=creators.query.get(creator_id),this_user=users.query.get(user_id))

@app.route('/delete/<int:song_id>')
def delete(song_id):
    this_song=songs.query.get(song_id)
    creator_id=this_song.creator_id
    this_creator=creators.query.get(creator_id)
    user_id=this_creator.user_id
    playlist=playlistsong.query.filter_by(song_id=song_id).all()
    album=albumsong.query.filter_by(song_id=song_id).all()
    for entry in playlist:
        db.session.delete(entry)
    for entry in album:
        db.session.delete(entry)    
    db.session.delete(this_song)
    db.session.commit()
    return redirect(url_for('creatorhome', creator_id=creator_id,user_id=user_id))

@app.route('/search', methods=['GET','POST'])
def search():
    search_key=request.form.get('search_key')
    songs_result=songs.query.filter(or_(songs.song_title.ilike(f'%{search_key}%'),songs.artist.ilike(f'%{search_key}%')))
    return render_template('searchresults.html',songs_result=songs_result)

@app.route('/searchalbum', methods=['GET','POST'])
def searchalbum():
    search_key=request.form.get('search_key')
    albums_result=albums.query.filter(or_(albums.album_title.ilike(f'%{search_key}%'),albums.genre.ilike(f'%{search_key}%')))
    return render_template('searchalbumsresults.html',albums_result=albums_result)

@app.route('/createplaylist/<int:user_id>', methods=['GET','POST'])
def createplaylist(user_id):
    this_user=users.query.get(user_id)
    song_list=songs.query.filter_by(flag=False)
    this_creator=creators.query.filter_by(user_id=user_id).first()
    if request.method=='POST':
        playlist_name=request.form.get('playlist_name')
        playlist_songs=request.form.getlist('checkbox_item')
        new_playlist=playlists(playlist_name=playlist_name,user_id=user_id)
        db.session.add(new_playlist)
        db.session.commit()
        for song_id in playlist_songs:
            this_playlist=playlists.query.filter_by(playlist_name=playlist_name).first()
            new_playlistsongrel=playlistsong(song_id=song_id,playlist_id=this_playlist.playlist_id)
            db.session.add(new_playlistsongrel)
            db.session.commit()
        if this_user.creator==True:
            creator_id=this_creator.creator_id
            return redirect(url_for('creatorhome',user_id=user_id,creator_id=creator_id))    
        return redirect(url_for('userhome',user_id=user_id))

    return render_template('createplaylist.html',this_user=this_user,song_list=song_list,this_creator=this_creator)

@app.route('/editplaylists/<int:user_id>', methods=['GET','POST'])
def editplaylists(user_id):
    this_user=users.query.get(user_id)
    this_creator=creators.query.filter_by(user_id=user_id).first()
    song_list=songs.query.filter_by(flag=False)
    myplaylists=playlists.query.filter_by(user_id=this_user.user_id).all()
    return render_template('editplaylists.html',this_user=this_user,song_list=song_list,myplaylists=myplaylists,this_creator=this_creator)

@app.route('/deleteplaylistsong/<int:user_id>/<int:playlist_id>',methods=['GET','POST'])
def deleteplaylistsong(user_id,playlist_id):
    playlist_songs=request.form.getlist('delete_checkbox')
    for song_id in playlist_songs:
        this_song=playlistsong.query.filter_by(song_id=song_id,playlist_id=playlist_id).first()
        db.session.delete(this_song)
        db.session.commit()  
    playlist=playlists.query.get(playlist_id)
    if not playlist.songs:
        db.session.delete(playlist)
        db.session.commit()    
    return redirect(url_for('editplaylists',user_id=user_id))   

@app.route('/addplaylistsong/<int:user_id>/<int:playlist_id>',methods=['GET','POST']) 
def addplaylistsong(user_id,playlist_id):
    playlist_songs=request.form.getlist('add_checkbox')
    for song_id in playlist_songs:
        new_playslistsong_rel=playlistsong(song_id=song_id,playlist_id=playlist_id)
        db.session.add(new_playslistsong_rel)
        db.session.commit()
    return redirect(url_for('editplaylists',user_id=user_id))   

@app.route('/rate/<int:user_id>/<int:song_id>', methods=['GET','POST'])
def rate(user_id,song_id):
    if request.method=='POST':
        this_user=rating.query.filter_by(user_id=user_id,song_id=song_id).first()
        if not this_user:
            value=int(request.form.get('inlineRadioOptions'))
            new_rating=rating(value=value,user_id=user_id,song_id=song_id)
            db.session.add(new_rating)
            db.session.commit()
            average_ratings=db.session.query(songs.song_id,func.avg(rating.value).label('average_rating')).join(rating).group_by(songs.song_id).all()
            for song_id,average_rating in average_ratings:
                this_song=songs.query.get(song_id)
                this_song.average_rating=average_rating
                db.session.commit()
            return redirect(url_for('userhome',user_id=user_id))    
        else:
            return 'You have already rated this song'
    return render_template('rate.html',user_id=user_id,song_id=song_id)

@app.route('/createalbum/<int:user_id>/<int:creator_id>',methods=['GET','POST'])   
def createalbum(user_id,creator_id):
    my_song_list=songs.query.filter_by(creator_id=creator_id)
    if request.method=='POST':
        album_title=request.form.get('album_title')
        genre=request.form.get('genre')
        album_songs=request.form.getlist('checkbox_item')
        new_album=albums(album_title=album_title,creator_id=creator_id,genre=genre)
        db.session.add(new_album)
        db.session.commit()
        for song_id in album_songs:
            this_song=songs.query.get(song_id)
            this_album=albums.query.filter_by(album_title=album_title).first()
            new_albumsongrel=albumsong(song_id=song_id,album_id=this_album.album_id)
            db.session.add(new_albumsongrel)
            db.session.commit()
            this_song.album_id=this_album.album_id
            db.session.commit()
        return redirect(url_for('creatorhome',user_id=user_id,creator_id=creator_id))
    return render_template('createalbum.html',user_id=user_id,creator_id=creator_id,my_song_list=my_song_list)

@app.route('/editalbums/<int:user_id>/<int:creator_id>',methods=['GET','POST'])
def editalbums(user_id,creator_id):
    this_user=users.query.get(user_id)
    song_list=songs.query.filter_by(creator_id=creator_id)
    myalbums=albums.query.filter_by(creator_id=creator_id).all()
    return render_template('editalbums.html',myalbums=myalbums,this_user=this_user,song_list=song_list,creator_id=creator_id)

@app.route('/deletealbumsong/<int:user_id>/<int:album_id>',methods=['GET','POST'])
def deletealbumsong(user_id,album_id):
    this_album=albums.query.get(album_id)
    creator_id=this_album.creator_id
    album_songs=request.form.getlist('delete_checkbox')
    for song_id in album_songs:
        this_song=songs.query.get(song_id)
        this_song.album_id=None
        db.session.commit()
        this_albumsong=albumsong.query.filter_by(song_id=song_id,album_id=album_id).first()
        db.session.delete(this_albumsong)
        db.session.commit()
    if not this_album.songs:
        db.session.delete(this_album)
        db.session.commit()    
    return redirect(url_for('editalbums',user_id=user_id,creator_id=creator_id))

@app.route('/addalbumsong/<int:user_id>/<int:album_id>',methods=['GET','POST'])
def addalbumsong(user_id,album_id):
    this_album=albums.query.get(album_id)
    creator_id=this_album.creator_id
    album_songs=request.form.getlist('add_checkbox')
    for song_id in album_songs:
        this_song=songs.query.get(song_id) 
        this_song.album_id=this_album.album_id
        db.session.commit() 
        new_albumsong_rel=albumsong(song_id=song_id,album_id=album_id)
        db.session.add(new_albumsong_rel)
        db.session.commit()
    return redirect(url_for('editalbums',user_id=user_id,creator_id=creator_id))

@app.route('/adminlogin',methods=['GET','POST'])
def adminlogin():
    admin_username=request.form.get('admin_username')
    admin_password=request.form.get('admin_password')
    if request.method=='POST':
        this_admin=admin.query.first()
        if admin_username==this_admin.username and admin_password==this_admin.password:
            return redirect(url_for('adminhome'))
        else:
            return 'invalid credentials'
    return render_template('adminlogin.html')

@app.route('/adminhome',methods=['GET','POST'])
def adminhome():
    all_songs=songs.query.all()
    songs_count = songs.query.count()
    all_users=users.query.all()
    users_count = users.query.count()
    all_creators=creators.query.all()
    creators_count = creators.query.count()
    all_albums=albums.query.all()
    albums_count=albums.query.count()
    return render_template('adminhome.html',all_songs=all_songs,all_users=all_users,all_creators=all_creators,songs_count=songs_count,users_count=users_count,creators_count=creators_count,all_albums=all_albums,albums_count=albums_count)

@app.route('/flag/<int:song_id>')
def flag(song_id):
    this_song=songs.query.get(song_id) 
    this_song.flag=True
    db.session.commit()
    return redirect(url_for('adminhome'))

@app.route('/unflag/<int:song_id>')
def unflag(song_id):
    this_song=songs.query.get(song_id) 
    this_song.flag=False
    db.session.commit()
    return redirect(url_for('adminhome'))

@app.route('/blacklist/<int:creator_id>')
def blacklist(creator_id):
    this_creator=creators.query.get(creator_id)
    this_creator.blacklist=True
    db.session.commit()
    return redirect(url_for('adminhome'))

@app.route('/whitelist/<int:creator_id>')
def whitelist(creator_id):
    this_creator=creators.query.get(creator_id)
    this_creator.blacklist=False
    db.session.commit()
    return redirect(url_for('adminhome'))    

if __name__ == "__main__":
    app.run(debug=True)

    