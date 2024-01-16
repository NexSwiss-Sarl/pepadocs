from odoo import api, models
import json
import urllib.request
import urllib.parse
from odoo import http
from odoo.http import request

def pepadocs_api(self,data):
    pepadocs_id = self.env['ir.config_parameter'].sudo().get_param('pepadocs.id')
    if not pepadocs_id:
        return {'error': 'API NOT CONFIGURED'}

    pepadocs_key = self.env['ir.config_parameter'].sudo().get_param('pepadocs.key')
    if not pepadocs_key:
        return {'error': 'API NOT CONFIGURED'}

    pepadocs_webdomain = self.env['ir.config_parameter'].sudo().get_param('pepadocs.webdomain')
    if not pepadocs_webdomain:
        return {'error': 'DOMAIN NOT CONFIGURED'}

    api_url = 'https://'+pepadocs_webdomain+'/api.php'
    headers = {
        'X-Scid': pepadocs_id,  # Replace with your actual API ID
        'X-Sckey': pepadocs_key,  # Replace with your actual API Key
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0)'
                        ' Gecko/20100101 Firefox/24.0'
    }
    data_encoded = urllib.parse.urlencode(data).encode()

    req = urllib.request.Request(api_url, data=data_encoded, headers=headers)

    try:
        with urllib.request.urlopen(req) as response:
            response_data = response.read()
            json_response = json.loads(response_data.decode())
            
            return json_response


    except urllib.error.HTTPError as e:
        # HTTP error
        return {'error': f'HTTP Error: {e.code} {e.reason}'}
    except urllib.error.URLError as e:
        # URL error
        return {'error': f'URL Error: {e.reason}'}
    except Exception as e:
        # Other exceptions
        return {'error': f'Unexpected Error: {str(e)}'}


class pepadocsTools(models.TransientModel):
    _name = 'pepadocs.tools'
    _description = 'Tools'

    @api.model
    def is_user_admin(self):
        return self.env.user.has_group('base.group_system')

    @api.model
    def refresh_dynamic_menus(self):
        webdomain = self.env['ir.config_parameter'].sudo().get_param('pepadocs.webdomain')
        if not webdomain:
            return

        parent_menu_completed = self.env.ref('pepadocs.menu_pepadocs_completed')
        parent_menu_models = self.env.ref('pepadocs.menu_pepadocs_models')
        parent_menu_calendars = self.env.ref('pepadocs.menu_pepadocs_calendars')

        existing_parent_menu_completed = self.env['ir.ui.menu'].search([('parent_id', '=', parent_menu_completed.id)])
        existing_parent_menu_completed.unlink()

        existing_parent_menu_models = self.env['ir.ui.menu'].search([('parent_id', '=', parent_menu_models.id)])
        existing_parent_menu_models.unlink()

        existing_parent_menu_calendars = self.env['ir.ui.menu'].search([('parent_id', '=', parent_menu_calendars.id)])
        existing_parent_menu_calendars.unlink()

        dynamic_data = self.get_dynamic_menu_data()

        for item in dynamic_data:
            action0 = self.env['ir.actions.client'].create({
                'name': item['name'],
                'tag': 'pepadocs.load_iframe',
                'context': json.dumps({'webdomain':webdomain,'id_doc': item['id_doc'], 'what': 'seeCompleted'})
            })

            self.env['ir.ui.menu'].create({
                'name': item['name'],
                'parent_id': parent_menu_completed.id,
                'action': 'ir.actions.client,' + str(action0.id),
            })

            action = self.env['ir.actions.client'].create({
                'name': item['name'],
                'tag': 'pepadocs.load_iframe',
                'context': json.dumps({'webdomain':webdomain,'id_doc': item['id_doc'], 'what': 'completeModele'})
            })

            self.env['ir.ui.menu'].create({
                'name': item['name'],
                'parent_id': parent_menu_models.id,
                'action': 'ir.actions.client,' + str(action.id),
            })

            action2 = self.env['ir.actions.client'].create({
                'name': item['name'],
                'tag': 'pepadocs.load_iframe',
                'context': json.dumps({'webdomain':webdomain,'id_doc': item['id_doc'], 'what': 'calendar'})
            })

            new_context = {'id_doc': item['id_doc'],'what': 'calendar'}
            self.env['ir.ui.menu'].create({
                'name': item['name'],
                'parent_id': parent_menu_calendars.id,
                'action': 'ir.actions.client,' + str(action2.id),
            })


        existing_action = self.env.ref('pepadocs.pepadocs_open_pepadocs')  # Replace 'module_name' with the actual module name
        existing_action.write({
            'name': 'Ouvrir Pepadocs',
            'tag': 'pepadocs.load_iframe',
            'context': json.dumps({'webdomain':webdomain,'what': 'openPepadocs'})
        })

    def get_dynamic_menu_data(self):
        result = pepadocs_api(self,{
            'class': 'Documents',
            'action': 'getModeles'
        })

        if 'error' in result:
            return []

        return_array = []

        if 'data' in result and isinstance(result['data'], list):
            for model in result['data']:
                if 'name' in model and 'id_doc' in model:
                    return_array.append({
                        'name': model['name'], 
                        'id_doc': model['id_doc']
                    })

        return return_array

    @api.model 
    def logout(self):

        user = self.env.user.pepadocs_user_id
        try:
            user = int(user) if user else 0
        except ValueError:
            user = 0

        result = pepadocs_api(self,{
            'class': 'Login',
            'action': 'logoutUser',
            'id_user':user
        })

        return result

