# GitHub Issues for SEPA Module Development

## Issue #1: Implement Automatic SEPA Batch Generation
**Title:** [SEPA] Add automatic batch generation via cron job
**Labels:** enhancement, sepa-module, priority-high
**Milestone:** Q1 2025

### Description
Implement scheduled automatic generation of SEPA batches for membership fees.

### Requirements
- [ ] Create cron job for monthly batch generation
- [ ] Run on 15th of each month for January fees
- [ ] Run on 15th of June for July fees  
- [ ] Configurable days before due date
- [ ] Skip weekends and holidays
- [ ] Email notification to treasurer

### Technical Details
- Use `ir.cron` for scheduling
- Check for existing batch before creating
- Log all automatic generations
- Handle errors gracefully

---

## Issue #2: Add Email Notifications for Members
**Title:** [SEPA] Email notifications for payment collections
**Labels:** enhancement, sepa-module, communication
**Milestone:** Q1 2025

### Description
Send automatic emails to members about upcoming SEPA collections.

### Requirements
- [ ] Pre-collection notice (7 days before)
- [ ] Collection confirmation
- [ ] Failed collection notice
- [ ] Email templates in German
- [ ] Opt-out option for notifications
- [ ] Batch sending to avoid spam filters

### Templates Needed
1. Pre-collection notice
2. Successful collection
3. Failed collection
4. Mandate expiry warning

---

## Issue #3: SEPA XML Schema Validation
**Title:** [SEPA] Validate XML against pain.008.001.02 XSD
**Labels:** enhancement, sepa-module, validation
**Milestone:** Q1 2025

### Description
Add XML schema validation before bank upload to prevent rejections.

### Requirements
- [ ] Download official XSD schema
- [ ] Validate on XML generation
- [ ] Show validation errors clearly
- [ ] Block invalid XML export
- [ ] Log validation results

### Resources
- ISO 20022 pain.008.001.02 schema
- Python lxml validation

---

## Issue #4: Payment Reconciliation Module
**Title:** [SEPA] Import and reconcile bank statements
**Labels:** enhancement, sepa-module, accounting
**Milestone:** Q2 2025

### Description
Automatic reconciliation of SEPA collections with bank statements.

### Requirements
- [ ] Import MT940/CAMT formats
- [ ] Match by mandate reference
- [ ] Handle partial payments
- [ ] Flag failed collections
- [ ] Create journal entries
- [ ] Reconciliation report

---

## Issue #5: Mandate Renewal Management
**Title:** [SEPA] Automated mandate renewal reminders
**Labels:** enhancement, sepa-module, compliance
**Milestone:** Q1 2025

### Description
Track mandate validity and send renewal reminders.

### Requirements
- [ ] 36-month validity tracking
- [ ] Reminder 60 days before expiry
- [ ] Renewal workflow
- [ ] Document management
- [ ] Compliance reporting

---

## Issue #6: BIC Auto-Lookup
**Title:** [SEPA] Automatic BIC lookup from IBAN
**Labels:** enhancement, sepa-module, ux
**Milestone:** Q1 2025

### Description
Automatically determine BIC from IBAN to reduce data entry.

### Requirements
- [ ] German IBAN → BIC database
- [ ] API integration fallback
- [ ] Cache lookup results
- [ ] Manual override option
- [ ] Validation on save

### Resources
- Bundesbank BIC directory
- IBAN validation library

---

## Issue #7: Mobile App Integration
**Title:** [SEPA] Member portal for mandate management
**Labels:** enhancement, sepa-module, mobile
**Milestone:** Q2 2025

### Description
Allow members to manage SEPA mandates via mobile/web portal.

### Requirements
- [ ] View mandate status
- [ ] Update bank details
- [ ] Download mandate form
- [ ] Payment history
- [ ] Notification preferences
- [ ] Two-factor authentication

---

## Issue #8: Advanced Reporting Dashboard
**Title:** [SEPA] Analytics dashboard for membership payments
**Labels:** enhancement, sepa-module, reporting
**Milestone:** Q2 2025

### Description
Comprehensive dashboard for membership payment analytics.

### Requirements
- [ ] Collection success rate
- [ ] Monthly/yearly trends
- [ ] Member retention metrics
- [ ] Failed payment analysis
- [ ] Forecast projections
- [ ] Export to Excel/PDF

### KPIs
- Collection rate
- Average payment delay
- Mandate churn rate
- Revenue forecast

---

## Issue #9: GDPR Compliance Tools
**Title:** [SEPA] GDPR data protection features
**Labels:** enhancement, sepa-module, compliance, security
**Milestone:** Q1 2025

### Description
Ensure full GDPR compliance for payment data handling.

### Requirements
- [ ] Data retention policies
- [ ] Right to deletion
- [ ] Data export for members
- [ ] Consent tracking
- [ ] Audit logging
- [ ] Encryption at rest

---

## Issue #10: Failed Payment Retry Logic
**Title:** [SEPA] Automatic retry for failed collections
**Labels:** enhancement, sepa-module, automation
**Milestone:** Q2 2025

### Description
Implement smart retry logic for failed SEPA collections.

### Requirements
- [ ] Configurable retry intervals
- [ ] Maximum retry attempts
- [ ] Different strategies per error code
- [ ] Notification on final failure
- [ ] Manual retry option
- [ ] Reporting on retry success

### Error Codes to Handle
- Insufficient funds
- Account closed
- Mandate cancelled
- Technical errors

---

## Creating Issues via GitHub CLI

```bash
# Install GitHub CLI if needed
brew install gh

# Authenticate
gh auth login

# Create issues
gh issue create --title "[SEPA] Add automatic batch generation via cron job" \
  --body "$(cat issue-1-body.md)" \
  --label "enhancement,sepa-module,priority-high" \
  --milestone "Q1 2025" \
  --repo syntax-sabotage/kulturhaus-bortfeld-de

# List all SEPA issues
gh issue list --label sepa-module --repo syntax-sabotage/kulturhaus-bortfeld-de
```

## Priority Order
1. 🔴 Automatic batch generation (Issue #1)
2. 🔴 Email notifications (Issue #2)
3. 🟡 XML validation (Issue #3)
4. 🟡 Mandate renewal (Issue #5)
5. 🟡 GDPR compliance (Issue #9)
6. 🟢 BIC auto-lookup (Issue #6)
7. 🟢 Payment reconciliation (Issue #4)
8. 🟢 Failed payment retry (Issue #10)
9. 🔵 Reporting dashboard (Issue #8)
10. 🔵 Mobile integration (Issue #7)

---
*Generated: 2025-01-14*