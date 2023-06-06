# -*- coding: utf-8 -*-
import current as current
import self

from odoo import models, fields, api, exceptions
from odoo.addons.test_convert.tests.test_env import record
from odoo.exceptions import ValidationError, UserError
from odoo.tools.safe_eval import time
from odoo.tools.translate import _
from datetime import date, timedelta


class MergeTasksLine(models.Model):
    _name = 'base.task.merge.line'

    min_id = fields.Integer(string='MinID', order='min_id asc')
    aggr_ids = fields.Char('Ids')
    zone = fields.Integer(string="Zone")
    zo = fields.Char(string="Zone")
    secteur = fields.Integer(string="Secteur")
    secteur_to = fields.Integer(string="Secteur")
    date_from = fields.Date(string='Wizard')
    date_to = fields.Date(string='Wizard')
    poteau_t = fields.Float('Time Spent')
    is_display = fields.Boolean(string='Ids')
    plans = fields.Char(string='Ids')
    from_int = fields.Integer(string='MinID')
    to_int = fields.Integer(string='MinID')

    wizard_id = fields.Many2one('base.task.merge.automatic.wizard', string='Wizard')
    employee_id = fields.Many2one('hr.employee', string='Wizard')
    plan_id = fields.Many2one('risk.management.response.category', string='Wizard')
    plan_id2 = fields.Many2one('risk.management.response.category', string='Wizard')
    risk_id = fields.Many2one('risk.management.category', string='Wizard')


def onchange_plan_id_(self, plan_id, plan_id2):
    result = {'value': {}}
    total = 0
    if plan_id and plan_id2:
        plan1 = self.env['risk.management.response.category'].browse(plan_id)
        plan2 = self.env['risk.management.response.category'].browse(plan_id2)
        for x in range(plan_id, plan_id2 + 1):
            plan = self.env['risk.management.response.category'].browse(x)
            if plan:
                total += plan.aerien + plan.ps + plan.souterrain + plan.double_aerien + plan.double_conduit

        result['value']['plans'] = plan1.plan + '-' + plan2.plan
        return result


def onchange_plans(self, plans):
    result = {'value': {}}
    total = 0
    count = 0
    if plans:
        if plans.count('-') > 1:
            # Replace the osv.except_osv calls with raise ValidationError to raise validation errors.
            raise ValidationError(_('Erreur !'),
                                  _('Format Incorrecte!, un seul tiret est autorisé!'))
        elif plans.count('-') == 1 and plans.count(';') == 0:

            # Replace the self.pool.get calls with self.env['model_name'].search to search for records from the respective models.
            # Update the usage of the search method by passing the search criteria directly as arguments.

            tt = self.env['risk.management.response.category'].search([('plan', '=', plans.split('-')[0])])
            tt1 = self.env['risk.management.response.category'].search([('plan', '=', plans.split('-')[1])])
            if not tt:
                raise ValidationError(_('Erreur !'), _('Element n"est pas dans le tableau de relevé!'))
            else:
                t1 = tt[0]
            if not tt1:
                raise ValidationError(_('Erreur !'), _('Element n"est pas dans le tableau de relevé!'))
            else:
                t2 = tt1[0]
            for x in range(t1, t2):

                # Update the self.pool.get('risk.management.response.category').browse calls to use self.env['risk.management.response.category'].browse to retrieve records.

                plan = self.env['risk.management.response.category'].browse(x)
                if plan:
                    total += plan.aerien + plan.ps + plan.souterrain + plan.double_aerien + plan.double_conduit
        elif plans.count('-') == 1 and plans.count(';') > 0:
            tt = self.env['risk.management.response.category'].search(
                [('plan', '=', (plans.split(';')[0]).split('-')[0])])
            tt1 = self.env['risk.management.response.category'].search(
                [('plan', '=', (plans.split(';')[0]).split('-')[1])])
            if not tt:
                raise ValidationError(_('Erreur !'), _('Element n"est pas dans le tableau de relevé!'))
            else:
                t1 = tt[0]
            if not tt1:
                raise ValidationError(_('Erreur !'), _('Element n"est pas dans le tableau de relevé!'))
            else:
                t2 = tt1[0]
            for x in range(t1, t2):
                plan = self.env['risk.management.response.category'].browse(x)
                if plan:
                    # Replace the list variable name with lst as list is a reserved keyword in Python.

                    total += plan.aerien + plan.ps + plan.souterrain + plan.double_aerien + plan.double_conduit
                lst = (plans.split(';')[1]).split(';')
                for kk in lst:
                    tt2 = self.env['risk.management.response.category'].search([('plan', '=', kk)])
                    if not tt2:
                        raise ValidationError(_('Erreur !'), _('Element n"est pas dans le tableau de relevé!'))
                    else:
                        plan = self.env['risk.management.response.category'].browse(tt2[0])
                    if plan:
                        total += plan.aerien + plan.ps + plan.souterrain + plan.double_aerien + plan.double_conduit
        elif plans.count('-') == 0 and plans.count(';') > 0:
            lst = plans.split(';')
            for kk in lst:
                for kk in lst:
                    tt2 = self.env['risk.management.response.category'].search([('plan', '=', kk)])
                    if not tt2:
                        raise ValidationError(_('Erreur !'), _('Element n"est pas dans le tableau de relevé!'))
                    else:
                        plan = self.env['risk.management.response.category'].browse(tt2[0])
                    if plan:
                        total += plan.aerien + plan.ps + plan.souterrain + plan.double_aerien + plan.double_conduit
        else:
            raise ValidationError(_('Erreur !'),
                                  _('Format Incorrecte!, seuls les tirets "-" ou les points virgules ";" sont autorisés!'))

    result['value']['poteau_t'] = total / 1000
    return result


