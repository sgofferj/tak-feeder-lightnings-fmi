
[![Build and publish the container image](https://github.com/sgofferj/tak-feeder-lightnings-fmi/actions/workflows/actions.yml/badge.svg)](https://github.com/sgofferj/tak-feeder-lightnings-fmi/actions/workflows/actions.yml)

# tak-feeder-lightnings-fmi
Get latest lightning observation data from the Finnish Meteorological Institute and feed them to a TAK server

(C) 2025 Stefan Gofferje

Licensed under the GNU General Public License V3 or later.

## Description
The Finnish Meteorological Institute provides free API access to the weather data from their sensor network. This container connects to their WFS server,
downloads the sensor data and sends it to a TAK server. Note that the lightning data is not realtime but about 2 minutes delayed.

The lightning strikes are displayed as thunderstorm icons with colors depending on the age of the strike:

| Age | Color |
|-----|-------|
| <5min | white |
| >=5min | yellow |
| >=15min | orange |
| >=30min | red    |
| >=45min | dark red | 

The stale time is set to 2x UPDATE_INTERVAL (see below)

## Configuration
The following values are supported and can be provided either as environment variables or through an .env-file.

| Variable | Default | Purpose |
|----------|---------|---------|
| COT_URL | empty | (mandatory) TAK server full URL, e.g. ssl://takserver:8089 |
| HISTORY | 300 | (optional) Wanted lightning history in seconds. Values less than 120 seconds don't get any results. |
| UPDATE_INTERVAL | 30 | (optional) Interval between data updates - how often should we get data? |
| PYTAK_TLS_CLIENT_CERT | empty | (mandatory for ssl) User certificate in PEM format |
| PYTAK_TLS_CLIENT_KEY | empty | (mandatory for ssl) User certificate key file (xxx.key) |
| PYTAK_TLS_DONT_VERIFY | 1 | (optional) Verify the server certificate (0) or not (1) |
| TAK_PROTO | 0 | (optional) Choose the protocol (see [PyTAK docs](https://pytak.readthedocs.io/en/stable/configuration/)) |

## Certificates
These are the server-issued certificate and key files. Before using, the password needs to be removed from the key file with `openssl rsa -in cert.key -out cert-nopw.key`. OpenSSL will ask for the key password which usually is "atakatak".

## Container use
First, get your certificate and key and copy them to a suitable folder which needs to be added as a volume to the container.

### Image
The image is built for AMD64 and ARM64 and pushed to ghcr.io: *ghcr.io/sgofferj/tak-feeder-lightnings-fmi:latest*

### Docker compose
Here is an example for a docker-compose.yml file:
```
version: '2.0'

services:
  weather-fmi:
    image: ghcr.io/sgofferj/tak-feeder-lightnings-fmi:latest
    restart: always
    networks:
      - default
    volumes:
      - <path to data-directory>:/data:ro
    environment:
      - COT_URL=ssl://tak-server:8089
      - PYTAK_TLS_CLIENT_CERT=/data/cert.pem
      - PYTAK_TLS_CLIENT_KEY=/data/key.pem
      - PYTAK_TLS_DONT_VERIFY=1
      - TAK_PROTO=0

networks:
  default:
