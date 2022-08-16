# Copyright 2022 CreuBlanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HrJob(models.Model):

    _inherit = "hr.job"
    skill_ids = fields.One2many("hr.job.skill", inverse_name="job_id")


class HrJobSkill(models.Model):
    _name = "hr.job.skill"
    _description = "Expected Skills on a Job"

    job_id = fields.Many2one("hr.job", required=True)
    skill_id = fields.Many2one("hr.skill", required=True)
    skill_level_id = fields.Many2one("hr.skill.level")
    skill_type_id = fields.Many2one("hr.skill.type", required=True)
    level_progress = fields.Integer(
        related="skill_level_id.level_progress", readonly=True
    )

    _sql_constraints = [
        (
            "_unique_skill",
            "unique (job_id, skill_id)",
            "Two levels for the same skill is not allowed",
        ),
    ]

    def _get_job_skill_vals(self, employee):
        return {
            "skill_id": self.skill_id.id,
            "skill_type_id": self.skill_type_id.id,
            "expected_level_id": self.skill_level_id.id,
            "skill_level_id": employee.employee_skill_ids.filtered(
                lambda r: r.skill_id == self.skill_id
            ).skill_level_id.id,
        }
