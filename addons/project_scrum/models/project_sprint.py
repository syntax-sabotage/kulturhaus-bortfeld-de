from dateutil.relativedelta import relativedelta

from odoo import api, fields, models
from odoo.tools import LazyTranslate

_lt = LazyTranslate(__name__, default_lang="en_US")

DATE_OPTIONS = [
    ("1_weeks", str(_lt("1 Week"))),
    ("2_weeks", str(_lt("2 Weeks"))),
    ("1_months", str(_lt("1 Month"))),
    ("2_months", str(_lt("2 Month"))),
    ("1_years", str(_lt("1 Year"))),
    ("2_years", str(_lt("2 Years"))),
    ("custom", str(_lt("Custom"))),
]


class ProjectSprint(models.Model):
    _name = "project.sprint"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Project Sprint"
    _sql_constraints = [
        (
            "date_check",
            "CHECK (date_start <= date_end)",
            "Error: End date must be greater than start date!",
        ),
    ]

    name = fields.Char(required=True, tracking=True)
    user_ids = fields.Many2many(
        comodel_name="res.users",
        string="Members",
        required=True,
        domain="[('share', '=', False), ('active', '=', True)]",
        tracking=True,
        relation="project_sprint_user_rel",
    )
    description = fields.Text(tracking=True)
    project_id = fields.Many2one(
        comodel_name="project.project",
        string="Project",
        tracking=True,
    )
    task_ids = fields.One2many(
        comodel_name="project.task",
        inverse_name="sprint_id",
        string="Tasks",
        domain="[('project_id', '=', project_id)]",
    )
    date_start = fields.Date(
        string="Start Date", default=fields.Date.context_today, required=True
    )
    date_option = fields.Selection(
        selection=DATE_OPTIONS, default=DATE_OPTIONS[0][0], required=True
    )
    date_end = fields.Date(
        string="End Date",
        required=True,
        compute="_compute_date_end",
        store=True,
        readonly=False,
    )
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("in_progress", "In progress"),
            ("done", "Done"),
        ],
        default="draft",
        tracking=True,
    )
    tasks_count = fields.Integer(compute="_compute_tasks_count")

    def _compute_tasks_count(self):
        tasks_count_by_sprint = dict(
            self.env["project.task"]._read_group(
                [("sprint_id", "in", self.ids)], ["sprint_id"], ["__count"]
            )
        )
        for sprint in self:
            sprint.tasks_count = tasks_count_by_sprint.get(sprint, 0)

    def action_start(self):
        self.write({"state": "in_progress"})

    def action_done(self):
        self.write({"state": "done"})
        self._check_task_state()

    def action_tasks(self):
        self.ensure_one()
        return {
            "name": self.env._("Tasks"),
            "type": "ir.actions.act_window",
            "res_model": "project.task",
            "view_mode": "list,form",
            "domain": [("sprint_id", "=", self.id)],
            "context": {
                "default_project_id": self.project_id.id,
                "default_sprint_id": self.id,
            },
        }

    @api.model
    def cron_update_sprint_state(self):
        date = fields.Date.context_today(self)
        for sprint in self.search([("state", "=", "draft")]):
            if date >= sprint.date_start:
                sprint.write({"state": "in_progress"})

        for sprint in self.search([("state", "=", "in_progress")]):
            if date >= sprint.date_end:
                sprint.write({"state": "done"})
                sprint._check_task_state()

    def _check_task_state(self):
        self.ensure_one()
        in_progress_sprints = self.project_id.sprint_ids.filtered(
            lambda sprint: sprint.state == "in_progress"
        )
        self.task_ids.filtered(lambda task: task.state != "1_done").write(
            {
                "sprint_id": (
                    in_progress_sprints[0].id if in_progress_sprints else False
                ),
                "user_ids": False,
            }
        )

    @api.depends("date_start", "date_option")
    def _compute_date_end(self):
        for record in self:
            if record.date_option != "custom":
                num, interval = record.date_option.split("_")
                record.date_end = record.date_start + relativedelta(
                    **{interval: int(num)}
                )
            else:
                record.date_end = record.date_start + relativedelta(days=1)
