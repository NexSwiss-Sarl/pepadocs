# controllers/main.py
import json
import urllib.request
import urllib.parse
import secrets
from odoo import http
from odoo.http import request
from ..models import tools

class PepadocsController(http.Controller):
    @http.route('/pepadocs/webhook', type='http', auth='public', csrf=False, methods=['POST'])
    def handle_webhook(self, **kwargs):
        ConfigParameter = request.env['ir.config_parameter'].sudo()

        autoSyncEmployees = False
        autoSyncEmployees = ConfigParameter.get_param('pepadocs.autoSyncEmployees')
        if not autoSyncEmployees:
            autoSyncEmployees = False

        syncWithModoGroupId = ConfigParameter.get_param('pepadocs.syncWithModoGroupId')
        if syncWithModoGroupId:
            try:
                syncWithModoGroupId = int(syncWithModoGroupId)
            except ValueError:
                # Handle the case where the value is not a valid integer
                syncWithModoGroupId = 0  # or some default value or logging
        else:
            syncWithModoGroupId = 0 


        idPage = ConfigParameter.get_param('pepadocs.idPage')
        if not idPage:
            return {'error':'idPage not defined'}

        
        id_user = request.params.get('id_user')
        webhook_code = request.params.get('webhookCode')
        odoo_user = request.params.get('odooUser')
        confirmCode = request.params.get('confirmCode')
        pepadocsUser = request.params.get('pepadocsUser')

        
            # Check if any required data is missing
        if None in (id_user, webhook_code, odoo_user, confirmCode, pepadocsUser):
            return json.dumps({'status': 'error', 'error': 'Missing data'})


        # Check if the webhook code matches the stored webhook code for the Odoo user
        odoo_user_record = request.env['res.users'].browse(int(odoo_user))
        if odoo_user_record:
            user_webhook_code = request.env['user.webhook.code'].sudo().search([
                ('user_id', '=', int(odoo_user))
            ], limit=1)
            
            user = odoo_user_record.sudo().pepadocs_user_id

            try:
                user = int(user) if user else 0
            except ValueError:
                user = 0

            if user < 1 and autoSyncEmployees != 'True':
                return json.dumps({'status': 'error', 'error': 'Your odoo account is not linked to any pepadocs account, you must contact an admin to link it as the auto link functionality is disabled by your admin.'})

            if user > 0 and int(pepadocsUser) != user:
                return json.dumps({'status': 'error', 'error': 'You cannot change the pepadocs account linked to your odoo account. Ask an admin to remove the pepadocs id account from your odoo user settings page to do this. Maybe you are logged in pepadocs with the wrong account ?'})



            if user_webhook_code:
                if user_webhook_code.webhook_code == webhook_code:
                    user_webhook_code.write({'webhook_code': "null"})
                    json_response = tools.pepadocs_api(request,{
                        'class': 'Login',
                        'action': 'validateUserERPSync',
                        'id_page': idPage,
                        'id_user': pepadocsUser,
                        'odoouser': odoo_user,
                        'confirmCode': confirmCode,
                    })

                    if json_response.get('status') == 'success' and json_response.get('success'):
                        odoo_user_record = odoo_user_record.with_context(from_controller=True)
                        odoo_user_record.sudo().write({'pepadocs_user_id': int(pepadocsUser)})


                        if syncWithModoGroupId > 0:
                            json_response2 = tools.pepadocs_api(request,{
                                'class': 'ModoGroups',
                                'action': 'update',
                                'id_page': idPage,
                                'id_group': syncWithModoGroupId,
                                'members': pepadocsUser,
                                'what': 'addMembers'
                            })
                            if json_response2.get('status') == 'success' and json_response2.get('success'):
                                return json.dumps({'status': 'success','success':True})
                            else:
                                return json.dumps({'status': 'error', 'error': 'Your account has been synchronized, but an error has occurred preventing you from being added to the correct group: '+json_response2.get('error')})
                        else:
                            return json.dumps({'status': 'success','success':True})
                    else:
                        return json.dumps({'status': 'error', 'error': json_response.get('error')})
                else:
                    user_webhook_code.write({'webhook_code': "null"})
                    return json.dumps({'status': 'error', 'error': 'Invalid webhook code..'})
            else:
                return json.dumps({'status': 'error', 'error': 'no code in memory'})
        else:
            return json.dumps({'status': 'error', 'error': 'odoo user not found'})


    @http.route('/pepadocs/connectUser', type='json', auth='user')
    def compute_value(self, **kwargs):
        
        ConfigParameter = request.env['ir.config_parameter'].sudo()

        autoSyncEmployees = False
        autoSyncEmployees = ConfigParameter.get_param('pepadocs.autoSyncEmployees')
        if not autoSyncEmployees:
            autoSyncEmployees = False

        pepadocs_webdomain = ConfigParameter.get_param('pepadocs.webdomain')
        if not pepadocs_webdomain:
            return {'error':'webdomain not defined'}

        idPage = ConfigParameter.get_param('pepadocs.idPage')
        if not idPage:
            return {'error':'idPage not defined'}


        # Access the current user
        current_user = request.env.user

        if not current_user:
            return {'error':'no user found'}

        # Retrieve the Pepadocs User ID
        user = current_user.pepadocs_user_id

        user_id = current_user.id

        webhookcode = secrets.token_hex(16)
        
        # Check if a record already exists for the user_id
        user_webhook_code = request.env['user.webhook.code'].sudo().search([
            ('user_id', '=', user_id)
        ], limit=1)

        try:
            user = int(user) if user else 0
        except ValueError:
            user = 0


        if user<1 and autoSyncEmployees != 'True':
            return {'error':"This odoo account is not synchronized with a pepadocs account. Please contact your administrator if you need access to pepadocs."}
        elif user<1 and autoSyncEmployees == 'True':

            if user_webhook_code:
                # Update the existing record with a new webhook code
                user_webhook_code.write({'webhook_code': webhookcode})
            else:
                # Create a new record
                user_webhook_code = request.env['user.webhook.code'].sudo().create({
                    'user_id': user_id,
                    'webhook_code': webhookcode,
                })

            return {'error':'userIdToSync','webdomain':pepadocs_webdomain,'webhookcode':webhookcode,'id_page':idPage,'odoouser':user_id}
        else:
            json_response = tools.pepadocs_api(request,{
                'class': 'Login',
                'action': 'getUserConnectToken',
                'id_page': idPage,
                'id_user': user,
            })


            if json_response.get('status') == 'success' and json_response.get('success'):
                data_encoded = json_response.get('data', '')
                
                if data_encoded:
                    data = json.loads(data_encoded)
                    if isinstance(data, dict):
                        return {
                            'id_token': data.get('id_token', ''),
                            'token': data.get('token', ''),
                            'user': data.get('id_user', '')
                        }
                    else:
                        return {'error': 'Data is not a dictionary'}
                else:
                    return {'error': 'No data found in JSON response'}
            else:
                
                if user_webhook_code:
                    # Update the existing record with a new webhook code
                    user_webhook_code.write({'webhook_code': webhookcode})
                else:
                    # Create a new record
                    user_webhook_code = request.env['user.webhook.code'].sudo().create({
                        'user_id': user_id,
                        'webhook_code': webhookcode,
                    })

                json_response['webdomain'] = pepadocs_webdomain
                json_response['webhookcode'] = webhookcode
                json_response['id_page'] = idPage
                json_response['odoouser'] = user_id
                return json_response
