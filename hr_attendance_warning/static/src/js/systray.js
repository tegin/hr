odoo.define('hr_attendance_warning.systray', function (require) {
    "use strict";

    var config = require('web.config');
    var core = require('web.core');
    var session = require('web.session');
    var SystrayMenu = require('web.SystrayMenu');
    var Widget = require('web.Widget');
    var time = require('web.time');
    var bus = require('bus.bus').bus;
    var chat_manager = require('mail.chat_manager');

    var QWeb = core.qweb;

    var WarningMenu = Widget.extend({
        template:'att_warning.view.Menu',
        events: {
            "click": "_onMenuClick",
            "click .o_mail_channel_preview": "_onWarningClick",
            "click .o_view_all_warnings": "_viewAllWarnings",
        },
        start: function () {
            this.$warnings_preview = this.$('.o_mail_navbar_dropdown_channels');
            this._updateWarningsPreview();
            var channel = 'hr.attendance.warning';
            bus.add_channel(channel);
            bus.on('notification', this, this._updateWarningsPreview);
            return this._super();
        },

        // Private

        _getWarningsData: function(){
            var self = this;

            return self._rpc({
                model: 'hr.attendance.warning',
                method: 'pending_warnings_count',
                kwargs: {
                    context: session.user_context,
                },
            }).then(function (data) {
                self.warnings = data;
                for (var i = 0; i < self.warnings.length; ++i) {
                    self.warnings[i]['date_ago'] = moment(time.str_to_datetime(self.warnings[i]['date'])).fromNow();
                }
                self.warningsCounter = data.length;
                self.$('.o_notification_counter').text(self.warningsCounter);
                self.$el.toggleClass('o_no_notification', !self.warningsCounter);
            });
        },

        _isOpen: function () {
            return this.$el.hasClass('open');
        },

        _updateWarningsPreview: function () {
            var self = this;
            self._getWarningsData().then(function (){
                self.$warnings_preview.html(QWeb.render('att_warning.view.Data', {
                    warnings : self.warnings
                }));
            });
        },

        _onWarningClick: function (event) {

            var warning_id = parseInt($(event.currentTarget).data('warning-id'));
            this.do_action({
                type: 'ir.actions.act_window',
                name: 'Attendance Warnings',
                res_model: 'hr.attendance.warning',
                views: [[false, 'form']],
                res_id: warning_id
            });
        },

        _viewAllWarnings: function (event){
            this.do_action({
                type: 'ir.actions.act_window',
                name: 'Attendance Warnings',
                res_model: 'hr.attendance.warning',
                context: "{'search_default_pending': 1, }",
                views: [[false, 'list']],
            });
        },

        _onMenuClick: function () {
            if (!this._isOpen()) {
                this._updateWarningsPreview();
            }
        },

    });

    SystrayMenu.Items.push(WarningMenu);

    return {
        WarningMenu: WarningMenu,
    };
});