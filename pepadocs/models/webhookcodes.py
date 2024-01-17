from odoo import models, fields

class UserWebhookCode(models.Model):
    _name = 'user.webhook.code'
    _description = 'User Webhook Code'

    user_id = fields.Many2one('res.users', string='User', required=True, ondelete='cascade')
    webhook_code = fields.Char(string='Webhook Code', required=True)

    _sql_constraints = [
        ('unique_user_webhook_code', 'unique(user_id)', 'Each user can have only one webhook code.'),
    ]