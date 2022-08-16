# Copyright 2022 CreuBlanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Hr Skills Evaluation",
    "summary": """
        Evaluate skills of employees""",
    "version": "13.0.1.0.0",
    "license": "AGPL-3",
    "author": "CreuBlanca,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/hr",
    "depends": ["hr_skills"],
    "data": [
        "templates/assets.xml",
        "views/hr_job.xml",
        "security/ir.model.access.csv",
        "views/hr_job_evaluation.xml",
    ],
    "demo": ["demo/hr_job_evaluation.xml",],
    "qweb": ["static/src/xml/skills_templates.xml"],
}
