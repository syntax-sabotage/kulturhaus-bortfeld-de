#!/usr/bin/expect -f

spawn ssh khaus@193.30.120.108
expect "password:"
send "[REMOVED-USE-SSH-KEY]\r"
expect "$ "
send "echo '[REMOVED-USE-SSH-KEY]' | sudo -S systemctl restart odoo18\r"
expect "$ "
send "echo 'Odoo service restarted'\r"
expect "$ "
send "exit\r"
expect eof