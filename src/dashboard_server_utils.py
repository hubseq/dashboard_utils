#
# dashboard_server_utils
#
# General server utility functions for Plotly Dash web server instance.
#

############################################################
## CONSTANTS USED BY DASHBOARDS
############################################################
USER_SCRATCH_DIR = 'scratch'
DASH_STYLESHEETS = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

DASHBOARD_NAME_MAIN = 'Pipeline Data Analysis Dashboard'

def list2optionslist( L ):
    D = []
    for e in L:
        D.append({'label': e, 'value': e})
    return D
