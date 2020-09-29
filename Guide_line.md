# Gudie Line

/lib/systemd/system/MengxiaWatcher.service

```
[Unit]
Description=Mnegxia watcher
After=multi-user.target
 
[Service]
Type=idle
ExecStart=/usr/bin/python3 /home/own/work/MengXia/watcher.py > /home/own/work/loginfo/watcher.log 2>&1
 
[Install]
WantedBy=multi-user.target
```

systemctl daemon-reload  
systemctl enable MengxiaWatcher.service

reboot

systemctl status MengxiaWatcher.service

systemctl restart MengxiaWatcher.service  
systemctl stop MengxiaWatcher.service	  
systemctl start MengxiaWatcher.service  


screen -ls

screen -L -t watcher -dmS watcher
screen -r watcher
conda activate MengXia
python3 watcher.py

screen -L -t runner -dmS runner 
screen -r runner
conda activate MengXia
python3 runner.py