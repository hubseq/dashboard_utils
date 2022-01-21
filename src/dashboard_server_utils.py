#
# dashboard_server_utils
#
# General server utility functions for Plotly Dash web server instance.
#
import os
import pandas as pd

############################################################
## CONSTANTS USED BY DASHBOARDS
############################################################
STATIC_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scratch')
SCRATCH_DIR = STATIC_PATH
DASH_STYLESHEETS = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
ROOT_FOLDER = 's3://'

DASHBOARD_NAME_MAIN = 'Pipeline Data Analysis Dashboard'
DNASEQ_TARGETED_PIPELINE_ID = 'dnaseq_targeted'
DASHBOARD_ID_FASTQC = 'fastqc-dashboard'
DASHBOARD_ID_BARCODEQC = 'barcodeqc-dashboard'
DASHBOARD_ID_ALIGNMENT_PANEL = 'alignment-panel-analysis-dashboard'
DASHBOARD_ID_COVERAGE = 'coverage-analysis-dashboard'
DASHBOARD_ID_VARIANT = 'variant-analysis-dashboard'
DASHBOARD_ID_RAW = 'raw-files-dashboard'
PIPELINE_DNASEQ_TARGETED_DF = {DASHBOARD_ID_FASTQC: {},
                               DASHBOARD_ID_BARCODEQC: {},
                               DASHBOARD_ID_ALIGNMENT_PANEL: {},
                               DASHBOARD_ID_COVERAGE: {},
                               DASHBOARD_ID_VARIANT: {},
                               DASHBOARD_ID_RAW: {}}

def list2optionslist( V, L = []):
    # if extra label L is passed in, we add that to label
    D = []
    print('V: {}, L: {}'.format(str(V), str(L)))
    for i in range(0,len(V)):
        val = V[i]
        if L != []:
            lab = L[i]
            D.append({'label': '{}: {}'.format(lab, val), 'value': val})
        else:
            D.append({'label': val, 'value': val})
    return D

def selectionEmpty( field ):
    # checks if a field selection (e.g., dropdown) from dashboard is empty
    if field == None or (type(field)==type([]) and field==[]) or (type(field)==str and field=='') or \
       (type(field)==type(pd.DataFrame()) and field.empty):
        return True
    else:
        return False
