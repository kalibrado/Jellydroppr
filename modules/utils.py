import os 
from pathlib import Path
import subprocess
import requests
import yaml
import yt_dlp

with open("config/config.yaml", "r", encoding="utf-8") as f:
    config = yaml.load(f, Loader=yaml.Loader)


MOVIE_TRAILLER_ADDED = 0
SHOW_TRAILLER_ADDED = 0
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
   
def post_process(cache_path, files, item_path, bitrate = None, cropvalue = None):
    log(WHITE, "POST PROCESS", f"Create '{item_path}/{config['output_dirs']}' folder ")
    os.makedirs(f'{item_path}/{config["output_dirs"]}', exist_ok=True)

    for file in files:
        filename = Path(file).stem
        base = f'ffmpeg -i "{cache_path}/{file}" -threads {config["thread_count"]} '
        if cropvalue:
            base += f'-vf {cropvalue} -c:v libx264 '
        if bitrate:
            base += f'-b:v {bitrate*140} -maxrate {bitrate*140} '
        if not cropvalue and not bitrate:
            base += '-c:v copy -c:a aac -af "volume=-7dB" '
            
        base += f'-bufsize {config["buffer_size_ffmpeg"]} -preset slow '
        base += f'-y "{item_path}/{config["output_dirs"]}/{filename}.{config["filetype"]}" '
        log(WHITE, "FFMPEG", base)
        ffmpeg = subprocess.Popen(base, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        ffmpeg.wait()
        
def remove_black_borders(files):
    for file in files:
        log(WHITE, "BLACK BORDER", f"Looking for black borders {file} ...")
        cropvalue = subprocess.check_output(f"ffmpeg -i '{file}' -t 30 -vf cropdetect -f null - 2>&1 | awk "
                                        "'/crop/ {{ print $NF }}' | tail -1",
                                            shell=True).decode('utf-8').strip()
        log(WHITE, "DEBUG BLACK BORDER", cropvalue)
        l = [j for i, j in {720: 20, 1280: 24, 1920: 28, 3840: 35}.items()
            if i >= int(cropvalue.split('crop=')[1].split(':')[0])]
        return cropvalue, l[0] if len(l) > 0 else None

def trailer_download(link, item):
    cache_path = f'cache/{item["title"]}/'
    def dl_progress(d): 
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
    try:
        links = list(d["yt_link"] for d in link if "yt_link" in d)
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
    except:
        log(RED, "YT_DLP", "Something went wrong, Searching for something else...")
        ydl.download([f"ytsearch5:{item['title']} ({item['year']}) {config['yt_search_keywords']}"])
        
    if os.path.exists(cache_path):
        files = os.listdir(cache_path)
        if config['remove_black_borders']:
            remove_black_borders(files)
        else:
            post_process(cache_path, files, item['path'] )
    else:
        log(RED, 'YT_DLP', f'No cache folder for {cache_path}')
        
        