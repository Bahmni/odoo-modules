# -*- coding: utf-8 -*-
{
    'name': 'Bahmni Stock',
    'version': '1.0',
    'summary': 'Custom stock module to meet bahmni requirement',
    'sequence': 1,
    'description': """
Bahmni Purchase
====================
""",
    'category': 'Stock',
    'website': '',
    'images': [],
    'depends': ['stock', 'bahmni_product', 'bahmni_account'],
    'data': ['views/purchase_views.xml',
             'views/product_view.xml',
             ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
