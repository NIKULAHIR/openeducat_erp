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

from odoo.exceptions import ValidationError

from odoo import models, fields, api, _


class OpAssignment(models.Model):
    _name = "op.assignment"
    _inherit = "mail.thread"
    _description = "Assignment"
    _order = "submission_date DESC"

    name = fields.Char('Name', size=64, required=True)
    course_id = fields.Many2one('op.course', 'Course', required=True)
    batch_id = fields.Many2one('op.batch', 'Batch', required=True)
    subject_id = fields.Many2one('op.subject', 'Subject', required=True)
    faculty_id = fields.Many2one(
        'op.faculty', 'Faculty', default=lambda self: self.env[
            'op.faculty'].search([('user_id', '=', self.env.uid)]),
        required=True)
    assignment_type_id = fields.Many2one(
        'op.assignment.type', 'Assignment Type', required=True)
    marks = fields.Float('Marks', required=True, track_visibility='onchange')
    description = fields.Text('Description', required=True)
    state = fields.Selection([
        ('draft', 'Draft'), ('publish', 'Published'),
        ('finish', 'Finished'), ('cancel', 'Cancel'),
    ], 'State', required=True, default='draft', track_visibility='onchange')
    issued_date = fields.Datetime(string='Issued Date', required=True,
                                  default=lambda self: fields.Datetime.now())
    submission_date = fields.Datetime('Submission Date', required=True,
                                      track_visibility='onchange')
    allocation_ids = fields.Many2many('op.student', string='Allocated To')
    assignment_sub_line = fields.One2many('op.assignment.sub.line',
                                          'assignment_id', 'Submissions')
    reviewer = fields.Many2one('op.faculty', 'Reviewer')
    attachment_ids = fields.One2many('ir.attachment', 'res_id',
                                     domain=[('res_model', '=',
                                              'op.job.applicant')],
                                     string='Attachments', readonly=True)

    @api.multi
    @api.constrains('issued_date', 'submission_date')
    def check_dates(self):
        for record in self:
            issued_date = fields.Date.from_string(record.issued_date)
            submission_date = fields.Date.from_string(record.submission_date)
            if issued_date > submission_date:
                raise ValidationError(_(
                    "Submission Date cannot be set before Issue Date."))

    @api.onchange('course_id')
    def onchange_course(self):
        self.batch_id = False
        if self.course_id:
            subject_ids = self.env['op.course'].search([
                ('id', '=', self.course_id.id)]).subject_ids
            return {'domain': {'subject_id': [('id', 'in', subject_ids.ids)]}}

    @api.multi
    def act_publish(self):
        result = self.state = 'publish'
        return result and result or False

    @api.multi
    def act_finish(self):
        result = self.state = 'finish'
        return result and result or False

    @api.multi
    def act_cancel(self):
        self.state = 'cancel'

    @api.multi
    def act_set_to_draft(self):
        self.state = 'draft'

    @api.model
    def create(self, vals):
        print("__student ____", vals)
        res = super(OpAssignment, self).create(vals)
        print("____Final created app__", res)
        return  res
    @api.model
    def search_read_for_attchment(self, domain=None, fields=None, offset=0, limit=None, order=None):
        print("____inside assinments_____")
        attachment = self.env['ir.attachment'].sudo().search([])
        print("____atatchments_", attachment)
        domain = domain + ['res_id','=', self.env.user.id]
        res = self.sudo().search_read(domain=domain, fields=self.attachment_ids, offset=offset, limit=limit,
                                      order=order)
        print("____res___for atchments__", res)
        return res


    @api.model
    def search_read_for_app(self, domain=None, fields=None, offset=0, limit=None, order=None):

        if self.env.user.partner_id.is_student:


            print("______-ASSIGNMENT_________",self.attachment_ids.search([]), domain)

            # attachment = self.env['ir.attachment'].sudo().search_read(
            #     []
            # )


            # obj = []
            partner = self.env.user.partner_id
            domain = domain + [('allocation_ids.partner_id', '=', partner.id)]

            print("____doamin--_L", domain)
            res = self.sudo().search_read(domain=domain, fields=self.attachment_ids, offset=offset, limit=limit, order=order)
            print("______-res_____", res, fields, type(res))


            # attachment_instance = self.env['ir.attachment'].sudo().search([('id','=',self.attachment_ids)])

            # for i in attachment_instance:
            #     print("\n\n   ATACHMENTS-------",i.name, i.res_model, i.url,i.type )

            return res
                # {'assignment_ids':res,
                #     'attachment': attachment_instance}
                # res
                   # attachment_instance
                # {'object':res,
                #     'attachment': attachment}



        elif self.env.user.partner_id.is_parent:
            user = self.env.user
            parent_id = self.env['op.parent'].sudo().search([('user_id', '=', user.id)])
            student_id = [student.id for student in parent_id.student_ids]
            domain = domain + [('allocation_ids', 'in', student_id)]
            res = self.sudo().search_read(domain=domain, fields=fields, offset=offset, limit=limit, order=order)
            return res
        else:
            print("____its is facult___", id,"=====")
            user = self.env.user
            print("___user__:", user)
            parent_id = self.env['op.faculty'].sudo().search([('user_id','=', user.id)])
            print("___faculty_ids:::", parent_id)
            student_id = [student.id for student in parent_id]
            print("____student_ids___:", student_id, student_id,"+++",domain)
            domain = domain
            print("____working___:", domain)
            res = self.sudo().search_read(domain=domain, fields=fields, offset=offset, limit=limit, order=order)
            return res



    # @api.model
    # def search_read_for_assignment(self, domain=None, fields=None, offset=0, limit=None, order=None):
    #     print("____is faculty")
    #     # if not [(self.env.user.partner_id.is_student),(self.env.user.partner_id.is_student)]:
    #     print("_____this is faculty___")
    #     partner = self.env.user.partner_id
    #     student_id = self.env['op.student'].sudo().search([('partner_id', '=', partner.id)])
    #     faculty_id = self.env['op.faculty'].sudo().search([('id','=',student_id.id)])
    #     domain = domain + [('allocation_ids.partner_id', '=', faculty_id.id)]
    #     print("_____workinh___:", domain)
    #     res = self.sudo().search_read(domain=domain, fields=fields, offset=offset, limit=limit, order=order)
    #     print("____-res___", res)
    #     return res


class Seach_attachment(models.Model):
    _inherit = "ir.attachment"
    _description = "select attachment"

    @api.model
    def search_read_for_app(self, domain=None, fields=None, offset=0, limit=None, order=None):
        if self.env.user.partner_id.is_student:
            print("______-ATTCHEMENTS INSID ETHE", self.attachment_ids.search([]), domain)

            # attachment = self.env['ir.attachment'].sudo().search_read(
            #     []
            # )

            # obj = []
            partner = self.env.user.partner_id
            domain = domain + []

            print("____doamin--_", domain)
            res = self.sudo().search_read(domain=domain, fields=self.attachment_ids, offset=offset, limit=limit,
                                          order=order)
            print("______-res_____", res, fields, type(res))
            return res


