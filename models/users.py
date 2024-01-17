from odoo import models, fields, api

class pepadocsUsers(models.Model):
    _inherit = 'res.users'

    pepadocs_user_id = fields.Char(string='Pepadocs User ID')

    @api.model
    def write(self, vals):
        if 'pepadocs_user_id' in vals:
            # Check if the current user is not an administrator
            if not (self.env.user.has_group('base.group_system') or self.env.context.get('from_controller')):
                raise UserError("Only administrators can edit the 'Pepadocs User ID' field.")
        return super(pepadocsUsers, self).write(vals)