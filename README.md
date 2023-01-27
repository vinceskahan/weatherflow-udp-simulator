# DEPRECATED REPO

This repo is read-only as of 2023-0127 - please see my https://github.com/vinceskahan/wfudptools repo - this repo is left read/only so folks can find any old PR that might still work with the refactored combined listener/simulator tools.

## WeatherFlow UDP Simulator

This script will broadcast UDP ala the WeatherFlow Hub, with some parameters changing over time.

### Background

Although I sold/gifted my WeatherFlow stations in mid-2020, sending them to new homes, I still have a need to support my UDP Listener app which multiple people use, so I thought I'd write a quick minimal simulator of what the Hub emits.

### Usage

```
nohup python3 wfsim.py >/dev/null 2>&1 & 
```

### Current Capabilities

See the code itself for details.  I'll try to put comments at the top of the file.
