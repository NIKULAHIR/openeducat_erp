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


class OpMarksheetLine(models.Model):
    _name = "op.marksheet.line"
    _rec_name = "student_id"
    _description = "Marksheet Line"

    marksheet_reg_id = fields.Many2one(
        'op.marksheet.register', 'Marksheet Register')
    evaluation_type = fields.Selection(
        related='marksheet_reg_id.exam_session_id.evaluation_type',
        store=True)
    student_id = fields.Many2one('op.student', 'Student', required=True)
    result_line = fields.One2many(
        'op.result.line', 'marksheet_line_id', 'Results')
    total_marks = fields.Integer("Total Marks",
                                 compute='_compute_total_marks',
                                 store=True)
    percentage = fields.Float("Percentage", compute='_compute_percentage',
                              store=True)
    generated_date = fields.Date(
        'Generated Date', required=True,
        default=fields.Date.today(), track_visibility='onchange')
    grade = fields.Char('Grade', readonly=True, compute='_compute_grade')
    status = fields.Selection([
        ('pass', 'Pass'),
        ('fail', 'Fail')
    ], 'Status', compute='_compute_status')

    @api.constrains('total_marks', 'percentage')
    def _check_marks(self):
        if (self.total_marks < 0.0) or (self.percentage < 0.0):
            raise ValidationError(_("Enter proper marks or percentage!"))

    @api.multi
    @api.depends('result_line.marks')
    def _compute_total_marks(self):
        for record in self:
            record.total_marks = sum([
                int(x.marks) for x in record.result_line])

    @api.multi
    @api.depends('total_marks')
    def _compute_percentage(self):
        for record in self:
            total_exam_marks = sum(
                [int(x.exam_id.total_marks) for x in record.result_line])
            record.percentage = record.total_marks and (
                    100 * record.total_marks) / total_exam_marks or 0.0

    @api.multi
    @api.depends('percentage')
    def _compute_grade(self):
        for record in self:
            if record.evaluation_type == 'grade':
                grades = record.marksheet_reg_id.result_template_id.grade_ids
                for grade in grades:
                    if grade.min_per <= record.percentage and \
                            grade.max_per >= record.percentage:
                        record.grade = grade.result

    @api.multi
    @api.depends('result_line.status')
    def _compute_status(self):
        for record in self:
            record.status = 'pass'
            for result in record.result_line:
                if result.status == 'fail':
                    record.status = 'fail'

    @api.model
    def search_read_for_app(self, domain=None, fields=None, offset=0, limit=None, order=None):

        if self.env.user.partner_id.is_student:
            print("___-inside studnet MArkshhet line", domain, self.id)
            user = self.env.user
            student_id = self.env['op.student'].sudo().search([('user_id', '=', user.id)])
            print("___student__", student_id)
            exam_id = self.env['op.exam'].sudo().search([('attendees_line.student_id','=',student_id.id)])
            exam_ids = [rec.id for rec in exam_id]
            print("___exam idd__", exam_ids)
            domain = domain + ([('student_id','=', student_id.id)])
            print("____domain___", domain)
            res = self.sudo().search_read(domain=domain, fields=fields, offset=offset, limit=limit, order=order)
            # res_result = self.env['op.result.line'].sudo().search([('student_id','=', student_id.id)])

            print("\n___111111_res___", res, type(res),)

            #
            # exam = self.env['op.exam'].sudo().search_read(
            #     domain=[('attendees_line.student_id', '=', student_id.id)],
            #     fields=[ 'name', 'subject_id', 'total_marks', 'id'],
            #     offset=offset,
            #     limit=limit,
            #     order=order)

            exam_session = self.env['op.exam.session'].sudo().search_read(
                domain=[('exam_ids.attendees_line.student_id','=',exam_ids)],
                fields=['name','exam_ids','exam_type','start_date', 'end_date'],
                offset=offset,
                limit=limit, order=order)

            # print("\n____exam___", exam)
            print("\n__studnet_session_data__", exam_session)
            return res
            # {
            #     'local': res,
            #     'session': exam_session
            # }
            # {'first':res,
            #     'second': rtn,
            #     'third': list}

            #
            # print("___exam_id__", exam_id)
            # main_list = []
            # for rec in exam_id:
            #     print("_____name__", rec.name, rec.id, rec.session_id.name,"\n total matk____", rec.total_marks,
            #           "\n stst time", rec.start_time, "-To-",  rec.end_time)
            #
            #     exam_session_id = self.env['op.exam.session'].sudo().search([('id','=', rec.session_id.id)])
            #     main_list.append({'exam_name':rec.name,
            #                       'total_marks': rec.total_marks,
            #                       'start_time': rec.start_time,
            #                       'end_time': rec.end_time})
            #
            # print("____session__", exam_session_id)
            # for i in exam_session_id:
            #     print(i.name, i.exam_type.name)
            #     main_list.append({'session_name':i.name})
            #     for j in i.exam_ids:
            #         print("_-subject__",j.subject_id.name, j.subject_id)
            #         main_list.append({'subject': j.subject_id.name})
            # student_id = [student.id for student in student_id]
            # print("_____ mian_list__", main_list)
            # print("\n\n]n____-rtn____print",rtn)
            # .append({'exam_session_ids':rtn,
            #             'exam_ids': rth})


            # list = []
            # for rec in exam_id:
            #
            #     new = self.env['op.exam.session'].sudo().search_read(domain=[('id','=', rec.session_id.id)],
            #                                              fields=['exam_type','id'], offset=offset,
            #                                              limit=limit, order=order)
            #     list.append(new)


        if self.env.user.partner_id.is_parent:
            print("_PARENT--For the marksheet line__", domain)

            user = self.env.user
            parent_id = self.env['op.parent'].sudo().search([('user_id', '=', user.id)])
            student_id = [student.id for student in parent_id.student_ids]
            domain = domain + [('student_id', 'in', student_id)]
            print("p_____dimain__", domain)
            res = self.sudo().search_read(domain=domain, fields=fields, offset=offset, limit=limit, order=order)
            print("\np_____res___", res)

            exam_session_id = self.env['op.exam.session'].sudo().search([('exam_ids.attendees_line.student_id', 'in', student_id)])
            exam_session_ids = [rec.id for rec in exam_session_id]
            # exam_code=[]
            # for i in exam_session_id:
            #     print("__======__--exam sesson_obj", i, i.name, i.exam_type,)
            #     for j in i.exam_ids:
            #         print("_+++++_", j,j.subject_id,j.exam_code)
            #         exam_code.append(j.exam_code)
            # print("__-exam_code__", exam_code)


            exam_obj =  self.env['op.exam'].sudo().search([('session_id','in',exam_session_ids)])
            exam_ids = [rec.id for rec in exam_obj]
            print("______exam_obj___", exam_obj,"-->",exam_ids)

            exam_session = self.env['op.exam.session'].sudo().search_read(
                domain=[('exam_ids.attendees_line.student_id', 'in', student_id)],
                fields=['name', 'exam_ids','id' 'exam_type', 'start_date', 'end_date'],
                offset=offset,
                limit=limit, order=order)

            exam = self.env['op.exam'].sudo().search_read(
                domain=[('session_id','in',exam_session_ids)],
                fields=['name', 'subject_id', 'session_id','total_marks', 'id', 'exam_code'],
                offset=offset,
                limit=limit,
                order=order)
            print("\n p____exam__", exam,)



            print("\n_p____exam session___", exam_session,)
            return res
            # {'local':res,
            #         'exam': exam,
            #         'session': exam_session,
            # }
                    # 'exam': exam,
                    # 'session_exam_code': exam_code,
                    # 'session': exam_session}
