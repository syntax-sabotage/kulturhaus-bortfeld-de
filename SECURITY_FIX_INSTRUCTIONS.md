# CRITICAL SECURITY FIX - SSH Password Exposed

## Immediate Actions Required

### 1. ✅ Remove Credentials from Files (COMPLETED)
- All files have been cleaned
- Changes committed and pushed

### 2. 🔄 Clean Git History (IN PROGRESS)

Run these commands to remove the password from ALL git history:

```bash
# Clone a fresh copy of the repo
cd /tmp
git clone --mirror https://github.com/syntax-sabotage/kulturhaus-bortfeld-de.git

# Download BFG if you don't have it
brew install bfg  # or download from https://rtyley.github.io/bfg-repo-cleaner/

# Remove the password from all commits
cd kulturhaus-bortfeld-de.git
bfg --replace-text <(echo "Basf1\$Khaus=>[REMOVED]") .

# Clean the repository
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# Force push the cleaned history
git push --force
```

### 3. 🚨 Change Server Password (URGENT)

The exposed password needs to be changed immediately on the server!

```bash
# Connect to server (you'll need the current password one last time)
ssh khaus@v2202411240735294743.luckysrv.de

# Change password
passwd

# Exit
exit
```

### 4. 🔐 Set Up SSH Key Authentication

```bash
# If you don't have an SSH key, generate one
ssh-keygen -t ed25519 -f ~/.ssh/kulturhaus_bortfeld_new

# Copy the public key to the server
ssh-copy-id -i ~/.ssh/kulturhaus_bortfeld_new.pub khaus@v2202411240735294743.luckysrv.de

# Test SSH key authentication
ssh -i ~/.ssh/kulturhaus_bortfeld_new khaus@v2202411240735294743.luckysrv.de

# Update SSH config
echo "
Host kulturhaus
    HostName v2202411240735294743.luckysrv.de
    User khaus
    IdentityFile ~/.ssh/kulturhaus_bortfeld_new
    IdentitiesOnly yes
" >> ~/.ssh/config
```

### 5. 📝 Update Deployment Scripts

All deployment scripts need to be updated to use SSH key authentication instead of password.

Replace all instances of:
```bash
sshpass -p 'PASSWORD' ssh user@host
```

With:
```bash
ssh kulturhaus
```

## Prevention

1. **Never commit passwords** - Use environment variables or secure vaults
2. **Use SSH keys** - Always prefer key-based authentication
3. **Add .gitignore** - Include sensitive files in .gitignore
4. **Use git-secrets** - Install pre-commit hooks to detect secrets
5. **Regular audits** - Scan repositories for exposed credentials

## Repository Status

- Repository is currently **PUBLIC** - Consider making it private temporarily
- GitGuardian has been notified of the exposure
- All team members should re-clone the repository after history is cleaned