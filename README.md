# Kulturhaus-bortfeld.de

## Project Overview
- **Customer**: Kulturhaus Bortfeld e.V.
- **Type**: Odoo Instance (Self-hosted on VPS)
- **Domain**: kulturhaus-bortfeld.de
- **Server**: v2202411240735294743.luckysrv.de (193.30.120.108)
- **Hosting**: VPS Server (not Odoo.sh)
- **Status**: New Project

## Description
Self-hosted Odoo ERP system for Kulturhaus Bortfeld e.V. - a cultural center managing events, memberships, and operations. Deployed on a dedicated VPS server for full control and customization.

## Hosting Architecture
- **Deployment**: Self-hosted on VPS
- **Environment**: Production server with full admin access
- **Benefits**: Complete customization freedom, cost control, data sovereignty

## Project Structure
```
kulturhaus-bortfeld-de/
├── README.md           # This file
├── docker-compose.yml  # Odoo deployment configuration
├── requirements.txt    # Python dependencies
├── modules/           # Custom Odoo modules
├── config/            # Odoo configuration files
├── nginx/             # Reverse proxy configuration
├── ssl/               # SSL certificates
└── backups/           # Database and filestore backups
```

## Next Steps
1. Define requirements and scope
2. Set up VPS server infrastructure
3. Configure Docker deployment
4. Install and configure Odoo
5. Set up SSL certificates
6. Configure backup strategy
7. Deploy custom modules and settings