run:
	systemctl start Watcher.service
	systemctl start Runner.service

stop:
	systemctl stop Watcher.service
	systemctl stop Runner.service

status:
	systemctl status Watcher.service
	systemctl status Runner.service

restart:
	systemctl restart Watcher.service
	systemctl restart Runner.service