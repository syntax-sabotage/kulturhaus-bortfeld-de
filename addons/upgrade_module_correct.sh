#!/usr/bin/expect -f

spawn ssh khaus@193.30.120.108
expect "password:"
send "[REMOVED-USE-SSH-KEY]\r"
expect "$ "
send "cd /opt/odoo18/odoo\r"
expect "$ "
send "sudo -u odoo18 /opt/odoo18/venv/bin/python /opt/odoo18/odoo/odoo-bin -c /etc/odoo18.conf -u kulturhaus_board_resolutions --stop-after-init\r"
expect "password"
send "[REMOVED-USE-SSH-KEY]\r"
expect eof