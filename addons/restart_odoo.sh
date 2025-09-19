#!/usr/bin/expect -f

spawn ssh khaus@193.30.120.108 "sudo systemctl restart odoo18"
expect "password:"
send "Basf1\$Khaus\r"
expect "password"
send "Basf1\$Khaus\r"
expect eof