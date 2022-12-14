import re
import spotipy
import sys
import pprint
import random
import py_eureka_client.eureka_client as eureka_client

from spotipy.oauth2 import SpotifyClientCredentials
from flask import Flask, request
from http import client
from py_eureka_client import netint_utils

client_id= '8ccb512ab6f5404bb835edf9502d238e'
client_secret='297adc4aa85844f1a6d9fa65f631479b' 
artist = None
song = None
href = None
uri = None
url_ext = None
duration = None
estados = {'Alegre':'',
    'Triste':'',
    'Enojado':'',
    'Miedo':'',
    'Neutro':''}

# create the Flask app
app = Flask(__name__)

# heroku credentials
host="music-spotipy.herokuapp.com"
rest_port = 8080
ip = netint_utils.get_first_non_loopback_ip("192.168.10.0/24")
eureka_client.init(eureka_server="http://52.73.98.2:8099/eureka",
                   app_name="music-spotipy", 
                   instance_port=rest_port, 
                   instance_host=host,
                   instance_ip=ip)



# GET requests will be blocked
@app.route('/animo', methods=['POST'])
def animo():
    request_data = request.get_json()

    estado = None
    error = []
    if request_data:
        for req in request_data:
            if req == 'estado':
                estado = request_data['estado']
                if estado in estados:
                    if estados[estado] != '':
                        definir_lista(estado)
                    else:
                        error.append("No se a definido la playlist para "+estado)
                        
                else:
                    error.append("No existe el estado '"+estado+"'")
            else:
                error.append("No existe '"+req+"'como parametro")
        

    return {"state": estado,"song":song,"artist":artist,"href":href,"uri":uri,"url_ext":url_ext,"duration_ms":duration,"error":error}

# GET requests will be blocked
@app.route('/playlist', methods=['POST'])
def playlist():
    request_data = request.get_json()
    error = []
    url = None
    
    if request_data:
        for req in request_data:
            if req in estados:
                url = request_data[req]
                definir_playlist(req,url)    
            else:
                error.append("No existe el estado de animo seleccionado ("+req+")")
        estados["error"] = error
    return estados
   
              
def definir_playlist(state,url):
    global estados
    if state  in estados:
        estados[state] = url
    else:
        error ='error state not found'
        return error

def definir_lista(item):
    global artist
    global song
    global href
    global uri
    global url_ext
    global duration
    
    if item in estados:
        playlist_id = estados[item]
        sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id,client_secret))
        results = sp.playlist(playlist_id)
        lista = results['tracks']['items']
        n = len(lista)
   
        if n > 0:
            i = random.randrange(n)
            song = results['tracks']['items'][i]['track']['name']
            artist = results['tracks']['items'][i]['track']['artists'][0]['name']
            href = results['tracks']['items'][i]['track']['href']
            uri = results['tracks']['items'][i]['track']['uri']
            url_ext = results['tracks']['items'][i]['track']['external_urls']['spotify']
            duration = results['tracks']['items'][i]['track']['duration_ms']

if __name__ == '__main__':
    # run app in debug mode on port 5000
    app.run(port='8080',debug=False, host='0.0.0.0')