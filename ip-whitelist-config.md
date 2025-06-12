# IP Whitelisting Configuration

## Current IP Addresses to Whitelist
- **IPv4**: `94.31.75.76`
- **IPv6**: `2a00:6020:4921:8a00:cc66:d0dd:cfd5:c8ef`

## Method 1: Fail2Ban Whitelist (Recommended)

### Create fail2ban whitelist file
```bash
# On the server, create/edit fail2ban ignoreip configuration
sudo nano /etc/fail2ban/jail.local
```

### Configuration content:
```ini
[DEFAULT]
# Whitelist trusted IPs (space or comma separated)
ignoreip = 127.0.0.1/8 ::1 94.31.75.76 2a00:6020:4921:8a00:cc66:d0dd:cfd5:c8ef

# SSH jail configuration
[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log
maxretry = 5
bantime = 3600
findtime = 600
ignoreip = 127.0.0.1/8 ::1 94.31.75.76 2a00:6020:4921:8a00:cc66:d0dd:cfd5:c8ef
```

### Apply configuration:
```bash
sudo systemctl restart fail2ban
sudo fail2ban-client status sshd
```

## Method 2: UFW Firewall Rules

### Allow specific IP for SSH:
```bash
# Allow your IP for SSH
sudo ufw allow from 94.31.75.76 to any port 22
sudo ufw allow from 2a00:6020:4921:8a00:cc66:d0dd:cfd5:c8ef to any port 22

# Check rules
sudo ufw status numbered
```

## Method 3: iptables Direct Rules

### Add whitelist rules:
```bash
# Allow your IPv4
sudo iptables -I INPUT -s 94.31.75.76 -p tcp --dport 22 -j ACCEPT

# Allow your IPv6
sudo ip6tables -I INPUT -s 2a00:6020:4921:8a00:cc66:d0dd:cfd5:c8ef -p tcp --dport 22 -j ACCEPT

# Save rules (Ubuntu/Debian)
sudo iptables-save > /etc/iptables/rules.v4
sudo ip6tables-save > /etc/iptables/rules.v6
```

## Method 4: SSH Configuration (Additional Security)

### Limit SSH access by IP in sshd_config:
```bash
sudo nano /etc/ssh/sshd_config
```

### Add these lines:
```
# Allow only specific IPs
AllowUsers khaus@94.31.75.76
AllowUsers khaus@2a00:6020:4921:8a00:cc66:d0dd:cfd5:c8ef

# Alternative: Use Match blocks
Match Address 94.31.75.76,2a00:6020:4921:8a00:cc66:d0dd:cfd5:c8ef
    AllowUsers khaus
```

### Restart SSH service:
```bash
sudo systemctl restart sshd
```

## Verification Commands

### Check if your IP is whitelisted:
```bash
# Check fail2ban status
sudo fail2ban-client status sshd

# Check if your IP is banned
sudo fail2ban-client get sshd banip

# Unban your IP if needed
sudo fail2ban-client set sshd unbanip 94.31.75.76

# Check firewall rules
sudo ufw status
sudo iptables -L INPUT -n --line-numbers
```

## Troubleshooting

### If still getting banned:
1. **Check fail2ban logs**:
   ```bash
   sudo tail -f /var/log/fail2ban.log
   ```

2. **Check SSH logs**:
   ```bash
   sudo tail -f /var/log/auth.log
   ```

3. **Manually unban your IP**:
   ```bash
   sudo fail2ban-client set sshd unbanip 94.31.75.76
   ```

## Dynamic IP Considerations

If your IP changes frequently:
1. **Use IP ranges** instead of specific IPs
2. **Set up dynamic DNS** updates
3. **Use VPN** with static IP
4. **Consider key-based authentication** instead of passwords

## Commands to Run on Server

Once you have SSH access, run these commands in order:

```bash
# 1. Create fail2ban configuration
sudo tee /etc/fail2ban/jail.local << 'EOF'
[DEFAULT]
ignoreip = 127.0.0.1/8 ::1 94.31.75.76 2a00:6020:4921:8a00:cc66:d0dd:cfd5:c8ef

[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log
maxretry = 5
bantime = 3600
findtime = 600
ignoreip = 127.0.0.1/8 ::1 94.31.75.76 2a00:6020:4921:8a00:cc66:d0dd:cfd5:c8ef
EOF

# 2. Restart fail2ban
sudo systemctl restart fail2ban

# 3. Verify configuration
sudo fail2ban-client status sshd

# 4. Check current bans and unban if needed
sudo fail2ban-client get sshd banip
sudo fail2ban-client set sshd unbanip 94.31.75.76

# 5. Test SSH connection
echo "SSH whitelisting configured successfully"
```