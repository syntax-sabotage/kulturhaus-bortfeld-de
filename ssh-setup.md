# SSH Authentication Setup

## Current Status
⚠️ SSH connection works locally but blocked from remote (firewall/network issue)
✅ Credentials verified: user khaus, password khaus works locally

## Generated SSH Key
✅ SSH key pair generated successfully:
- **Private key**: `~/.ssh/kulturhaus_bortfeld`
- **Public key**: `~/.ssh/kulturhaus_bortfeld.pub`
- **Key type**: ed25519
- **Comment**: kulturhaus-bortfeld-ev-server

## Public Key Content
```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIDwTl6QPVgFNgHkrzk9aRRHC27vMvBMR6MWPRblmoxmV kulturhaus-bortfeld-ev-server
```

## Next Steps Required
1. **Verify server credentials** - Current user/password combination is not working
2. **Alternative access methods**:
   - Check if different username is required (root, ubuntu, admin, etc.)
   - Verify if server is accessible via console/panel
   - Contact hosting provider for correct credentials

## Manual SSH Key Installation
Once correct access is established, run on the server:
```bash
# Create SSH directory
mkdir -p ~/.ssh
chmod 700 ~/.ssh

# Add public key to authorized_keys
echo "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIDwTl6QPVgFNgHkrzk9aRRHC27vMvBMR6MWPRblmoxmV kulturhaus-bortfeld-ev-server" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

## Local SSH Configuration
Add to `~/.ssh/config`:
```
Host kulturhaus
    HostName v2202411240735294743.luckysrv.de
    User khaus
    IdentityFile ~/.ssh/kulturhaus_bortfeld
    IdentitiesOnly yes
```

## Security Hardening (After SSH keys work)
1. Disable password authentication
2. Change default SSH port (optional)
3. Configure fail2ban
4. Set up firewall rules