#!/bin/bash

# Deploy board resolutions module to server
echo "Deploying kulturhaus_board_resolutions module..."

# Create tar archive
tar -czf kulturhaus_board_resolutions.tar.gz kulturhaus_board_resolutions/

# Upload using expect script for password
expect << 'EOF'
spawn scp kulturhaus_board_resolutions.tar.gz khaus@193.30.120.108:/tmp/
expect "password:"
send "Basf1\$Khaus\r"
expect eof
EOF

# Connect and extract
expect << 'EOF'
spawn ssh khaus@193.30.120.108
expect "password:"
send "Basf1\$Khaus\r"
expect "$ "
send "sudo rm -rf /opt/odoo18/odoo/addons/kulturhaus_board_resolutions\r"
expect "password"
send "Basf1\$Khaus\r"
expect "$ "
send "sudo tar -xzf /tmp/kulturhaus_board_resolutions.tar.gz -C /opt/odoo18/odoo/addons/\r"
expect "$ "
send "sudo chown -R odoo18:odoo18 /opt/odoo18/odoo/addons/kulturhaus_board_resolutions\r"
expect "$ "
send "sudo systemctl restart odoo18\r"
expect "$ "
send "exit\r"
expect eof
EOF

echo "Module deployed and Odoo restarted!"
rm kulturhaus_board_resolutions.tar.gz