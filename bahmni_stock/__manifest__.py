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
    'data': ['views/stock_production_lot_view.xml',
#              'report/batch_stock_future_forecast_view.xml',
#              'security/ir.model.access.csv'
             ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
