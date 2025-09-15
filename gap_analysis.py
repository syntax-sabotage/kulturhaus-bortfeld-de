#!/usr/bin/env python3
"""
GAP Analysis für Kulturhaus Buchhaltung/Finanzen
Scannt die Produktionsdatenbank und identifiziert fehlende Features
"""

import xmlrpc.client
from datetime import datetime, timedelta
import json

# Production Connection
url = 'https://kulturhaus-bortfeld.de'
db = 'kulturhive'
username = 'admin'
password = 'Khausb2024'

print("🔍 Starting GAP Analysis for Kulturhaus Accounting/Finance...")
print("=" * 60)

# Connect to Odoo
common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

# GAP Report Structure
gap_report = {
    'timestamp': datetime.now().isoformat(),
    'accounting_setup': {},
    'payment_methods': {},
    'bank_setup': {},
    'tax_configuration': {},
    'workflows': {},
    'missing_features': [],
    'recommendations': []
}

print("\n📊 1. CHECKING ACCOUNTING CONFIGURATION...")
print("-" * 40)

# Check Chart of Accounts
coa = models.execute_kw(db, uid, password,
    'account.account', 'search_read',
    [[]],
    {'fields': ['code', 'name', 'account_type'], 'limit': 5})

print(f"✓ Chart of Accounts: {len(coa)} accounts found")
print(f"  Sample: {coa[0]['code'] if coa else 'NO ACCOUNTS'} - {coa[0]['name'] if coa else ''}")

# Check if German COA
has_german_coa = any('SKR' in str(acc.get('code', '')) for acc in coa[:20])
gap_report['accounting_setup']['has_german_coa'] = has_german_coa
if not has_german_coa:
    gap_report['missing_features'].append("German Chart of Accounts (SKR03/04/49)")
    print("  ⚠️  No German COA detected (SKR)")

# Check Analytic Accounts (Kostenstellen)
analytic = models.execute_kw(db, uid, password,
    'account.analytic.account', 'search_read',
    [[]],
    {'fields': ['name', 'code'], 'limit': 10})

gap_report['accounting_setup']['analytic_accounts'] = len(analytic)
print(f"✓ Analytic Accounts: {len(analytic)} found")
if len(analytic) < 5:
    gap_report['missing_features'].append("Proper cost center structure")

# Check Journals
journals = models.execute_kw(db, uid, password,
    'account.journal', 'search_read',
    [[]],
    {'fields': ['name', 'type', 'code']})

journal_types = {j['type'] for j in journals}
gap_report['accounting_setup']['journal_types'] = list(journal_types)
print(f"✓ Journals: {len(journals)} configured")
print(f"  Types: {', '.join(journal_types)}")

print("\n💳 2. PAYMENT METHODS & INTEGRATION...")
print("-" * 40)

# Check Payment Acquirers
acquirers = models.execute_kw(db, uid, password,
    'payment.provider', 'search_read',
    [[]],
    {'fields': ['name', 'code', 'state']})

active_acquirers = [a for a in acquirers if a['state'] == 'enabled']
gap_report['payment_methods']['acquirers'] = [a['name'] for a in active_acquirers]
print(f"✓ Payment Providers: {', '.join([a['name'] for a in active_acquirers])}")

has_stripe = any('stripe' in a['code'].lower() for a in acquirers if a.get('code'))
if has_stripe:
    print("  ✓ Stripe integration found")
else:
    gap_report['missing_features'].append("Stripe payment reconciliation")

# Check SEPA
sepa_check = models.execute_kw(db, uid, password,
    'ir.model', 'search',
    [[['model', '=', 'account.sepa.direct.debit']]])

has_sepa = len(sepa_check) > 0
gap_report['payment_methods']['has_sepa'] = has_sepa
if has_sepa:
    print("  ✓ SEPA module detected")
else:
    gap_report['missing_features'].append("SEPA Direct Debit functionality")

print("\n🏦 3. BANK & RECONCILIATION...")
print("-" * 40)

# Check Bank Accounts
bank_accounts = models.execute_kw(db, uid, password,
    'account.journal', 'search_read',
    [[['type', '=', 'bank']]],
    {'fields': ['name', 'bank_account_id']})

gap_report['bank_setup']['bank_accounts'] = len(bank_accounts)
print(f"✓ Bank Accounts: {len(bank_accounts)} configured")

# Check for Bank Sync
statements = models.execute_kw(db, uid, password,
    'account.bank.statement', 'search_count',
    [[]])

gap_report['bank_setup']['bank_statements'] = statements
print(f"✓ Bank Statements: {statements} imported")
if statements < 10:
    gap_report['missing_features'].append("Automated bank synchronization")

