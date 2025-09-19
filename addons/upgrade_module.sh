#!/usr/bin/expect -f

spawn ssh khaus@193.30.120.108
expect "password:"
send "[REMOVED-USE-SSH-KEY]\r"
expect "$ "
send "cd /opt/odoo18\r"
expect "$ "
send "sudo -u odoo18 ./venv/bin/python odoo-bin -c /etc/odoo18.conf -u kulturhaus_board_resolutions --stop-after-init\r"
expect "password"
send "[REMOVED-USE-SSH-KEY]\r"
expect eof