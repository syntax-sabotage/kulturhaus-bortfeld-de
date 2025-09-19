# CRITICAL: Odoo 18 View Issues and Fixes

## ⚠️ COMMON VIEW ERRORS TO AVOID

### 1. Broken Form View with Technical List Columns
**SYMPTOM**: When clicking a line item, you see a broken view with wrong columns like "Dokumenten Name", "Aktivitätstyp", etc.

**CAUSE**: Incorrectly embedding chatter fields directly in the form
```xml
<!-- ❌ WRONG - Creates broken embedded lists -->
<div class="oe_chatter">
    <field name="message_follower_ids"/>
    <field name="activity_ids"/>
    <field name="message_ids"/>
</div>
```

**FIX**: Use the proper chatter widget
```xml
<!-- ✅ CORRECT -->
<chatter/>
```

### 2. Odoo 18 Breaking Changes

#### Tree vs List Elements
**Odoo 18 REQUIRES `<list>` instead of `<tree>`**
```xml
<!-- ❌ WRONG in Odoo 18 -->
<tree string="Records">
    <field name="name"/>
</tree>

<!-- ✅ CORRECT in Odoo 18 -->
<list string="Records">
    <field name="name"/>
</list>
```

#### Invisible Attributes
**Odoo 18 REMOVED `attrs` and `states` attributes completely**
```xml
<!-- ❌ WRONG - attrs/states removed in Odoo 18 -->
<button attrs="{'invisible': [('state', '!=', 'draft')]}"/>
<field states="{'draft': [('readonly', False)]}"/>

<!-- ✅ CORRECT - Use direct Python expressions -->
<button invisible="state != 'draft'"/>
<field readonly="state != 'draft'"/>
```

#### Column Visibility
```xml
<!-- ❌ WRONG -->
<field name="field" invisible="1"/>

<!-- ✅ CORRECT for hiding columns in list views -->
<field name="field" column_invisible="True"/>
```

### 3. View Priority and Loading

**ALWAYS set explicit priorities**:
```xml
<record id="view_form" model="ir.ui.view">
    <field name="priority" eval="1"/>  <!-- Form view should have lowest priority -->
</record>

<record id="view_list" model="ir.ui.view">
    <field name="priority" eval="10"/> <!-- List view higher priority -->
</record>
```

### 4. Action Window View Bindings

**EXPLICITLY bind views to actions to prevent auto-generated views**:
```xml
<record id="action_model" model="ir.actions.act_window">
    <field name="name">Model Name</field>
    <field name="res_model">model.name</field>
    <field name="view_mode">list,form</field>
</record>

<!-- EXPLICIT BINDINGS -->
<record id="action_model_list" model="ir.actions.act_window.view">
    <field name="sequence">1</field>
    <field name="view_mode">list</field>
    <field name="view_id" ref="view_list"/>
    <field name="act_window_id" ref="action_model"/>
</record>

<record id="action_model_form" model="ir.actions.act_window.view">
    <field name="sequence">2</field>
    <field name="view_mode">form</field>
    <field name="view_id" ref="view_form"/>
    <field name="act_window_id" ref="action_model"/>
</record>
```

### 5. Manifest File Loading Order

**CRITICAL**: Load files in correct order
```python
'data': [
    # Security FIRST
    'security/security.xml',
    'security/ir.model.access.csv',
    
    # Data files
    'data/sequence.xml',
    
    # Views - main views BEFORE dependent views
    'views/res_partner_views.xml',  # Extensions first
    'views/main_model_views.xml',   # Main model views
    'wizards/wizard_views.xml',     # Wizards after main views
    'views/menu.xml',                # Menus LAST
],
```

## 🔧 DEBUGGING BROKEN VIEWS

### Check what views exist:
```bash
sudo -u postgres psql -d DATABASE_NAME -c "
SELECT id, name, model, priority, mode 
FROM ir_ui_view 
WHERE model = 'your.model' 
ORDER BY priority;"
```

### Delete broken/auto-generated views:
```sql
DELETE FROM ir_ui_view 
WHERE model = 'your.model' 
AND (name LIKE '%auto%' OR arch_fs IS NULL);
```

### Force module upgrade:
```sql
UPDATE ir_module_module 
SET state = 'to upgrade' 
WHERE name = 'your_module';
```

## ⚡ QUICK CHECKLIST

When views are broken:
1. ✅ Check chatter is using `<chatter/>` widget, not embedded fields
2. ✅ Verify all `<tree>` changed to `<list>` 
3. ✅ Remove all `attrs` and `states` attributes
4. ✅ Set explicit view priorities
5. ✅ Create explicit action-view bindings
6. ✅ Check manifest file loading order
7. ✅ Clear Python cache: `find /path/to/module -name "__pycache__" -exec rm -rf {} +`
8. ✅ Restart Odoo after changes

## 🚨 MOST COMMON MISTAKE

**The #1 cause of broken views**: Embedding chatter fields directly instead of using `<chatter/>` widget. This creates broken technical list views that show wrong columns.