from odoo import models, fields, api


#todo description index.html and screenshots
class pepadocsSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    pepadocs_idPage = fields.Integer(string='Pepadocs idPage')
    pepadocs_webdomain = fields.Char(string='Pepadocs webdomain')
    pepadocs_id = fields.Char(string='Pepadocs ID')
    pepadocs_key = fields.Char(string='Pepadocs Key')
    pepadocs_autoSyncEmployees = fields.Boolean(string='Pepadocs autoSyncEmployees')
    pepadocs_syncWithModoGroupId = fields.Integer(string='Pepadocs syncWithModoGroupId')

    @api.model
    def default_get(self, fields):
        res = super(pepadocsSettings, self).default_get(fields)
        # Set the default value for pepadocs_autoSyncEmployees to True
        res['pepadocs_autoSyncEmployees'] = True
        return res

    def set_values(self):
        super(pepadocsSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('pepadocs.idPage', self.pepadocs_idPage)
        self.env['ir.config_parameter'].sudo().set_param('pepadocs.webdomain', self.pepadocs_webdomain)
        self.env['ir.config_parameter'].sudo().set_param('pepadocs.id', self.pepadocs_id)
        self.env['ir.config_parameter'].sudo().set_param('pepadocs.key', self.pepadocs_key)
        self.env['ir.config_parameter'].sudo().set_param('pepadocs.autoSyncEmployees', self.pepadocs_autoSyncEmployees)
        self.env['ir.config_parameter'].sudo().set_param('pepadocs.syncWithModoGroupId', self.pepadocs_syncWithModoGroupId)

    @api.model
    def get_values(self):
        res = super(pepadocsSettings, self).get_values()
        syncWithModoGroupId = self.env['ir.config_parameter'].sudo().get_param('pepadocs.syncWithModoGroupId')
        if syncWithModoGroupId:
            try:
                syncWithModoGroupId = int(syncWithModoGroupId)
            except ValueError:
                # Handle the case where the value is not a valid integer
                syncWithModoGroupId = 0  # or some default value or logging
        idPage = self.env['ir.config_parameter'].sudo().get_param('pepadocs.idPage')
        if idPage:
            try:
                idPage = int(idPage)
            except ValueError:
                # Handle the case where the value is not a valid integer
                idPage = 0  # or some default value or logging
        res.update(
            pepadocs_idPage=idPage,
            pepadocs_webdomain=self.env['ir.config_parameter'].sudo().get_param('pepadocs.webdomain'),
            pepadocs_id=self.env['ir.config_parameter'].sudo().get_param('pepadocs.id'),
            pepadocs_key=self.env['ir.config_parameter'].sudo().get_param('pepadocs.key'),
            pepadocs_autoSyncEmployees=(self.env['ir.config_parameter'].sudo().get_param('pepadocs.autoSyncEmployees') == 'True'),
            pepadocs_syncWithModoGroupId=syncWithModoGroupId,
        )
        return res
