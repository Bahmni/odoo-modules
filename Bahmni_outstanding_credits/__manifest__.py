{
    'name': 'Account Invoice Outstanding',
    'version': '12.0',
    'summary': 'Account Invoice Outstanding',
    'description': "",
    'author': 'random',
    'category': 'account',
    'sequence' : 1,
    'depends': ['base','bahmni_account'],
    'data': [
        'security/ir.model.access.csv',
        'views/account_invoice.xml',

    ],
    'demo': [],
    'images': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'qweb':[],
}
