# Kulturhaus Membership SEPA Module

## 📋 Overview
SEPA-Lastschriftverfahren für Mitgliedsbeiträge des Kulturhaus Bortfeld e.V.

## ✅ Current Status

### Implemented Features
- ✅ SEPA mandate management for members
- ✅ Configurable membership periods (full year/half year)  
- ✅ Manual batch generation with buttons
- ✅ SEPA XML export for bank processing
- ✅ Demo data with 50 test members
- ✅ Mandate ID generation (KH-SEPA-YYYYMM-XXX)
- ✅ IBAN/BIC validation
- ✅ Batch history tracking

### 🚧 In Development
- ⏳ Automatic batch generation (scheduled)
- ⏳ Email notifications for members
- ⏳ Payment reconciliation
- ⏳ Mandate renewal reminders
- ⏳ SEPA XML validation against XSD schema

## 📊 Data Model

### Extended Fields on res.partner
- `sepa_mandate_id` - Unique mandate reference
- `sepa_mandate_date` - Date mandate was signed
- `sepa_mandate_active` - Is mandate currently valid
- `sepa_iban` - Member's IBAN
- `sepa_bic` - Member's BIC code
- `membership_type` - Selection: full_year (50€) / half_year (25€)
- `last_payment_date` - Last successful SEPA collection

### SEPA Batch Model (kulturhaus.sepa.batch)
- `name` - Batch reference (e.g., SEPA-2024-01)
- `creation_date` - When batch was created
- `due_date` - Collection date
- `total_amount` - Sum of all transactions
- `member_count` - Number of members in batch
- `xml_file` - Generated SEPA XML
- `state` - draft/confirmed/sent/processed

## 🔧 Installation

1. Copy module to addons folder:
```bash
cp -r kulturhaus_membership_sepa /mnt/extra-addons/
```

2. Update Apps List in Odoo:
- Settings → Apps → Update Apps List

3. Install Module:
- Search for "Kulturhaus Membership SEPA"
- Click Install

## 📝 Usage

### Creating SEPA Mandates
1. Go to Contacts → Select Member
2. Open "SEPA" tab
3. Enter:
   - IBAN & BIC
   - Mandate signature date
   - Membership type (full/half year)
4. Save

### Generating SEPA Batch
1. Go to Membership → SEPA Batches
2. Click "Create New Batch"
3. Select:
   - Collection date
   - Membership period (January/July)
   - Member filter (optional)
4. Review member list
5. Click "Generate XML"
6. Download XML file for bank upload

### Demo Data
The module includes 50 demo members with realistic German data:
- Names, addresses, phone numbers
- Valid SEPA mandates
- Mix of full-year and half-year memberships
- Various German banks (Sparkasse, Volksbank, etc.)

To load demo data:
```bash
python3 scripts/upgrade_with_demo.py
```

## 🏦 Bank Integration

### Supported Banks
- Sparkasse Gifhorn-Wolfsburg
- Volksbank BraWo
- All SEPA-compliant German banks

### XML Format
- SEPA Core Direct Debit (pain.008.001.02)
- ISO 20022 compliant
- UTF-8 encoding
- Batch booking supported

## 🔐 Security

### Access Rights
- `membership.group_membership_manager` - Full access
- `base.group_user` - Read access to own records
- `base.group_system` - System administration

### Data Protection
- IBAN/BIC encrypted in database
- Audit trail for all mandate changes
- GDPR compliant data handling

## 🧪 Testing

### Manual Testing
1. Create test member with SEPA data
2. Generate test batch
3. Validate XML output
4. Check batch history

### Automated Tests
```bash
docker exec kulturhaus-odoo python3 -m pytest \
  /mnt/extra-addons/kulturhaus_membership_sepa/tests/
```

## 📈 Reporting

### Available Reports
- Monthly collection summary
- Failed mandate list
- Member payment history
- Annual membership overview

## 🐛 Known Issues
- Mandate validation requires manual confirmation
- BIC lookup not yet automated
- No automatic retry for failed collections

## 🚀 Roadmap

### Q1 2025
- [ ] Automatic batch generation via cron
- [ ] Email notifications
- [ ] Payment import & reconciliation

### Q2 2025
- [ ] Mobile app integration
- [ ] Member portal self-service
- [ ] Advanced reporting dashboard

## 📞 Support
- **Technical**: IT Team (it@kulturhaus-bortfeld.de)
- **Business**: Membership Team
- **Emergency**: +49 160 606654 (Lars)

## 📄 License
LGPL-3.0

## 🤝 Contributing
1. Create feature branch from `develop`
2. Test thoroughly in Docker environment
3. Create PR with description
4. Wait for review & approval

---
*Last Updated: 2025-01-14*