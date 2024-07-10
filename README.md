# Jellydroppr

[![Open in Coder](https://leodevops.duckdns.org/open-in-coder.svg)](https://leodevops.duckdns.org/templates/vscode/workspace?param.git_repo=https://github.com/kalibrado/Jellydroppr.git&name=Jellydroppr)

## docker-compose.yml

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



[!["Buy Me A Beer"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/leonardofod)
