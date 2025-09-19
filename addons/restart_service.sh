#!/usr/bin/expect -f

spawn ssh khaus@193.30.120.108
expect "password:"
send "Basf1\$Khaus\r"
expect "$ "
send "echo 'Basf1\$Khaus' | sudo -S systemctl restart odoo18\r"
expect "$ "
send "echo 'Odoo service restarted'\r"
expect "$ "
send "exit\r"
expect eof