class EbMergeTasks(models.Model):
    _name = 'base.task.merge.automatic.wizard'
    _description = 'Merge Tasks'

    name = fields.Char(string='Name')

    def name_get(self):
        result = []
        for record in self:
            name = record.name  # Replace 'name' with the field you want to use as the record name
            result.append((record.id, name))
        return result

    @api.model
    def default_get(self, fields_list):
        res = super(EbMergeTasks, self).default_get(fields_list)
        #  I've updated the method signature to use fields_list. Additionally,
        #  I've replaced res['task_ids'] = active_ids with res.update({'task_ids': active_ids})
        #  to ensure the correct behavior in case there are other existing values in the dictionary.
        active_ids = self.env.context.get('active_ids')
        if self.env.context.get('active_model') == 'project.task' and active_ids:
            res.update({'task_ids': active_ids})
        return res

    @api.depends('project_id.user_id')
    def _compute_disponible(self):
        for book in self:
            if book.project_id.user_id.id == self.env.user.id:
                book.disponible = True
            else:
                book.disponible = False

    disponible = fields.Boolean(compute='_compute_disponible', string='Disponible')

    date_from = fields.Date(string='Wizard')
    date_to = fields.Date(string='Wizard')
    project_id = fields.Many2one('project.project', string='Wizard')
    partner_id = fields.Many2one('res.partner', string='wizard')
    task_id = fields.Many2one('project.task', string='Wizard')
    work_id = fields.Many2one('project.task.work', string='Wizard')
    product_id = fields.Many2one('product.product', string='Wizard')

    class ProjectTaskWork(models.Model):
        _name = 'project.task.work'

    choix = fields.Selection([
        ('1', 'Garder Les Taches Sources Actives'),
        ('2', 'Archiver les Taches Sources')

    ],

        string='Priority', select=True)

    type = fields.Selection([
        ('1', 'Nouvelle Subdivision'),
        ('2', 'Modification Subdivision Existante'),
        ('3', 'Ajouter Subdivision A Partir d"une Existante')
    ], string='Type', select=True)

    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('open', 'Validé')
    ], string='Priority', default='draft', select=True)

    week_no = fields.Selection([
        ('00', '00'),
        ('01', '01'),
        ('02', '02'),
        ('03', '03'),
        ('04', '04'),
        ('05', '05'),
        ('06', '06'),
        ('07', '07'),
        ('08', '08'),
        ('09', '09'),
        ('10', '10'),
        ('11', '11'),
        ('12', '12'),
        ('13', '13'),
        ('14', '14'),
        ('15', '15'),
        ('16', '16'),
        ('17', '17'),
        ('18', '18'),
        ('19', '19'),
        ('20', '20'),
        ('21', '21'),
        ('22', '22'),
        ('23', '23'),
        ('24', '24'),
        ('25', '25'),
        ('26', '26'),
        ('27', '27'),
        ('28', '28'),
        ('29', '29'),
        ('30', '30'),
        ('31', '31'),
        ('32', '32'),
        ('33', '33'),
        ('34', '34'),
        ('35', '35'),
        ('36', '36'),
        ('37', '37'),
        ('38', '38'),
        ('39', '39'),
        ('40', '40'),
        ('41', '41'),
        ('42', '42'),
        ('43', '43'),
        ('44', '44'),
        ('45', '45'),
        ('46', '46'),
        ('47', '47'),
        ('48', '48'),
        ('49', '49'),
        ('50', '50'),
        ('51', '51'),
        ('52', '52')
    ], string='Priority', select=True, default=lambda self: str(time.strftime('%W')))

    exist = fields.Boolean(string='Ids', default=True)
    year_no = fields.Char(string='Priority', default=lambda self: str(time.strftime('%Y')))
    is_kit = fields.Boolean(string="Email")
    task_ids = fields.Many2many('project.task', string='Tasks')
    work_ids = fields.Many2many('project.task.work', string='Tasks')
    user_id = fields.Many2one('res.users', string='Assigned to')
    dst_task_id = fields.Many2one('project.task', string='Destination Task')
    dst_project = fields.Many2one('project.project', string='Project')
    line_ids = fields.One2many('base.task.merge.line', 'wizard_id', string='Role Lines', copy=True)
    line_ids1 = fields.One2many('base.group.merge.line2', 'wiz_id', string='Role Lines', copy=True)
    line_ids2 = fields.One2many('task_line.show.line2', 'wizard_id', string='Role Lines', copy=True)

    zone = fields.Integer(string='Zone')
    secteur = fields.Integer(string='Secteur')

    keep = fields.Selection([
        ('active', 'Actives'),
        ('inactive', 'Archivées'),
        ('both', 'Actives et Archivées')
    ], string='Keep', default='active')


