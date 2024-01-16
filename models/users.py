from odoo import models, fields, api, SUPERUSER_ID

class pepadocsUsers(models.Model):
    _inherit = 'res.users'

    pepadocs_user_id = fields.Char(string='Pepadocs User ID')

    @api.model
    def write(self, vals):
        if 'pepadocs_user_id' in vals and self.env.uid != SUPERUSER_ID:
            # Check if the current user is not an administrator
            if not self.env.user.has_group('base.group_system'):
                raise UserError("Only administrators can edit the 'Pepadocs User ID' field.")
        return super(pepadocsUsers, self).write(vals)