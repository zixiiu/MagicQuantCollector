### some note for build docker.
#### build image
```commandline
docker build --tag faznky/mqcollector .
```
and then use docker desktop push.

#### deploy on synology
Do not use the GUI to launch.   
need to add `--net="host"` as an option in order to access mysql from other container.

#### update on synology
Run watchtower.