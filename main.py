import os  
import shutil  
from time import sleep
import threading
from modules.utils import *
from modules.radarr  import movie_finder
from modules.sonarr  import show_finder

def main():
    try:
        os.makedirs(f"cache", exist_ok=True)
        log(GREEN, "CREATE", "Created cache directory.")
    except:
        log(RED, "CREATE", "Cache directory found.")
        
    while True:
        log(WHITE, "CACHE", f"Clean cache")
        shutil.rmtree("cache/", ignore_errors=True)
        
        if all(x in config for x in ["radarr_host", "radarr_api"]):
            movie_finder()
	        # movie_thread = threading.Thread(name="MOVIE", target=movie_finder, daemon=True )
        if all(x in config for x in ['sonarr_host', 'sonarr_api']):
            show_finder()
            # show_thread = threading.Thread(name="SHOW", target=show_finder, daemon=True )

        # movie_thread.start()
        # show_thread.start()
        
        # movie_thread.join()
        # show_thread.join()
        
        log(WHITE, "CACHE", f"Clean cache")
        shutil.rmtree("cache/", ignore_errors=True)
       
        if "sleep_time" in config:
            log(WHITE, "WAIT", f"Operation complete. \n Waiting {config['sleep_time'] * 3600} minute(s).")
            sleep(config['sleep_time'] * 3600)
        else:
            log(WHITE, "FINISH", f"Operation complete. \n No sleep time was set, stopping.")
            exit()




if __name__ == '__main__':
    main()
