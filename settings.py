from os import environ

SESSION_CONFIGS = [
    dict(
        name='HumanvsMachine',
        display_name='Honesty in Human vs. Machine Decision-Making',
        app_sequence=['HumanvsMachine', 'payout_referral'],
        num_demo_participants=26,
    ),
]

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00,
    participation_fee=0.00,
    doc='',
)

PARTICIPANT_FIELDS = ['role', 'applicant_group']
SESSION_FIELDS     = ['selected_round', 'bonus_winners']

LANGUAGE_CODE          = 'en'
REAL_WORLD_CURRENCY_CODE = 'EUR'
USE_POINTS             = False

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

DEMO_PAGE_INTRO_HTML = ''

SECRET_KEY = environ.get('OTREE_SECRET_KEY', '5693988952124')

ROOMS = [
    dict(
        name='wulabs',
        display_name='WULABS Experiment Room',
        participant_label_file='_rooms/wulabs.txt',
        use_secure_urls=False,
    ),
]
