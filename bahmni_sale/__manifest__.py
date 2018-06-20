# -*- coding: utf-8 -*-
{
    'name': 'Bahmni Sale',
    'version': '1.0',
    'summary': 'Custom Sales module to meet bahmni requirement',
    'sequence': 1,
    'description': """
Bahmni Sale
====================
""",
    'category': 'Sales',
    'website': '',
    'images': [],
    'depends': ['sale', 'sale_stock', 'bahmni_account'],
    'data': ['security/security_groups.xml',
             'views/bahmni_sale.xml',
#              'views/price_markup_table_view.xml',
             'views/village_master_view.xml',
             'views/sale_order_views.xml',
             'views/sale_config_settings.xml'],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
