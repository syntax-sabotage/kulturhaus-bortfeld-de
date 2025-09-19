import xmlrpc.client

url = 'https://kulturhaus-bortfeld.de'
db = 'kulturhive'
username = 'admin'
password = 'khaus'

# Connect
common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

# Delete all broken views for board.resolution
view_ids = models.execute_kw(db, uid, password,
    'ir.ui.view', 'search',
    [[['model', '=', 'board.resolution']]])

print(f"Found {len(view_ids)} views to delete")

# Delete them
for view_id in view_ids:
    try:
        models.execute_kw(db, uid, password,
            'ir.ui.view', 'unlink', [[view_id]])
        print(f"Deleted view {view_id}")
    except:
        print(f"Could not delete view {view_id}")

# Create a simple form view
form_arch = """<?xml version="1.0"?>
<form string="Board Resolution">
    <sheet>
        <group>
            <field name="name"/>
            <field name="title"/>
            <field name="date"/>
            <field name="state"/>
        </group>
    </sheet>
</form>"""

# Create the form view
form_id = models.execute_kw(db, uid, password,
    'ir.ui.view', 'create',
    [{
        'name': 'board.resolution.simple.form',
        'model': 'board.resolution',
        'priority': 1,
        'arch_base': form_arch,
        'type': 'form'
    }])

print(f"Created form view with ID {form_id}")

# Create a simple list view
list_arch = """<?xml version="1.0"?>
<list string="Board Resolutions">
    <field name="name"/>
    <field name="title"/>
    <field name="date"/>
    <field name="state"/>
</list>"""

list_id = models.execute_kw(db, uid, password,
    'ir.ui.view', 'create',
    [{
        'name': 'board.resolution.simple.list',
        'model': 'board.resolution', 
        'priority': 10,
        'arch_base': list_arch,
        'type': 'list'
    }])

print(f"Created list view with ID {list_id}")

print("Views fixed!")