# -*- coding: utf-8 -*-
{
    'name': 'Bahmni Web Extension',
    'version': '1.0',
    'summary': 'Changes in web modules, as per bahmni requirement',
    'sequence': 1,
    'description': """
Bahmni Web Extension
====================
""",
    'category': 'Web',
    'website': '',
    'images': [],
    'depends': ['web'],
    'data': ['views/web_templates.xml'],
    'demo': [],
    'qweb': ['static/src/xml/*.xml'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
