""" _summary_ """

import os
import sys
import shutil
from time import sleep
from pyarr import RadarrAPI, SonarrAPI
from src.utils import log, config, trailer_download, trailer_pull, GB
from src.finder_db import FinderDB


def movie_finder():
    log("WHITE", "RADARR", "Movie trailer finder started.")
    radarr = RadarrAPI(config["radarr_host"], config["radarr_api"])
    movies = radarr.get_movie()
    for movie in movies:
        db = FinderDB("radarr")
        num = movies.index(movie) + 1
        title = movie["title"]
        year = movie["year"]
        path = movie["path"]
        sort_title = movie["sortTitle"]
        if "tmdbId" not in movie:
            log("RED", "RADARR", "This movies {title} does not have tmdbId")
            continue
        tmdb_id = movie["tmdbId"]
        movie["id"] = tmdb_id
        movie["retry"] = 0
        movie["reason"] = ""
        if (
            tmdb_id in db.get("failed").keys()
            and db.get("failed")[tmdb_id]["retry"] == config["max_retry"]
            or tmdb_id in db.get("success").keys()
        ):
            continue
        if not os.path.exists(path):
            continue
        path_file = os.path.join(
            path, config["output_dirs"], f"{sort_title}.{config['filetype']}"
        )
        if os.path.exists(path_file):
            db.update("success", tmdb_id, path_file)
            continue
        disk = shutil.disk_usage(path).free
        if disk == 0:
            reason = f"Adding trailers in {path} is not possible due \
            to insufficient disk space free {round(disk / GB, 2)}G."
            log("RED", "DISK", reason)
            movie["retry"] = config["max_retry"]
            movie["reason"] = reason
            db.update("failed", tmdb_id, movie)
            continue
        log(
            "WHITE",
            "RADARR",
            f"[{num}] - Title: '{title}' \
            - Year: '{year}' \
            - Path: '{path}' \
            - TMDB-ID: '{tmdb_id}' ",
        )
        link = trailer_pull(tmdb_id, "movie")
        trailer_download(link, movie, db)


def show_finder():
    log("WHITE", "SONARR", "Show trailer finder started.")
    sonarr = SonarrAPI(config["sonarr_host"], config["sonarr_api"])
    shows = sonarr.get_series()
    for show in shows:
        db = FinderDB("sonarr")
        num = shows.index(show) + 1
        title = show["title"]
        year = show["year"]
        path = show["path"]
        sort_title = show["sortTitle"]
        if "imdbId" not in show:
            log("RED", "SONARR", f"This series {title} does not have imdbId")
            continue
        imdb_id = show["imdbId"]
        show["id"] = imdb_id
        show["retry"] = 0
        show["reason"] = ""
        if (
            imdb_id in db.get("failed").keys()
            and db.get("failed")[imdb_id]["retry"] == config["max_retry"]
            or imdb_id in db.get("success").keys()
        ):
            continue
        if not os.path.exists(path):
            continue
        path_file = os.path.join(
            path, config["output_dirs"], f"{sort_title}.{config['filetype']}"
        )
        if os.path.exists(path_file):
            db.update("success", imdb_id, path_file)
            continue
        disk = shutil.disk_usage(path).free
        if disk == 0:
            reason = f"Adding trailers in {path} is not possible due \
            to insufficient disk space free {round(disk / GB, 2)}G."
            log("RED", "DISK", reason)
            show["retry"] = config["max_retry"]
            show["reason"] = reason
            db.update("failed", imdb_id, show)
            continue
        log(
            "WHITE",
            "SONARR",
            f"[{num}] - Title: '{title}' \
            - Year: '{year}' \
            - Path: '{path}' \
            - IMDB-ID: '{imdb_id}' ",
        )
        links_episode = trailer_pull(imdb_id, "tv", parent_mode=True)
        for link_episode in links_episode:
            link_episode_trailler = trailer_pull(link_episode["id"], "tv")
            if len(link_episode_trailler) > 0:
                trailer_download(link_episode_trailler, show, db)
            else:
                continue
        log("RED", "SONARR", f"No trailer is available for: {title}.")


def finder():
    """_summary_"""
    os.makedirs("cache", exist_ok=True)
    log("GREEN", "CREATE", "Created cache directory.")
    FinderDB().prepare()
    while True:
        log("WHITE", "CACHE", "Clean cache")
        shutil.rmtree("cache/", ignore_errors=True)
        if all(x in config for x in ["radarr_host", "radarr_api"]):
            movie_finder()
        if all(x in config for x in ["sonarr_host", "sonarr_api"]):
            show_finder()
        if "sleep_time" in config:
            to = config["sleep_time"]
            log(
                "WHITE",
                "WAIT",
                f"Operation complete. Waiting {to} hour(s).",
            )
            sleep(to * 3600)
        else:
            log(
                "WHITE",
                "FINISH",
                "Operation complete. No sleep time was set, stopping.",
            )
            sys.exit()


if __name__ == "__main__":
    finder()
