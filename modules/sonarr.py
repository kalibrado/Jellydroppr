from pyarr import SonarrAPI
import shutil
from modules.utils import *

def show_finder():
    log(WHITE, "SonarrAPI", "Show trailer finder started.")

    sonarr = SonarrAPI(config["sonarr_host"], config["sonarr_api"])
    shows = sonarr.get_series()
    for show in shows:
        num = shows.index(show) + 1
        title = show["title"]
        year = show["year"]
        path = show["path"] 
        sortTitle = show["sortTitle"]
        
        if not "imdbId" in show:
            log(RED, 'SHOW', "This series {title} does not have imdbId" )
            continue
        imdbId = show["imdbId"] 
        
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
        
        log(WHITE, f"SHOW", f"[{num}] - Title: '{title}'  - Year: '{year}'  - Path: '{path}' - IMDB-ID: '{imdbId}' ")
        links_episode = trailer_pull(imdbId, "tv", parent_mode=True)
        for link_episode in links_episode:
            link_episode_trailler = trailer_pull(link_episode['id'], "tv")
        
            if len(link_episode_trailler) > 0:
                trailer_download(link_episode_trailler, show)
                SHOW_TRAILLER_ADDED = SHOW_TRAILLER_ADDED + 1
            else:
                continue
        log(RED, "SHOW", f"No trailer is available for the {title}.")

