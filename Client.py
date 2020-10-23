
import constants
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import RedditClient
import os
import csv

# Initial client generation


class SpotifyClient():
    def __init__(self):
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=constants.constants['client_ID'],
                                                            client_secret=constants.constants['client_SECRET'],
                                                            redirect_uri=constants.constants['redirect_URI'],
                                                            scope="playlist-modify-public playlist-modify-private user-read-private user-read-recently-played"))
        self.username = constants.constants['username']



    def make_playlist(self, name):
        self.sp.user_playlist_create(constants.constants['username'], name=name) if self.get_playlist_id(
            constants.constants['username'], name) == '' else print("Playlist exists")



    def get_playlist_id(self, username, playlistname):
        playlistid = ''
        playlists = self.sp.user_playlists(username)
        for playlist in playlists['items']:
            if playlist['name'] == playlistname:
                playlistid = playlist['id']

        return playlistid



    def add_to_playlist(self, username, tracks, playlistname):
        playlistID = self.get_playlist_id(username, playlistname)
        self.sp.user_playlist_add_tracks(username, playlistID, tracks)



    def get_track_ids(self, data):
        track_ids = []
        for i in range(len(data)):
            try:
                results = self.sp.search(q=f"{data[i]}")
                if results['tracks']['total'] == 0:
                    continue
                else:
                    for j in range(len(results['tracks']['items'])):
                        # print(results['tracks']['items'][j])
                        track_ids.append(results['tracks']['items'][j]['id'])
                        # print(track_ids)
                        break
            except:
                continue

        return track_ids



    def get_artists(self, username):
        final_results = []
        artists = []
        playlists = self.sp.user_playlists(username)
        for playlist in playlists['items']:
            # print(playlist['id'])
            res = self.user_playlist_tracks_full(self.username, playlist['id'])
            final_results.extend(res)
        for song in final_results:
            try:
                artists.extend(song['track']['artists'])
            except:
                continue    
        
        return artists
    


    def analyse_genres(self, username):
        genres = {}
        artists = self.get_artists(username)
        artist_ids=[]
        for artist in artists:
            if artist['id'] not in artist_ids:
                artist_ids.append(artist['id'])
        for id in artist_ids:
            try:
                result = self.sp.artist(id)
                for genre in result['genres']:
                    print(genre)
                    genres[genre] = genres.get(genre,0)+1
            except:
                continue        

        df = pd.DataFrame(genres)
        # df.to_csv('Genre_analysis.csv')

          

               

               

    def user_playlist_tracks_full(self, user, playlist_id=None, fields=None, market=None):
        response = self.sp.user_playlist_tracks(user, playlist_id, fields=fields, limit=100, market=market)
        results = response["items"]
        while len(results) < response["total"]:
            response = self.sp.user_playlist_tracks(user, playlist_id, fields=fields, limit=100, offset=len(results), market=market)
            results.extend(response["items"])
        return results    



    def make_playlist_with_dir(self, path_to_dir, name):
        curdir = os.chdir(path_to_dir)
        f = []
        for(dirpath, dirnames, filenames) in os.walk(os.curdir):
            f.extend(filenames)
            break
        names = []
        for i in f:
            if '.mp3' in i:
                names.append(i.split('.mp3')[0])
        # print(names)
        self.make_playlist(name)
        track_ids = self.get_track_ids(names)
        self.add_to_playlist(self.username, track_ids, name)



    def listen_to_this(self):
        rclient = RedditClient.RedditClient()
        songlist = rclient.getHot('listentothis', 20)
        new_list = list(songlist)
        self.make_playlistwithSongs(new_list, 'r/listentothis')



    def make_playlist_with_songs(self, song_list, name):
        self.make_playlist(name)
        track_ids = self.get_track_ids(song_list)
        self.add_to_playlist(self.username, track_ids, name)


if __name__ == "__main__":
    client = SpotifyClient()
    client.analyse_genres(constants.constants['username'])
