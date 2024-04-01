import os 
from pathlib import Path
import subprocess
import requests
import yaml
import yt_dlp
from time import sleep

with open("config/config.yaml", "r", encoding="utf-8") as f:
    config = yaml.load(f, Loader=yaml.Loader)

KB = 1024
MB = 1024 * KB
GB = 1024 * MB
RESET = "\033[0m"
RED = "\033[31m"
GREEN = "\033[32m"
BLUE = "\033[34m"
WHITE = "\033[37m"


def log(color, prefix, msg):
    print(color + f"[{prefix}] - {msg} " + RESET + "\n")
    sleep(1)

def trailer_pull(tmdb_id, item_type, parent_mode = False):
    log(WHITE, "PULL", f"Getting information about {tmdb_id} {item_type}")
    url = f"http://api.themoviedb.org/3/{item_type}/{tmdb_id}/videos?api_key={config['tmdb_api']}&language=fr-FR&include_video_language=fr"
    if parent_mode:
        url = f"https://api.themoviedb.org/3/find/{tmdb_id}?api_key={config['tmdb_api']}&external_source=imdb_id"
    try:
        headers = {"accept": "application/json"}
        raw_trailers = requests.get(url, headers=headers).json()
        clean_trailers = []
        if parent_mode:
            clean_trailers = raw_trailers["tv_results"]
        else:
            raw_trailers = raw_trailers["results"]
            for trailers in raw_trailers:
                if trailers["type"] == "Trailer" and trailers["site"] == "YouTube":
                    trailers["yt_link"] = config["yt_link_base"] + trailers["key"]
                    clean_trailers.append(trailers)
        return clean_trailers
    except:
        return []
   
def post_process(cache_path, files, item_path):
    log(WHITE, "POST PROCESS", f"Create '{item_path}/{config['output_dirs']}' folder ")
    os.makedirs(f'{item_path}/{config["output_dirs"]}', exist_ok=True)

    for file in files:
        filename = Path(file).stem
        base = f'ffmpeg -i "{cache_path}/{file}" -threads {config["thread_count"]} '
        base += '-c:v copy -c:a aac -af "volume=-7dB" '   
        base += f'-bufsize {config["buffer_size_ffmpeg"]} -preset slow '
        base += f'-y "{item_path}/{config["output_dirs"]}/{filename}.{config["filetype"]}" '
        log(WHITE, "FFMPEG", base)
        ffmpeg = subprocess.Popen(base, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        ffmpeg.wait()
        
def trailer_download(link, item):
    cache_path = f'cache/{item["title"]}'
    def dl_progress(d): 
        print()
        if d["status"] == "finished":
            log(GREEN, "YT_DL", "Trailer downloaded.")
        if d["status"] == "error":
            log(RED, "YT_DL", "Trailer download fail.")

    def check_duration(info, *, incomplete):
        duration = info.get('duration')
        if duration not in range(int(config['length_range'].split(",")[0]), int(config['length_range'].split(",")[1])):
            log(RED, "YT_DLP",'Video too long/short')
            raise 'Video too long/short'

    ytdl_opts = {
        "progress_hooks": [dl_progress],
        "format": "bestvideo+bestaudio",
        "outtmpl": f'{cache_path}/{item["sortTitle"]}',
        "username": config["auth_yt_user"],
        "password": config["auth_yt_pass"],
        "no_warnings": config["no_warnings"],
    }

    if config["skip_intros"]:
        ytdl_opts.update(
            {
                "postprocessors": [
                    {"key": "SponsorBlock"},
                    {
                        "key": "ModifyChapters",
                        "remove_sponsor_segments": [
                            "sponsor",
                            "intro",
                            "outro",
                            "selfpromo",
                            "preview",
                            "filler",
                            "interaction",
                        ],
                    },
                ]
            }
        )

    if config["length_range"]:
        ytdl_opts.update({'match_filter': check_duration}) 
    
    ydl = yt_dlp.YoutubeDL(ytdl_opts)

    links = list(d["yt_link"] for d in link if "yt_link" in d)
    if len(links) > 0:
        for link in links:
            if config["only_one_trailer"]:
                if os.path.exists(cache_path) and len(os.listdir(cache_path)) > 0:
                    continue 
                try:
                    log(WHITE, "YT_DLP", f"Importing {item['title']} trailers...")
                    ydl.download(link) 
                except:
                    continue
            else:
                log(WHITE, "YT_DLP", "Importing all trailers...")
                ydl.download(link)
    else:
        log(WHITE, "YT_DLP", f"No avalide links try manual search with: 'ytsearch5:{item['title']} ({item['year']}) {config['yt_search_keywords']}'")
        try:
            ydl.download([f"ytsearch5:{item['title']} ({item['year']}) {config['yt_search_keywords']}"])
        except:
            log(RED, "YT_DLP", f"No trailler found for: '{item['title']} ({item['year']})'")

            
    if os.path.exists(cache_path):
        files = os.listdir(cache_path)
        post_process(cache_path, files, item['path'] )
    else:
        log(RED, 'YT_DLP', f'No cache folder for {cache_path}')  