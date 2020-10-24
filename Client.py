
import constants
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import RedditClient
import os
from fuzzywuzzy import fuzz
# Initial client generation


class SpotifyClient():
    def __init__(self):
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=constants.constants['client_ID'],
                                                            client_secret=constants.constants['client_SECRET'],
                                                            redirect_uri=constants.constants['redirect_URI'],
                                                            scope="playlist-modify-public playlist-modify-private user-read-private user-read-recently-played"))
        self.username = constants.constants['username']
        self.token = self.generate_token()

    def generate_token(self):
        credentials = spotipy.oauth2.SpotifyClientCredentials(
            client_id=constants.constants['client_ID'],
            client_secret=constants.constants['client_SECRET'])
        token = credentials.get_access_token()
        return token
    

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
        songs_in_playlist = self.user_playlist_tracks_full(username, playlistID)
        playlisttracks = []
        res = []
        for j in range(len(songs_in_playlist)):
                playlisttracks.append(songs_in_playlist[j]['track']['id']) 
        for i in tracks:
            if i not in playlisttracks:
                res.append(i)
        print(res)        

        self.sp.user_playlist_add_tracks(username, playlistID, res) if len(res) > 0 else print("All songs already in playlist")

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
        artist_ids = []
        for artist in artists:
            if artist['id'] not in artist_ids:
                artist_ids.append(artist['id'])
        for id in artist_ids:
            try:
                result = self.sp.artist(id)
                for genre in result['genres']:
                    print(genre)
                    genres[genre] = genres.get(genre, 0)+1
            except:
                continue

        df = pd.DataFrame(genres)

        # df.to_csv('Genre_analysis.csv')

    def user_playlist_tracks_full(self, user, playlist_id=None, fields=None, market=None):
        response = self.sp.user_playlist_tracks(
            user, playlist_id, fields=fields, limit=100, market=market)
        results = response["items"]
        while len(results) < response["total"]:
            response = self.sp.user_playlist_tracks(
                user, playlist_id, fields=fields, limit=100, offset=len(results), market=market)
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
        songlist, titles = rclient.getHot('listentothis', 20)
        songs = []
        for i in titles:
            if ' -- ' in i:
                i = i.split(' -- ')
            elif ' - ' in i:
                i = i.split(' - ')
            elif ' — ' in i:
                i = i.split(' — ')
            # print(i[len(i)-1].split(' [')[0])
            temp = { 'artist' : i[0], 'title':i[len(i)-1].split(' [')[0] }
            songs.append(temp)

        self.make_playlist_with_songs(songs, 'r/listentothis')

    def make_playlist_with_songs(self, song_list, name):
        self.make_playlist(name)
        track_ids = self.gettrackids_by_artist(song_list, [])
        self.add_to_playlist(self.username, track_ids, name)

    def gettrackids_by_artist(self,sample_data, titles=[]):
        track_ids = []
        for i in range(len(sample_data)):
            results = self.sp.search(
                q=f"{sample_data[i]['title']} {sample_data[i]['artist']} ", limit=5, type='track')
            # if track isn't on spotify as queried, go to next track
            if results['tracks']['total'] == 0:
                continue
            else:
                for j in range(len(results['tracks']['items'])):
                    if fuzz.partial_ratio(results['tracks']['items'][j]['artists'][0]['name'], sample_data[i]['artist']) > 80 and fuzz.partial_ratio(results['tracks']['items'][j]['name'], sample_data[i]['title']) > 80:
                        track_ids.append(results['tracks']['items'][j]['id'])
                        break  
                    else:
                        continue
        annotation_track_ids = []
        for title in titles:
            results = self.sp.search(q=f"{title} ", type='track')
            if results['tracks']['total'] == 0:
                continue
            else:
                annotation_track_ids.append(results['tracks']['items'][0]['id'])
        track_ids = track_ids + annotation_track_ids
        print("Got TrackIDs")
        return track_ids


if __name__ == "__main__":
    client = SpotifyClient()
    client.listen_to_this()
