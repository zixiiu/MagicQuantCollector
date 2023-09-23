### some note for build docker.
#### build image
```commandline
docker build --tag faznky/mqcollector .
# or on ARM MAC
docker buildx build --platform=linux/amd64 --tag faznky/mqcollector .
```
and then use docker desktop push.

#### deploy on synology
Do not use the GUI to launch.   
need to add `--net="host"` as an option in order to access mysql from other container.

#### update on synology
Run watchtower.

#### Mysql on synology
https://blog.csdn.net/lzyy1992/article/details/86256019  

#### SnowBall API Wrapper
https://github.com/uname-yang/pysnowball
