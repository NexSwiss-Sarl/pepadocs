from odoo import api, SUPERUSER_ID  
from . import controllers
from . import models

def uninstall_hook(cr, registry):
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        env['pepadocs.tools'].uninstall_hook(env)
