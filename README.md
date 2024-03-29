# Jellydroppr

### docker-compose.yml
```yml
version: "3"
services:
  Jellydroppr:
    image: ldfe/jellydroppr:latest
    restart: always
    volumes:
      - ./config:/config # Where the config file will be located
      # the access path must correspond to those of radarr and sonarr
      - /mnt/Media1:/mnt/Media1 # media folder 1
      - /mnt/Media2:/mnt/Media1 # media folder 1
```
