# -*- coding: utf-8 -*-
###############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech-Receptives(<http://www.techreceptives.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from odoo import models, fields, api


class ResCompany(models.Model):
    _inherit = "res.company"

    signature = fields.Binary('Signature')
    accreditation = fields.Text('Accreditation')
    approval_authority = fields.Text('Approval Authority')


class ResUsers(models.Model):
    _inherit = "res.users"

    user_line = fields.One2many('op.student', 'user_id', 'User Line')
    child_ids = fields.Many2many(
        'res.users', 'res_user_first_rel1',
        'user_id', 'res_user_second_rel1', string='Childs')

    @api.multi
    def create_user(self, records, user_group=None):
        for rec in records:
            if not rec.user_id:
                user_vals = {
                    'name': rec.name,
                    'login': rec.email or (rec.name + rec.last_name),
                    'partner_id': rec.partner_id.id
                }
                user_id = self.create(user_vals)
                rec.user_id = user_id
                if user_group:
                    user_group.users = user_group.users + user_id

    @api.multi
    def get_user_group(self):
        resp = {'is_student': 0, 'is_parent': 0, 'is_faculty': 0}
        resp['is_student'] = self.partner_id.is_student
        resp['is_parent'] = self.partner_id.is_parent
        resp['is_faculty'] = self.user_has_groups('openeducat_core.group_op_faculty')
        print("RESTPPPPPPPP---------------", resp)
        return resp

    @api.model
    def search_read_for_app(self, domain=None, fields=None, offset=0, limit=None, order=None):

        if self.env.user.partner_id.is_student:
            print("__inside res.user_______")
            print("---student_ res -user")
            domain = domain + [('user_id', '=', self.env.user.id)]
            res = self.env['op.student'].sudo().search_read(domain=domain, fields=fields, offset=offset, limit=limit, order=order)
            print("___-res-_______", res)

            # student = self.env['op.student'].sudo().search([('user_id', '=', self.env.user.id)])
            # print("_______-student-_____", student)
            return res
                # {'user_id':res,
                #     'student_id': student}

        elif self.env.user.partner_id.is_parent:
            print("---parent res user-----")
            parent = self.env['op.parent'].sudo().search([('user_id', '=', self.env.user.id)])
            domain = domain + [('parent_ids', '=', parent.id)]
            res = self.env['op.parent'].sudo().search_read(domain=domain, fields=fields, offset=offset, limit=limit, order=order)
            return res

        else:
            print("---faculty res user-----")
            parent = self.env['op.faculty'].sudo().search([('user_id', '=', self.env.user.id)])
            domain = domain + [('faculty', '=', parent.id)]
            res = self.env['op.faculty'].sudo().search_read(domain=domain, fields=fields, offset=offset, limit=limit,
                                                           order=order)
            return res



# class BaseModelExtend(models.BaseModel):
#
#     @api.model
#     def search_read_for_app(self, domain=None, fields=None, offset=0, limit=None, order=None):
#         res = super(BaseModelExtend, self).search_read(
#             domain=domain, fields=fields, offset=offset, limit=limit, order=order
#         )
#         return res
