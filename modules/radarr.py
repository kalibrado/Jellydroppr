import os 
import shutil
from pyarr import RadarrAPI
from modules.utils import *

def movie_finder():
    log(WHITE, "MOVIE", "Movie trailer finder started.")

    radarr = RadarrAPI(config["radarr_host"], config["radarr_api"])
    movies = radarr.get_movie()
    for movie in movies:
        num = movies.index(movie) + 1
        title = movie["title"]
        year = movie["year"]
        path = movie["path"]
        sortTitle = movie["sortTitle"]
        
        if not "tmdbId" in movie:
            log(RED, 'MOVIE', "This movies {title} does not have tmdbId" )
            continue
        
        
        tmdbId = movie["tmdbId"]
        if not os.path.exists(path):
            # log(RED, "PATH", f"'{path}' not exists.")
            continue
        disk = shutil.disk_usage(path).free
        if disk == 0:
            log(RED, f"DISK", f"Adding trailers in {path} is not possible due to insufficient disk space free {round(disk / GB, 2)}G.")
            continue
        # log(GREEN, f"DISK", f"Available disk space {round(disk / GB, 2)}G for {path}")
        file = os.path.exists(os.path.join(path, config["output_dirs"], f"{sortTitle}.{config['filetype']}"))
        if file:
            # log(WHITE, f"PATH", f"Trailer exists! for {title} " )
            continue

        log(WHITE, f"MOVIE", f"[{num}] - Title: '{title}'  - Year: '{year}'  - Path: '{path}' - TMDB-ID: '{tmdbId}' ")
        link = trailer_pull(tmdbId, "movie")
     
        trailer_download(link, movie)

        
