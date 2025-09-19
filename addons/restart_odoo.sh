#!/usr/bin/expect -f

spawn ssh khaus@193.30.120.108 "sudo systemctl restart odoo18"
expect "password:"
send "[REMOVED-USE-SSH-KEY]\r"
expect "password"
send "[REMOVED-USE-SSH-KEY]\r"
expect eof