# Check Reconciliation
unreconciled = models.execute_kw(db, uid, password,
    'account.move.line', 'search_count',
    [[['reconciled', '=', False], ['account_id.reconcile', '=', True]]])

gap_report['bank_setup']['unreconciled_items'] = unreconciled
print(f"  ⚠️  Unreconciled items: {unreconciled}")

print("\n📋 4. TAX CONFIGURATION...")
print("-" * 40)

# Check Tax Setup
taxes = models.execute_kw(db, uid, password,
    'account.tax', 'search_read',
    [[]],
    {'fields': ['name', 'amount', 'type_tax_use']})

tax_rates = {t['amount'] for t in taxes}
gap_report['tax_configuration']['tax_rates'] = list(tax_rates)
print(f"✓ Tax Rates: {sorted(tax_rates)}")

has_7_percent = 7.0 in tax_rates
has_19_percent = 19.0 in tax_rates
if not has_7_percent:
    gap_report['missing_features'].append("7% reduced tax rate (Kulturveranstaltungen)")
if not has_19_percent:
    gap_report['missing_features'].append("19% standard tax rate")

print("\n📈 5. REPORTING & COMPLIANCE...")
print("-" * 40)

# Check for German reports
reports = models.execute_kw(db, uid, password,
    'ir.actions.report', 'search_read',
    [[['model', 'in', ['account.move', 'res.partner']]]],
    {'fields': ['name'], 'limit': 10})

has_donation_cert = any('spende' in r['name'].lower() or 'donation' in r['name'].lower() 
                        for r in reports)
if not has_donation_cert:
    gap_report['missing_features'].append("Donation certificates (Spendenbescheinigungen)")
    print("  ⚠️  No donation certificate template found")

print("\n🔄 6. WORKFLOW ANALYSIS...")
print("-" * 40)

# Check recent invoices
recent_invoices = models.execute_kw(db, uid, password,
    'account.move', 'search_count',
    [[['move_type', '=', 'out_invoice'],
      ['create_date', '>', (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')]]])

gap_report['workflows']['monthly_invoices'] = recent_invoices
print(f"✓ Invoices (last 30 days): {recent_invoices}")

# Check Events Integration
events = models.execute_kw(db, uid, password,
    'event.event', 'search_count',
    [[]])

gap_report['workflows']['events_count'] = events
print(f"✓ Events configured: {events}")

# Check POS
pos_config = models.execute_kw(db, uid, password,
    'pos.config', 'search_count',
    [[]])

gap_report['workflows']['pos_configs'] = pos_config
print(f"✓ POS Configurations: {pos_config}")
if pos_config == 0:
    gap_report['missing_features'].append("Point of Sale for bar operations")

print("\n" + "=" * 60)
print("📊 GAP ANALYSIS SUMMARY")
print("=" * 60)

# Key Missing Features
print("\n🚨 CRITICAL GAPS IDENTIFIED:")
for i, gap in enumerate(gap_report['missing_features'], 1):
    print(f"  {i}. {gap}")

# Recommendations
gap_report['recommendations'] = [
    "Implement German COA (SKR49 for non-profits)" if not has_german_coa else None,
    "Add automated bank synchronization (EBICS/FinTS)" if statements < 10 else None,
    "Create donation certificate templates" if not has_donation_cert else None,
    "Setup Stripe reconciliation automation" if has_stripe else None,
    "Configure POS for bar operations" if pos_config == 0 else None,
    "Implement proper cost center structure" if len(analytic) < 5 else None,
]

gap_report['recommendations'] = [r for r in gap_report['recommendations'] if r]

print("\n💡 RECOMMENDATIONS:")
for i, rec in enumerate(gap_report['recommendations'], 1):
    print(f"  {i}. {rec}")

# Additional checks
print("\n🔍 ADDITIONAL FINDINGS:")

# Check for membership
members = models.execute_kw(db, uid, password,
    'res.partner', 'search_count',
    [[['is_company', '=', False], ['customer_rank', '>', 0]]])

print(f"  • Active contacts: {members}")

# Check accounting periods
fiscal_years = models.execute_kw(db, uid, password,
    'account.fiscal.year', 'search_count',
    [[]])

if fiscal_years == 0:
    print("  • No fiscal years configured")
    gap_report['missing_features'].append("Fiscal year configuration")

# Save report
with open('/Users/larsweiler/Development/docker-environments/kulturhaus-dev/gap_report.json', 'w') as f:
    json.dump(gap_report, f, indent=2)

print("\n✅ GAP Analysis complete!")
print("📄 Report saved to gap_report.json")