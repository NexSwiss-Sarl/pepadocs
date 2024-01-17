odoo.define('pepadocs.logout', function (require) {
    "use strict";
    console.log("Loading pepadocs tools");

    var rpc = require('web.rpc');

    $(document).ready(function() {
        var PepadocsAllowLogout = false;

        var pepaLogout = function () {
            return rpc.query({
                model: 'pepadocs.tools',
                method: 'logout',
            }).then(function () {
                console.log("Logout from pepadocs done");
            }).catch(function (error) {
                console.error("Error during Pepadocs logout:", error);
            });
        };

        $('body').on('click', 'a.o_logout, a[data-menu="logout"]', function (event) {
            if(!PepadocsAllowLogout){
                event.preventDefault();
                pepaLogout().then(function() {
                    PepadocsAllowLogout = true;
                    $(event.currentTarget).click();
                }).catch(function () {
                    PepadocsAllowLogout = true;
                    $(event.currentTarget).click();
                });
            } else {
                PepadocsAllowLogout = false;
            }
        });
    });
});


odoo.define('pepadocs.refreshMenuAction', function (require) {
    'use strict';

    var rpc = require('web.rpc');
    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');

    var RefreshMenuAction = AbstractAction.extend({
        start: function () {
            var self = this;
            rpc.query({
                model: 'pepadocs.tools',
                method: 'is_user_admin',
            }).then(function (isAdmin) {
                if (isAdmin) {
                    rpc.query({
                        model: 'pepadocs.tools',
                        method: 'refresh_dynamic_menus',
                    }).then(function () {
                        self.displayNotification({
                            type: 'success',
                            title: 'Success',
                            message: "Menus refreshed successfully, please reload page.",
                            sticky: true
                         });
                         $('.o_content').append('<br><div class="oe_demo oe_picture oe_screenshot">                       <center><img src="/pepadocs/static/description/icon.png" style="max-height: 400px; object-fit: contain;"></center>                     </div><br><div style="margin-left:auto;margin-right:auto; max-width:600px;"><center>Please reload the page, then click on another menu. <br><br>If you didn\'t set up pepadocs yet, please visit your Odoo Settings and set up Pepadocs.<br>Check-out our <a target="_blank" href="https://pepadocs.com/en/guides/category/odoo-with-pepadocs-62">Blog post</a> to learn more or contact us if wished <a href="mailto:contact@nexswiss.ch">contact@nexswiss.ch</a>. </center></div>');
                         //infinite redirection window.location.reload();
                    });
                } else {
                    alert("You should be an admin to refresh the menu. Please ask an admin to do it for you.");
                }
            });
        },
    });

    core.action_registry.add('pepadocs.refresh_menus', RefreshMenuAction);

    return RefreshMenuAction;
});


odoo.define('pepadocs.loadIframe', function(require) {
    'use strict';
    console.log("Loading pepadocs");

    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');


    var pepadocsConnectUser = function(id_token,token,id){
        var iframe = document.getElementById('pepadocsIframe');
        if(iframe == null){
            return;
        }
        iframe.contentWindow.postMessage(JSON.stringify({"type":"Login","action":"connectUser","id_token":id_token,"token":token,"id_user":id}), '*');
    };

    var CustomAction = AbstractAction.extend({
        template: 'pepadocs.main_template',

        willStart: function() {
            console.log("Action Name: ", this.action && this.action.name);
            return this._super.apply(this, arguments);
        },

        start: function() {
            this._super.apply(this, arguments);
            // Your JavaScript goes here
            var iframe = this.$('#pepadocsIframe');

            
            // Attach a 'load' event listener to the iframe
            iframe.on('load', function() {
                if(iframe.attr('logged') == 'yes')
                    return;
                iframe.attr('logged','yes');

                var ajax = require('web.ajax');
                ajax.jsonRpc("/pepadocs/connectUser", 'call', {
                
                }).then(function (result) {
                    if(result.isUserToSync || result.error == "userIdToSync"){
                        if(confirm('To use Pepadocs with odoo, please create a pepadocs.com account and synchronize it with odoo.')){
                            window.location.href = 'https://'+result.webdomain+'/openWindow/Login/ERPSync/'+result.id_page+'_-_'+result.odoouser+'_-_'+result.webhookcode+'_-_'+btoa(location.origin+'/pepadocs/webhook')+'_-_'+btoa(location.href);
                        }
                    }else if(result.error){
                        alert(result.error);
                    }
                    else
                        pepadocsConnectUser(result.id_token,result.token,result.user);
                });
            });

            // Access the variable from the context
            var id_doc, what, webdomain = null;
            if(this.searchModelConfig != null && this.searchModelConfig.context != null && this.searchModelConfig.context != null){
                id_doc = this.searchModelConfig.context.id_doc || 0;
                what = this.searchModelConfig.context.what || '';
                webdomain = this.searchModelConfig.context.webdomain || '';
            }

            var url = '';

            if(what == 'seeCompleted')
                url = 'https://'+webdomain+'/openWindow/Documents/showAnswers/'+id_doc+'/asMainPage/';
            else if(what == 'completeModele')
                url = 'https://'+webdomain+'/openWindow/Documents/complete/'+id_doc+'/asMainPage/';
            else if(what == 'calendar')
                url = 'https://'+webdomain+'/openWindow/Documents/showAgenda/'+id_doc+'/asMainPage';
            else
                url = 'https://'+webdomain+'/';

            iframe[0].src = url;

        },
    });

    core.action_registry.add('pepadocs.load_iframe', CustomAction);

    return CustomAction;
});