class BaseGroupMergeLine2(models.Model):
    _name = 'base.group.merge.line2'
    wiz_id = fields.Many2one('base.task.merge.automatic.wizard', string='Wizard', inverse_name='line_ids1')


class TaskLineShowLine2(models.Model):
    _name = 'task_line.show.line2'
    wizard_id = fields.Many2one('task_line.show.line2', string="wizard", inverse_name='line_ids2')

    def action_merge(self):
        names = []

        if self.dst_task_id:
            names.append(self.dst_task_id.name)
        else:
            raise UserError(_('You must select a Destination Task'))

        desc = []

        desc.append(self.dst_task_id.description)
        for record in self.task_ids:
            if record.id != self.dst_task_id.id:
                names.append(record.name)
                desc.append(record.description)

        for message in self.task_ids:
            for msg_id in message.message_ids:
                msg_id.res_id = self.dst_task_id.id

        plan_hours = self.dst_task_id.planned_hours
        for hour in self.task_ids:
            for time in hour.timesheet_ids:
                plan_hours += time.planned_hours

        self.dst_task_id.planned_hours = plan_hours

        transformed_names = ', '.join(names)
        self.dst_task_id.name = transformed_names

        transformed_desc = ', '.join(desc)
        self.dst_task_id.description = transformed_desc

        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')

        for task in self.task_ids:
            task.message_post(
                body=f"This task has been merged into: {base_url}/web#id={self.dst_task_id.id}&model=project.task")

        self.task_ids.active = False
        self.dst_task_id.active = True

        if self.user_id:
            self.dst_task_id.user_id = self.user_id
        elif self.dst_task_id.user_id:
            self.dst_task_id.user_id = self.dst_task_id.user_id
        else:
            raise UserError(
                _('There is no user assigned to the merged task, and the destination task does not have an assigned user!'))

        return True

    @api.onchange('year_no', 'week_no')
    # The method is now decorated with @api.onchange instead of being a separate method.
    def onchange_week_(self):
        # The result variable is no longer used since the method directly assigns values to the fields.
        if self.year_no and self.week_no:  # The method now uses the self parameter to access the field values.
            d = date(self.year_no, 1, 1)
            # The date object is created using date(self.year_no, 1, 1) instead of date(int(year_no), 1, 1).
            if d.weekday() <= 3:
                d = d - timedelta(d.weekday())
                # The timedelta class is imported separately with from datetime import timedelta.
            else:
                d = d + timedelta(7 - d.weekday())
            dlt = timedelta(days=(int(self.week_no) - 1) * 7)

            self.date_from = d + dlt
            self.date_to = d + dlt + timedelta(days=6)

    @api.onchange('project_id')
    def onchange_project_id(self):

        if self.project_id:
            self.task_ids = False
            self.work_ids = False

        return {'value': {}}

    @api.onchange('exist')
    def onchange_exist(self):
        if not self.exists:
            raise exceptions.UserError(_('Attention!'),
                                       _("Si vous décocher cette option, le système ne vérifiera pas l'existence du Project-Zone-Secteur!"))
        return True

    @api.model
    def action_copy1(self, default=None):

        return super().copy(default)

    def action_copy(self, default=None):
        if default is None:
            default = {}

        for current in self:
            for tt in current.task_ids:

                packaging_obj = self.env['project.task']

                if current.zone == 0 and current.secteur == 0:
                    cte = self.env['project.task.work'].create({
                        'task_id': tt.id,
                        'product_id': tt.product_id.id,
                        'name': tt.name,
                        'date_start': tt.date_start,
                        'date_end': tt.date_end,
                        'poteau_t': tt.qte,
                        'color': tt.color,
                        'total_t': tt.color * 7,
                        'project_id': tt.project_id.id,
                        'gest_id': tt.reviewer_id.id or False,
                        'uom_id': tt.uom_id.id,
                        'uom_id_r': tt.uom_id.id,
                        'ftp': tt.ftp,
                        'zone': tt.zone,
                        'secteur': tt.secteur,
                        'state': 'draft',
                        'priority': tt.priority,
                    })

                elif current.zone > 0 and current.secteur == 0:
                    for cc in range(1, current.zone + 1):
                        cte = self.env['project.task.work'].create({
                            'task_id': tt.id,
                            'product_id': tt.product_id.id,
                            'name': tt.name + ' Zone ' + str(cc),
                            'date_start': tt.date_start,
                            'date_end': tt.date_end,
                            'poteau_t': tt.qte,
                            'color': tt.color,
                            'total_t': tt.color * 7,
                            'project_id': tt.project_id.id,
                            'gest_id': tt.reviewer_id.id or False,
                            'uom_id': tt.uom_id.id,
                            'uom_id_r': tt.uom_id.id,
                            'ftp': tt.ftp,
                            'zone': cc,
                            'secteur': 0,
                            'state': 'draft',
                            'priority': tt.priority,
                        })

                elif current.zone > 0 and current.secteur > 0:
                    for cc in range(1, current.zone + 1):
                        for cc1 in range(1, current.secteur + 1):
                            cte = self.env['project.task.work'].create({
                                'task_id': tt.id,
                                'product_id': tt.product_id.id,
                                'name': tt.name + ' Zone ' + str(cc) + ' Secteur ' + str(cc1),
                                'date_start': tt.date_start,
                                'date_end': tt.date_end,
                                'poteau_t': tt.qte,
                                'color': tt.color,
                                'total_t': tt.color * 7,
                                'project_id': tt.project_id.id,
                                'gest_id': tt.reviewer_id.id or False,
                                'uom_id': tt.uom_id.id,
                                'uom_id_r': tt.uom_id.id,
                                'ftp': tt.ftp,
                                'zone': cc,
                                'secteur': cc1,
                                'priority': tt.priority,
                                'state': 'draft',
                            })

        return cte

    def show_results(self):
        current = self[0]

        self.env['base.group.merge.line2'].sudo().search([('wiz_id', '=', current.id)]).unlink()

        res_cpt = []
        result_list = []

        if current.project_id:
            if current.type == '1':
                if not current.task_ids:
                    raise UserError(_("Action impossible! Vous devez sélectionner les étapes/kits concernées!"))
                if not current.line_ids:
                    raise UserError(_("Action impossible! Vous devez Mentionner les Zones et Secteurs!"))

                kit_ids = []
                task_names = []
                for task in current.task_ids:
                    if task.kit_id:
                        kit_ids.append(task.kit_id.id)
                    else:
                        task_names.append(task.name)

                if kit_ids:
                    project_tasks = self.env['project.task.work'].sudo().search([
                        ('project_id', '=', current.project_id.id),
                        ('state', 'in', ['draft', 'affect']),
                        ('kit_id', 'in', kit_ids),
                        ('active', '=', True),
                        ('is_copy', '=', False)
                    ])
                else:
                    project_tasks = self.env['project.task.work'].sudo().search([
                        ('project_id', '=', current.project_id.id),
                        ('state', 'in', ['draft', 'affect']),
                        ('etape', 'in', task_names)
                    ])

                if not project_tasks:
                    raise UserError(_("Action impossible! Merci de sauvegarder le document avant!"))

                res_cpt = project_tasks.ids

            elif current.type == '2':
                kit_ids = []
                task_names = []
                for task in current.task_ids:
                    if task.kit_id:
                        kit_ids.append(task.kit_id.id)
                    else:
                        task_names.append(task.name)

                if kit_ids:
                    project_tasks = self.env['project.task.work'].sudo().search([
                        ('project_id', '=', current.project_id.id),
                        ('kit_id', 'in', kit_ids),
                        ('active', '=', True),
                        ('zone', '=', current.zone),
                        ('secteur', '=', current.secteur)
                    ])
                else:
                    project_tasks = self.env['project.task.work'].sudo().search([
                        ('project_id', '=', current.project_id.id),
                        ('active', '=', True),
                        ('zone', '=', current.zone),
                        ('secteur', '=', current.secteur),
                        ('etape', 'in', task_names)
                    ])

                if not project_tasks:
                    raise UserError(_("Action impossible! Merci de sauvegarder le document avant!"))

                res_cpt = project_tasks.ids

            for task_id in res_cpt:
                if task_id:
                    task = self.env['project.task.work'].sudo().browse(task_id)
                    sequence_w = 0
                    if task.task_id:
                        sequence_w = task.task_id.sequence or 0

                    for line in current.line_ids:
                        if line.secteur > line.secteur_to:
                            raise UserError(
                                _("Action impossible! Le secteur de départ doit être plus petit que le secteur de fin!"))

                        if line.zone == 0 and line.secteur > 0:
                            for hh in range(line.secteur, line.secteur_to + 1):
                                employee = line.employee_id.id or task.employee_id.id or False
                                date_from = line.date_from or task.date_start
                                date_to = line.date_to or task.date_end
                                poteau_t = line.poteau_t or task.poteau_t
                                is_display = line.is_display

                                self.env['base.group.merge.line2'].sudo().create({
                                    'task_id': task.task_id.id,
                                    'categ_id': task.categ_id.id,
                                    'product_id': task.product_id.id,
                                    'name': task.name.replace(' - Secteur ' + str(task.secteur),
                                                              '') + ' - Secteur ' + str(hh),
                                    'date_start': date_from,
                                    'date_end': date_to,
                                    'poteau_i': task.poteau_t,
                                    'poteau_t': poteau_t,
                                    'color': task.color,
                                    'total_t': task.total_t,
                                    'project_id': task.project_id.id,
                                    'etape': task.etape,
                                    'bon_id': current.id,
                                    'gest_id': task.gest_id.id or False,
                                    'employee_id': employee,
                                    'uom_id': task.uom_id.id,
                                    'uom_id_r': task.uom_id.id,
                                    'ftp': task.ftp,
                                    'state': task.state,
                                    'work_id': task.id,
                                    'sequence': sequence_w + 1,
                                    'zone': 0,
                                    'zo': str(line.zone),
                                    'secteur': hh,
                                    'wiz_id': current.id,
                                    'is_display': is_display
                                })

                        elif line.zone > 0 and line.secteur > 0:
                            for hh in range(line.zone, line.zone + 1):
                                for vv in range(line.secteur, line.secteur_to + 1):
                                    employee = line.employee_id.id or task.employee_id.id or False
                                    date_from = line.date_from or task.date_start
                                    date_to = line.date_to or task.date_end
                                    poteau_t = line.poteau_t or task.poteau_t
                                    is_display = line.is_display
                                    sequence_w += 1

                                    self.env['base.group.merge.line2'].sudo().create({
                                        'task_id': task.task_id.id,
                                        'categ_id': task.categ_id.id,
                                        'product_id': task.product_id.id,
                                        'name': task.name.replace(' - Secteur ' + str(task.secteur),
                                                                  '') + ' - Zone ' + str(hh) + ' - Secteur ' + str(vv),
                                        'date_start': date_from,
                                        'date_end': date_to,
                                        'poteau_i': task.poteau_t,
                                        'poteau_t': poteau_t,
                                        'color': task.color,
                                        'total_t': task.total_t,
                                        'project_id': task.project_id.id,
                                        'bon_id': current.id,
                                        'gest_id': task.gest_id.id or False,
                                        'employee_id': employee,
                                        'uom_id': task.uom_id.id,
                                        'uom_id_r': task.uom_id.id,
                                        'ftp': task.ftp,
                                        'state': task.state,
                                        'work_id': task.id,
                                        'zone': hh,
                                        'secteur': vv,
                                        'wiz_id': current.id,
                                        'sequence': sequence_w,
                                        'etape': task.etape,
                                        'zo': str(hh),
                                        'is_display': is_display
                                    })

                        elif line.zone > 0 and line.secteur == 0:
                            for hh in range(line.zone, line.zone + 1):
                                employee = line.employee_id.id or task.employee_id.id or False
                                date_from = line.date_from or task.date_start
                                date_to = line.date_to or task.date_end
                                poteau_t = line.poteau_t or task.poteau_t
                                is_display = line.is_display
                                sequence_w += 1

                                self.env['base.group.merge.line2'].sudo().create({
                                    'task_id': task.task_id.id,
                                    'categ_id': task.categ_id.id,
                                    'product_id': task.product_id.id,
                                    'name': task.name + ' - Zone ' + str(hh),
                                    'date_start': date_from,
                                    'date_end': date_to,
                                    'poteau_i': task.poteau_t,
                                    'poteau_t': poteau_t,
                                    'color': task.color,
                                    'total_t': task.total_t,
                                    'project_id': task.project_id.id,
                                    'bon_id': current.id,
                                    'gest_id': task.gest_id.id or False,
                                    'employee_id': employee,
                                    'uom_id': task.uom_id.id,
                                    'uom_id_r': task.uom_id.id,
                                    'ftp': task.ftp,
                                    'state': task.state,
                                    'work_id': task.id,
                                    'zone': hh,
                                    'zo': str(line.hh),
                                    'secteur': 0,
                                    'wiz_id': current.id,
                                    'sequence': sequence_w,
                                    'etape': task.etape,
                                    'is_display': is_display
                                })

            return True

        @api.onchange('project_id', 'task_ids')
        def onchange_project_id(self):
            ltask1 = []
            ltask2 = []
            zz = []

            if self.project_id:
                tt = self.env['project.task'].search([('project_id', '=', self.project_id.id)], order='sequence asc')

                for task in tt:
                    if self.project_id.is_kit and task.kit_id.id not in ltask1:
                        ltask1.append(task.kit_id.id)
                        ltask2.append(task.id)
                    elif 'Etap' in task.product_id.name and task.product_id.name not in ltask1:
                        ltask1.append(task.product_id.name)
                        ltask2.append(task.id)

                zz = self.env['project.task'].search([('id', 'in', ltask2)], order='sequence asc')

            return {'domain': {'task_ids': [('id', 'in', zz.ids)]}}

        @api.onchange('project_id', 'task_ids', 'zone', 'secteur', 'keep', 'type')
        def onchange_categ_id(self):
            list_ = []
            list1 = []
            list2 = []
            ltask1 = []
            ltask2 = []

            task_work = self.env['project.task.work']

            if self.type == '1':
                is_kit = False

                if self.task_ids:
                    for kk in self.task_ids.ids:
                        task = self.env['project.task'].browse(kk)

                        if task.kit_id:
                            is_kit = True
                            for jj in task.work_ids.ids:
                                work = task_work.browse(jj)

                                if work.kit_id.id not in list1:
                                    list1.append(work.kit_id.id)
                                    list2.append(work.id)
                        else:
                            list_.append(task.product_id.name)

                    if is_kit:
                        tt = self.env['project.task.work'].search([('id', 'in', list2)], order='sequence asc')
                    else:
                        tt = self.env['project.task.work'].search([
                            ('project_id', '=', self.project_id.id),
                            ('etape', 'in', list_),
                            ('is_copy', '=', False),
                            ('zone', '=', 0),
                            ('secteur', '=', 0),
                            '|', ('active', '=', True), ('active', '=', False)
                        ], order='sequence asc')
                else:
                    if self.project_id:
                        tt = self.env['project.task.work'].search([
                            ('project_id', '=', self.project_id.id),
                            ('is_copy', '=', False),
                            ('kit_id', '=', False),
                            ('zone', '=', 0),
                            ('secteur', '=', 0),
                            '|', ('active', '=', True), ('active', '=', False)
                        ], order='sequence asc')

                        if not tt:
                            for task in tt:
                                work = task_work.browse(task.id)

                                if work.kit_id:
                                    if work.kit_id.id not in list1:
                                        list1.append(work.id)

                            tt = self.env['project.task.work'].search([('id', 'in', list1)], order='sequence asc')

            else:
                if self.keep == 'active':
                    if self.task_ids:
                        for kk in self.task_ids.ids:
                            task = self.env['project.task'].browse(kk)
                            list_.append(task.product_id.name)

                        tt = self.env['project.task.work'].search([
                            ('project_id', '=', self.project_id.id),
                            ('etape', 'in', list_),
                            ('is_copy', '=', False),
                            ('active', '=', True),
                            ('secteur', '=', self.secteur)
                        ], order='sequence asc')
                    else:
                        if self.project_id:
                            tt = self.env['project.task.work'].search([
                                ('project_id', '=', self.project_id.id),
                                ('is_copy', '=', False),
                                ('active', '=', True),
                                ('secteur', '=', self.secteur)
                            ], order='sequence asc')

                elif self.keep == 'inactive':
                    if self.task_ids:
                        for kk in self.task_ids.ids:
                            task = self.env['project.task'].browse(kk)
                            list_.append(task.product_id.name)

                        tt = self.env['project.task.work'].search([
                            ('project_id', '=', self.project_id.id),
                            ('etape', 'in', list_),
                            ('is_copy', '=', False),
                            ('active', '=', False),
                            ('secteur', '=', self.secteur)
                        ], order='sequence asc')
                    else:
                        if self.project_id:
                            tt = self.env['project.task.work'].search([
                                ('project_id', '=', self.project_id.id),
                                ('is_copy', '=', False),
                                ('active', '=', False),
                                ('secteur', '=', self.secteur)
                            ], order='sequence asc')

                elif self.keep == 'both':
                    if self.task_ids:
                        for kk in self.task_ids.ids:
                            task = self.env['project.task'].browse(kk)
                            list_.append(task.product_id.name)

                        tt = self.env['project.task.work'].search([
                            ('project_id', '=', self.project_id.id),
                            ('etape', 'in', list_),
                            ('is_copy', '=', False),
                            ('secteur', '=', self.secteur),
                            '|', ('active', '=', True), ('active', '=', False)
                        ], order='sequence asc')
                    else:
                        if self.project_id:
                            tt = self.env['project.task.work'].search([
                                ('project_id', '=', self.project_id.id),
                                ('is_copy', '=', False),
                                ('secteur', '=', self.secteur),
                                '|', ('active', '=', True), ('active', '=', False)
                            ], order='sequence asc')

            return {'domain': {'work_ids': [('id', 'in', tt.ids)]}}


