
import constants
import requests
import json
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os

# Initial client generation

class SpotifyClient():
    def __init__(self):
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=constants.constants['client_ID'],
                                                client_secret=constants.constants['client_SECRET'],
                                                redirect_uri=constants.constants['redirect_URI'],
                                                scope="playlist-modify-public playlist-modify-private user-read-private user-read-recently-played"))
        self.username = constants.constants['username']

    def makePlayList(self,name):
        self.sp.user_playlist_create(constants.constants['username'], name=name) if self.getPlayListID(constants.constants['username'], name) == '' else print("Playlist exists")


    def getPlayListID(self,username, playlistname):
        playlistid = ''
        playlists = self.sp.user_playlists(username)
        for playlist in playlists['items']:
            if playlist['name'] == playlistname:
                playlistid = playlist['id']

        return playlistid


    def addToPlaylist(self,username, tracks, playlistname):
        playlistID = self.getPlayListID(username, playlistname)
        self.sp.user_playlist_add_tracks(username, playlistID, tracks)


    def GetTrackIDs(self, data):
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


    def analyseGenres(self,username):
        genres = []
        playlists = self.sp.user_playlists(username)


    def makePlayListwithSongs(self, path_to_dir, name):
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
        self.makePlayList(name)
        track_ids = self.GetTrackIDs(names)
        self.addToPlaylist(self.username,track_ids, name)


if __name__ == "__main__":
    client = SpotifyClient()
    
    
