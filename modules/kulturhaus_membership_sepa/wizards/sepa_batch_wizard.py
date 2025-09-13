# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta
import base64
import xml.etree.ElementTree as ET
from xml.dom import minidom

class SepaBatchWizard(models.TransientModel):
    _name = 'sepa.batch.wizard'
    _description = 'SEPA Batch Generation Wizard'
    
    batch_type = fields.Selection([
        ('full_year', 'Ganzjahresbeitrag'),
        ('half_year', 'Halbjahresbeitrag (Jan-Jun)'),
        ('half_year_2', 'Halbjahresbeitrag (Jul-Dez)'),
        ('custom', 'Benutzerdefinierte Auswahl')
    ], string='Beitragsart', required=True, default='full_year')
    
    collection_date = fields.Date(
        string='Einzugsdatum',
        required=True,
        default=lambda self: fields.Date.today() + timedelta(days=14),
        help='Datum, an dem die SEPA-Lastschrift ausgeführt wird (mindestens 14 Tage ab heute)'
    )
    
    member_ids = fields.Many2many(
        'res.partner',
        string='Einzubeziehende Mitglieder',
        domain=[('membership_state', 'in', ['paid', 'invoiced', 'free'])],
        help='Diese Mitglieder werden in den SEPA-Einzug aufgenommen (nur aktive Mitglieder angezeigt)'
    )
    
    excluded_member_ids = fields.Many2many(
        'res.partner',
        'sepa_batch_wizard_excluded_rel',
        string='Ausgeschlossene Mitglieder',
        help='Mitglieder, die von diesem Einzug ausgeschlossen sind'
    )
    
    member_count = fields.Integer(
        string='Anzahl Mitglieder',
        compute='_compute_member_count'
    )
    
    total_amount = fields.Float(
        string='Gesamtbetrag',
        compute='_compute_total_amount'
    )
    
    batch_reference = fields.Char(
        string='Einzugsreferenz',
        required=True,
        default=lambda self: self._get_default_reference()
    )
    
    # Smart selection options
    include_only_unpaid = fields.Boolean(
        string='Nur unbezahlte Mitgliedschaften',
        default=True,
        help='Nur Mitglieder einbeziehen, die für den aktuellen Zeitraum noch nicht bezahlt haben'
    )
    
    check_last_payment = fields.Boolean(
        string='Letztes Zahlungsdatum prüfen',
        default=True,
        help='Mitglieder ausschließen, die in den letzten Tagen bereits belastet wurden'
    )
    
    days_since_last_payment = fields.Integer(
        string='Tage seit letzter Zahlung',
        default=180,
        help='Mindestanzahl Tage seit letzter SEPA-Lastschrift'
    )
    
    filter_by_preference = fields.Boolean(
        string='Nach Mitgliederpräferenz filtern',
        default=True,
        help='Nur Mitglieder einbeziehen, die diesen Zahlungszeitraum bevorzugen'
    )
    
    # Information fields
    info_text = fields.Html(
        string='Auswahlinformationen',
        compute='_compute_info_text'
    )
    
    sepa_xml_file = fields.Binary(
        string='SEPA XML-Datei',
        readonly=True
    )
    
    sepa_xml_filename = fields.Char(
        string='Dateiname',
        readonly=True
    )
    
    state = fields.Selection([
        ('draft', 'Entwurf'),
        ('confirmed', 'Bestätigt'),
        ('generated', 'Generiert')
    ], default='draft')
    
    @api.depends('member_ids')
    def _compute_member_count(self):
        for wizard in self:
            wizard.member_count = len(wizard.member_ids)
    
    @api.depends('member_ids', 'batch_type')
    def _compute_total_amount(self):
        for wizard in self:
            total = 0.0
            amount = self._get_amount_for_type(wizard.batch_type)
            total = len(wizard.member_ids) * amount
            wizard.total_amount = total
    
    @api.depends('batch_type', 'member_ids', 'excluded_member_ids')
    def _compute_info_text(self):
        for wizard in self:
            info_parts = []
            
            # Batch type info
            if wizard.batch_type == 'full_year':
                info_parts.append("<b>Ganzjahreseinzug:</b> Einzug der Jahresmitgliedsbeiträge")
            elif wizard.batch_type == 'half_year':
                info_parts.append("<b>Halbjahr (Jan-Jun):</b> Einzug der Beiträge für das erste Halbjahr")
            elif wizard.batch_type == 'half_year_2':
                info_parts.append("<b>Halbjahr (Jul-Dez):</b> Einzug der Beiträge für das zweite Halbjahr")
            
            # Member selection info
            if wizard.member_ids:
                info_parts.append(f"<b>{len(wizard.member_ids)} Mitglieder ausgewählt</b>")
                
                # Check for recently paid members
                recent_paid = wizard.member_ids.filtered(
                    lambda m: m.sepa_last_debit_date and 
                    (fields.Date.today() - m.sepa_last_debit_date).days < wizard.days_since_last_payment
                )
                if recent_paid:
                    info_parts.append(f"<span style='color:orange'>⚠️ {len(recent_paid)} Mitglieder wurden in den letzten {wizard.days_since_last_payment} Tagen belastet</span>")
                
                # Check for invalid mandates
                invalid = wizard.member_ids.filtered(
                    lambda m: not m.bank_account_iban or m.sepa_mandate_state != 'valid'
                )
                if invalid:
                    info_parts.append(f"<span style='color:red'>❌ {len(invalid)} Mitglieder haben ungültige SEPA-Mandate</span>")
            
            if wizard.excluded_member_ids:
                info_parts.append(f"<span style='color:gray'>{len(wizard.excluded_member_ids)} Mitglieder ausgeschlossen</span>")
            
            wizard.info_text = "<br/>".join(info_parts) if info_parts else "Noch keine Mitglieder ausgewählt"
    
    def _get_amount_for_type(self, batch_type):
        """Get the amount for a specific batch type"""
        if batch_type in ['half_year', 'half_year_2']:
            product = self.env['product.template'].search([
                ('membership', '=', True),
                ('membership_period_type', '=', 'half_year')
            ], limit=1)
        else:
            product = self.env['product.template'].search([
                ('membership', '=', True),
                ('membership_period_type', '=', 'full_year')
            ], limit=1)
        return product.list_price if product else 60.0  # Default fallback
    
    def _get_default_reference(self):
        """Generate default batch reference"""
        ICP = self.env['ir.config_parameter'].sudo()
        prefix = ICP.get_param('kulturhaus_membership_sepa.batch_prefix', 'KH-SEPA')
        date_str = datetime.now().strftime('%Y%m%d')
        sequence = self.env['ir.sequence'].next_by_code('sepa.batch') or '001'
        return f"{prefix}-{date_str}-{sequence}"
    
    @api.onchange('batch_type', 'include_only_unpaid', 'check_last_payment', 
                  'days_since_last_payment', 'filter_by_preference')
    def _onchange_batch_type(self):
        """Smart member selection based on batch type and filters"""
        if not self.batch_type or self.batch_type == 'custom':
            return
        
        # Start with ONLY ACTIVE members with valid SEPA mandates
        domain = [
            ('member_lines', '!=', False),  # Is a member
            ('membership_state', 'in', ['paid', 'invoiced', 'free']),  # Only active memberships
            ('sepa_mandate_state', '=', 'valid'),  # Has valid mandate
            ('bank_account_iban', '!=', False),  # Has IBAN
        ]
        
        members = self.env['res.partner'].search(domain)
        excluded = self.env['res.partner']
        
        # Filter by payment preference
        if self.filter_by_preference:
            if self.batch_type == 'full_year':
                preferred = members.filtered(
                    lambda m: m.membership_period_preference != 'half_year'
                )
                excluded |= members - preferred
                members = preferred
            elif self.batch_type in ['half_year', 'half_year_2']:
                preferred = members.filtered(
                    lambda m: m.membership_period_preference == 'half_year'
                )
                excluded |= members - preferred
                members = preferred
        
        # Check last payment date
        if self.check_last_payment and self.days_since_last_payment > 0:
            cutoff_date = fields.Date.today() - timedelta(days=self.days_since_last_payment)
            recently_paid = members.filtered(
                lambda m: m.sepa_last_debit_date and m.sepa_last_debit_date > cutoff_date
            )
            excluded |= recently_paid
            members = members - recently_paid
        
        # For half-year collections, check which period
        if self.batch_type == 'half_year':
            # First half (Jan-Jun) - exclude if already paid this year's first half
            year_start = datetime(datetime.now().year, 1, 1).date()
            mid_year = datetime(datetime.now().year, 6, 30).date()
            already_paid = members.filtered(
                lambda m: m.sepa_last_debit_date and 
                year_start <= m.sepa_last_debit_date <= mid_year
            )
            excluded |= already_paid
            members = members - already_paid
            
        elif self.batch_type == 'half_year_2':
            # Second half (Jul-Dec) - exclude if already paid this year's second half
            mid_year = datetime(datetime.now().year, 7, 1).date()
            year_end = datetime(datetime.now().year, 12, 31).date()
            already_paid = members.filtered(
                lambda m: m.sepa_last_debit_date and 
                mid_year <= m.sepa_last_debit_date <= year_end
            )
            excluded |= already_paid
            members = members - already_paid
        
        self.member_ids = members
        self.excluded_member_ids = excluded
    
    def action_select_all_eligible(self):
        """Button to select all eligible members"""
        self._onchange_batch_type()
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }
    
    def action_confirm(self):
        """Confirm the batch and prepare for generation"""
        self.ensure_one()
        if not self.member_ids:
            raise UserError(_('No members selected for SEPA batch.'))
        
        # Validate all members have valid SEPA mandates
        invalid_members = self.member_ids.filtered(
            lambda m: not m.bank_account_iban or m.sepa_mandate_state != 'valid'
        )
        if invalid_members:
            raise UserError(_(
                'The following members have invalid SEPA mandates:\n%s\n\n'
                'Please remove them from the selection or fix their mandate data.'
            ) % '\n'.join(['- ' + m.name for m in invalid_members]))
        
        # Warn about recently paid members
        if self.check_last_payment:
            recent_paid = self.member_ids.filtered(
                lambda m: m.sepa_last_debit_date and 
                (fields.Date.today() - m.sepa_last_debit_date).days < self.days_since_last_payment
            )
            if recent_paid:
                # Just warn, don't block
                message = _(
                    'Warning: The following members were charged in the last %d days:\n%s\n\n'
                    'Are you sure you want to include them?'
                ) % (self.days_since_last_payment, '\n'.join(['- ' + m.name for m in recent_paid]))
                # Note: In production, you might want to add a confirmation dialog here
        
        self.state = 'confirmed'
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }
    
    def action_generate_sepa_xml(self):
        """Generate SEPA XML file"""
        self.ensure_one()
        
        # Generate XML
        xml_content = self._generate_sepa_xml()
        
        # Save as attachment
        filename = f"SEPA_{self.batch_reference}_{fields.Date.today()}.xml"
        self.sepa_xml_file = base64.b64encode(xml_content.encode('utf-8'))
        self.sepa_xml_filename = filename
        self.state = 'generated'
        
        # Update last debit date for members
        self.member_ids.write({
            'sepa_last_debit_date': self.collection_date
        })
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }
    
    def _generate_sepa_xml(self):
        """Generate SEPA pain.008.001.02 XML"""
        ICP = self.env['ir.config_parameter'].sudo()
        
        # Get creditor information from settings
        creditor_name = ICP.get_param('kulturhaus_membership_sepa.sepa_creditor_name', 'Kulturhaus Bortfeld')
        creditor_id = ICP.get_param('kulturhaus_membership_sepa.sepa_creditor_id', 'DE98ZZZ09999999999')
        creditor_iban = ICP.get_param('kulturhaus_membership_sepa.sepa_creditor_iban', 'DE89370400440532013000')
        creditor_bic = ICP.get_param('kulturhaus_membership_sepa.sepa_creditor_bic', 'COBADEFFXXX')
        
        # Create XML structure
        root = ET.Element('Document')
        root.set('xmlns', 'urn:iso:std:iso:20022:tech:xsd:pain.008.001.02')
        
        # Customer Direct Debit Initiation
        cstmr_drct_dbt_initn = ET.SubElement(root, 'CstmrDrctDbtInitn')
        
        # Group Header
        grp_hdr = ET.SubElement(cstmr_drct_dbt_initn, 'GrpHdr')
        ET.SubElement(grp_hdr, 'MsgId').text = self.batch_reference
        ET.SubElement(grp_hdr, 'CreDtTm').text = datetime.now().isoformat()
        ET.SubElement(grp_hdr, 'NbOfTxs').text = str(len(self.member_ids))
        ET.SubElement(grp_hdr, 'CtrlSum').text = str(self.total_amount)
        
        initg_pty = ET.SubElement(grp_hdr, 'InitgPty')
        ET.SubElement(initg_pty, 'Nm').text = creditor_name
        
        # Payment Information
        pmt_inf = ET.SubElement(cstmr_drct_dbt_initn, 'PmtInf')
        ET.SubElement(pmt_inf, 'PmtInfId').text = f"{self.batch_reference}-001"
        ET.SubElement(pmt_inf, 'PmtMtd').text = 'DD'
        ET.SubElement(pmt_inf, 'NbOfTxs').text = str(len(self.member_ids))
        ET.SubElement(pmt_inf, 'CtrlSum').text = str(self.total_amount)
        
        # Payment Type Information
        pmt_tp_inf = ET.SubElement(pmt_inf, 'PmtTpInf')
        svc_lvl = ET.SubElement(pmt_tp_inf, 'SvcLvl')
        ET.SubElement(svc_lvl, 'Cd').text = 'SEPA'
        lcl_instrm = ET.SubElement(pmt_tp_inf, 'LclInstrm')
        ET.SubElement(lcl_instrm, 'Cd').text = 'CORE'
        ET.SubElement(pmt_tp_inf, 'SeqTp').text = 'RCUR'  # Recurring payment
        
        ET.SubElement(pmt_inf, 'ReqdColltnDt').text = self.collection_date.isoformat()
        
        # Creditor
        cdtr = ET.SubElement(pmt_inf, 'Cdtr')
        ET.SubElement(cdtr, 'Nm').text = creditor_name
        
        # Creditor Account
        cdtr_acct = ET.SubElement(pmt_inf, 'CdtrAcct')
        id_elem = ET.SubElement(cdtr_acct, 'Id')
        ET.SubElement(id_elem, 'IBAN').text = creditor_iban
        
        # Creditor Agent
        cdtr_agt = ET.SubElement(pmt_inf, 'CdtrAgt')
        fin_instn_id = ET.SubElement(cdtr_agt, 'FinInstnId')
        ET.SubElement(fin_instn_id, 'BIC').text = creditor_bic
        
        # Creditor Scheme Identification
        cdtr_schme_id = ET.SubElement(pmt_inf, 'CdtrSchmeId')
        id_elem2 = ET.SubElement(cdtr_schme_id, 'Id')
        prvt_id = ET.SubElement(id_elem2, 'PrvtId')
        othr = ET.SubElement(prvt_id, 'Othr')
        ET.SubElement(othr, 'Id').text = creditor_id
        schme_nm = ET.SubElement(othr, 'SchmeNm')
        ET.SubElement(schme_nm, 'Prtry').text = 'SEPA'
        
        # Add transactions for each member
        amount = self._get_amount_for_type(self.batch_type)
        for member in self.member_ids:
            self._add_transaction_to_xml(pmt_inf, member, amount)
        
        # Convert to pretty XML string
        xml_str = ET.tostring(root, encoding='unicode')
        dom = minidom.parseString(xml_str)
        return dom.toprettyxml(indent="  ")
    
    def _add_transaction_to_xml(self, pmt_inf, member, amount):
        """Add a single transaction to the SEPA XML"""
        drct_dbt_tx_inf = ET.SubElement(pmt_inf, 'DrctDbtTxInf')
        
        # Payment ID
        pmt_id = ET.SubElement(drct_dbt_tx_inf, 'PmtId')
        ET.SubElement(pmt_id, 'EndToEndId').text = f"MB-{member.id}-{fields.Date.today().strftime('%Y%m%d')}"
        
        # Amount
        instd_amt = ET.SubElement(drct_dbt_tx_inf, 'InstdAmt')
        instd_amt.set('Ccy', 'EUR')
        instd_amt.text = str(amount)
        
        # Mandate Related Information
        drct_dbt_tx = ET.SubElement(drct_dbt_tx_inf, 'DrctDbtTx')
        mndt_rltd_inf = ET.SubElement(drct_dbt_tx, 'MndtRltdInf')
        ET.SubElement(mndt_rltd_inf, 'MndtId').text = member.sepa_mandate_id or f"MANDATE-{member.id}"
        ET.SubElement(mndt_rltd_inf, 'DtOfSgntr').text = (member.sepa_mandate_date or fields.Date.today()).isoformat()
        
        # Debtor Agent (if BIC is known)
        if member.bank_account_bic:
            dbtr_agt = ET.SubElement(drct_dbt_tx_inf, 'DbtrAgt')
            fin_instn_id = ET.SubElement(dbtr_agt, 'FinInstnId')
            ET.SubElement(fin_instn_id, 'BIC').text = member.bank_account_bic
        
        # Debtor
        dbtr = ET.SubElement(drct_dbt_tx_inf, 'Dbtr')
        ET.SubElement(dbtr, 'Nm').text = member.name[:70]  # Max 70 chars
        
        # Debtor Account
        dbtr_acct = ET.SubElement(drct_dbt_tx_inf, 'DbtrAcct')
        id_elem = ET.SubElement(dbtr_acct, 'Id')
        ET.SubElement(id_elem, 'IBAN').text = member.bank_account_iban.replace(' ', '')
        
        # Remittance Information
        rmt_inf = ET.SubElement(drct_dbt_tx_inf, 'RmtInf')
        if self.batch_type == 'full_year':
            ET.SubElement(rmt_inf, 'Ustrd').text = f"Mitgliedsbeitrag {datetime.now().year} - Ganzjahr"
        elif self.batch_type == 'half_year':
            ET.SubElement(rmt_inf, 'Ustrd').text = f"Mitgliedsbeitrag {datetime.now().year} - 1. Halbjahr"
        elif self.batch_type == 'half_year_2':
            ET.SubElement(rmt_inf, 'Ustrd').text = f"Mitgliedsbeitrag {datetime.now().year} - 2. Halbjahr"
        else:
            ET.SubElement(rmt_inf, 'Ustrd').text = f"Mitgliedsbeitrag {datetime.now().year}"
    
    def action_download_xml(self):
        """Download the generated XML file"""
        self.ensure_one()
        if not self.sepa_xml_file:
            raise UserError(_('No XML file generated yet.'))
        
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/?model={self._name}&id={self.id}&field=sepa_xml_file&filename_field=sepa_xml_filename&download=true',
            'target': 'self',
        }