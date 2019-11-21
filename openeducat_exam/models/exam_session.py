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

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class OpExamSession(models.Model):
    _name = "op.exam.session"
    _inherit = ["mail.thread"]
    _description = "Exam Session"

    name = fields.Char(
        'Exam Session', size=256, required=True, track_visibility='onchange')
    course_id = fields.Many2one(
        'op.course', 'Course', required=True, track_visibility='onchange')
    batch_id = fields.Many2one(
        'op.batch', 'Batch', required=True, track_visibility='onchange')
    exam_code = fields.Char(
        'Exam Session Code', size=16,
        required=True, track_visibility='onchange')
    start_date = fields.Date(
        'Start Date', required=True, track_visibility='onchange')
    end_date = fields.Date(
        'End Date', required=True, track_visibility='onchange')
    exam_ids = fields.One2many(
        'op.exam', 'session_id', 'Exam(s)')
    exam_type = fields.Many2one(
        'op.exam.type', 'Exam Type',
        required=True, track_visibility='onchange')
    evaluation_type = fields.Selection(
        [('normal', 'Normal'), ('grade', 'Grade')],
        'Evolution type', default="normal",
        required=True, track_visibility='onchange')
    venue = fields.Many2one(
        'res.partner', 'Venue', track_visibility='onchange')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('schedule', 'Scheduled'),
        ('held', 'Held'),
        ('cancel', 'Cancelled'),
        ('done', 'Done')
    ], 'State', default='draft', track_visibility='onchange')

    _sql_constraints = [
        ('unique_exam_session_code',
         'unique(exam_code)', 'Code should be unique per exam session!')]

    @api.constrains('start_date', 'end_date')
    def _check_date_time(self):
        if self.start_date > self.end_date:
            raise ValidationError(
                _('End Date cannot be set before Start Date.'))

    @api.onchange('course_id')
    def onchange_course(self):
        self.batch_id = False

    @api.multi
    def act_draft(self):
        self.state = 'draft'

    @api.multi
    def act_schedule(self):
        self.state = 'schedule'

    @api.multi
    def act_held(self):
        self.state = 'held'

    @api.multi
    def act_done(self):
        self.state = 'done'

    @api.multi
    def act_cancel(self):
        self.state = 'cancel'

    @api.model
    def search_read_for_app(self, domain=None, fields=None, offset=0, limit=None, order=None):
        print("__session====_____--aas su che session baku____", domain)
        user = self.env.user
        student_id = self.env['op.student'].sudo().search([('user_id', '=', user.id)])
        domain = domain + [('exam_ids.attendees_line.student_id','=',student_id.id)]
        res = self.sudo().search_read(domain=domain,
                                      fields=['name', 'exam_type', 'exam_code',  'start_date',
                                              'end_date'], offset=offset, limit=limit, order=order)
        print("______-res______", res)
        return res

    @api.model
    def search_read_for_exam(self, domain=None, fields=None, offset=0, limit=None, order=None):
        print("__StUDENT_______inside the exam in future______")
        if self.env.user.partner_id.is_student:
            main_list = []
            print("__Student_______", domain)
            user = self.env.user
            student_id = self.env['op.student'].sudo().search([('user_id', '=', user.id)])
            print("__Student__id_____",student_id)
            domain = domain + [('state','!=','done')]
            print("__Domain__", domain)
            session = self.sudo().search([('state', '!=', 'done'),('state','!=','draft')])

            for record in session:
                main_dict = {}
                print("\n\m___k__", record, record.exam_ids)
                main_dict.update({
                    'id': record.id,
                    'session_name': record.name,
                    'exam_type': record.exam_type.name,
                    'start_date': record.start_date,
                    'end_date': record.end_date,
                })
                sub_list = []
                for rec in record.exam_ids:
                    sub_dict = {}
                    print("___rec__", rec, rec.id)
                    sub_dict.update({
                        'id': rec.id,
                        'session_id': rec.session_id.id,
                        'exam_name': rec.name,
                        'start_time': rec.start_time,
                        'end_time': rec.end_time,
                        'subject_name': rec.subject_id.name,
                        'status': rec.state,
                        'total_marks': rec.total_marks,
                        'passing_marks': rec.min_marks
                    })
                    min_list = []
                    for r in rec.attendees_line:
                        min_dict = {}
                        print("_____r______", r, r.student_id.name)
                        min_dict.update({'studnet_name': r.student_id.name})

                        min_list.append(min_dict)
                        sub_dict.update({'student': min_list})

                    sub_list.append(sub_dict)
                    main_dict.update({'exam': sub_list})
                main_list.append(main_dict,
                                 )

            print("\n__mian_list__", main_list)
            return main_list

        #
            # exam_id = self.sudo().search([('attendees_line.student_id', 'in', student_id)])
            # print("____exam_id__",exam_id)
            # res = self.sudo().search_read(domain=domain, fields=fields, offset=offset, limit=limit, order=order)
            # print("____Exam data__", res)
            # session = self.env['op.exam.session'].sudo().serach_read(domain=domain, fields=fields, offset=offset, limit=limit, order=order)
            # print("____Sesssion__", session)
            # return {'exam_data':res,
            #         'session_data':session}

        if self.env.user.partner_id.is_parent:
            print("_parent_______", domain)
            main_list = []

            user = self.env.user
            parent_id = self.env['op.parent'].sudo().search([('user_id', '=', user.id)])
            student_id = [student.id for student in parent_id.student_ids]

            print("__Student__id_____", student_id)
            domain = domain + [('state', '!=', 'done'),('state','!=','draft')]
            print("__Domain__", domain)

            # exam_attendance = self.env['op.exam.attendees'].sudo().search(
            #     [('student_id', 'in', student_id)])
            #
            # for i in exam_attendance:
            #     print("___in side for __studt", i.student_id.name)
            #     mian_list.append({'student':i.student_id.name})

            # exam_id = self.env['op.exam'].sudo().search([('state','!=', 'done'),('attendees_line.student_id', 'in', student_id)])
            # print("____exam_id__", exam_id)
            # for i in exam_id:
            #     print("___in side for __studt", i.attendees_line, i.name)
            #     mian_list.append({
            #         'session_id': i.session_id.id,
            #         'exam_name': i.name,
            #         'start_time': i.start_time,
            #         'end_time': i.end_time,
            #         'subject_name': i.subject_id.name,
            #         'status': i.state,
            #         'total_marks': i.total_marks,
            #         'passing_marks': i.min_marks
            #     })
            #     for j in i.attendees_line:
            #         mian_list.append({'student_name':j.student_id.name})


            # res = self.env['op.exam'].sudo().search_read(domain=[('state','!=', 'done'),('attendees_line.student_id', 'in', student_id)], fields=fields, offset=offset, limit=limit, order=order)
            # print("____Exam data__", res)
            # session = self.sudo().search_read(domain=domain, fields=['name','exam_ids','exam_type','start_date','end_date'], offset=offset,
            #                                                          limit=limit, order=order)
            session = self.sudo().search([('state', '!=', 'done')])

            for record in session:
                main_dict={}
                print("\n\m___k__", record, record.exam_ids)
                main_dict.update({
                    'id': record.id,
                    'session_name': record.name,
                    'exam_type': record.exam_type.name,
                    'start_date': record.start_date,
                    'end_date': record.end_date,
                 })
                sub_list =[]
                for rec in record.exam_ids:
                    sub_dict={}
                    print("___rec__", rec, rec.id)
                    sub_dict.update({
                        'id': rec.id,
                        'session_id': rec.session_id.id,
                        'exam_name': rec.name,
                        'start_time': rec.start_time,
                        'end_time': rec.end_time,
                        'subject_name': rec.subject_id.name,
                        'status': rec.state,
                        'total_marks': rec.total_marks,
                        'passing_marks': rec.min_marks
                    })
                    min_list = []
                    for r in rec.attendees_line:
                        min_dict = {}
                        print("_____r______", r,r.student_id.name)
                        min_dict.update({'studnet_name':r.student_id.name})

                        min_list.append(min_dict)
                        sub_dict.update({'student':min_list})

                    sub_list.append(sub_dict)
                    main_dict.update({'exam':sub_list})
                main_list.append(main_dict,
                                  )




            print("\n__mian_list__",main_list)
            return main_list


