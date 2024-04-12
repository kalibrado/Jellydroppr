""" _summary_ """

import os
from pathlib import Path
import subprocess
from time import sleep
import requests
import yaml
import yt_dlp

GB = 1024 * 1024 * 1024
BASE_URL = "https://api.themoviedb.org"
color = {
    "RESET": "\033[0m",
    "RED": "\033[31m",
    "GREEN": "\033[32m",
    "BLUE": "\033[34m",
    "WHITE": "\033[37m",
}

with open("config/config.yaml", "r", encoding="utf-8") as f:
    config = yaml.load(f, Loader=yaml.Loader)


def log(cl, prefix, msg):
    print(color[cl] + f"[{prefix}] - {msg} " + color["RESET"] + "\n")
    sleep(1)


def trailer_pull(tmdb_id, item_type, parent_mode=False):
    log("WHITE", "GET", f"Getting information about {tmdb_id} {item_type}")
    url = f"{BASE_URL}/3/{item_type}/{tmdb_id}/videos?api_key={config['tmdb_api']}&language=fr-FR&include_video_language=fr"
    if parent_mode:
        url = f"{BASE_URL}/3/find/{tmdb_id}?api_key={config['tmdb_api']}&external_source=imdb_id"
    try:
        headers = {"accept": "application/json"}
        raw_trailers = requests.get(url, headers=headers, timeout=30000).json()
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
    except requests.HTTPError:
        return []


def post_process(cache_path, files, item_path):
    log("WHITE", "POST PROCESS", f"Create {item_path}/{config['output_dirs']}")
    os.makedirs(f'{item_path}/{config["output_dirs"]}', exist_ok=True)
    for file in files:
        filename = Path(file).stem
        cmd = f"""
            ffmpeg -i "{cache_path}/{file}" \
            -threads {config["thread_count"]} \
            -c:v copy -c:a aac -af "volume=-7dB" \
            -bufsize {config["buffer_size_ffmpeg"]} \
            -preset slow -y \
            "{item_path}/{config["output_dirs"]}/{filename}.{config["filetype"]}"
        """
        log("WHITE", "FFMPEG", cmd)
        with subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
        ) as ffmpeg:
            ffmpeg.wait()


def trailer_download(link, item, db):
    cache_path = f'cache/{item["title"]}'
    title = item["title"]
    retry = item["retry"]
    reason = item["reason"]

    def dl_progress(d):
        print()
        if d["status"] == "finished":
            log("GREEN", "DOWNLOAD", "Trailer downloaded.")
        if d["status"] == "error":
            log("RED", "DOWNLOAD", "Trailer download fail.")

    def check_duration(info, *, _):
        duration = info.get("duration")
        if duration not in range(
            int(config["length_range"].split(",")[0]),
            int(config["length_range"].split(",")[1]),
        ):
            reason = f"Video too long/short for: '{title} ({item['year']})'"
            log("RED", "DOWNLOAD", reason)
            item["retry"] = retry + 1
            item["reason"] = reason
            db.update("failed", item["id"], item)
            raise reason

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
        ytdl_opts.update({"match_filter": check_duration})
    ydl = yt_dlp.YoutubeDL(ytdl_opts)
    links = list(d["yt_link"] for d in link if "yt_link" in d)
    if len(links) > 0:
        for link in links:
            if config["only_one_trailler"]:
                if os.path.exists(cache_path) and len(os.listdir(cache_path)):
                    continue
                try:
                    log(
                        "WHITE",
                        "DOWNLOAD",
                        f"Importing {item['title']} trailers...",
                    )
                    ydl.download(link)
                except ModuleNotFoundError:
                    continue
            else:
                log("WHITE", "DOWNLOAD", "Importing all trailers...")
                ydl.download(link)
    else:
        log(
            "WHITE",
            "DOWNLOAD",
            f"No avalide links try manual search with: \
            ytsearch5:{item['title']} ({item['year']}) \
            {config['yt_search_keywords']}",
        )
        try:
            ydl.download(
                [
                    f"ytsearch5:{item['title']} ({item['year']}) \
                    {config['yt_search_keywords']}"
                ]
            )
        except ModuleNotFoundError:
            reason = f"No trailler found for: '{title} ({item['year']})'"
            log("RED", "DOWNLOAD", reason)
            item["retry"] = retry + 1
            item["reason"] = reason
            db.update("failed", item["id"], item)

    if os.path.exists(cache_path):
        files = os.listdir(cache_path)
        post_process(cache_path, files, item["path"])
    else:
        reason = f"No cache folder for {title}"
        log("RED", "DOWNLOAD", reason)
        item["retry"] = retry + 1
        item["reason"] = reason
        db.update("failed", item["id"], item)
