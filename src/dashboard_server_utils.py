#
# dashboard_server_utils
#
# General server utility functions for Plotly Dash web server instance.
#

USER_SCRATCH_DIR = 'scratch'
DASH_STYLESHEETS = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

DASHBOARD_NAME_MAIN = 'Pipeline Data Analysis Dashboard'

DASHBOARD_ID_FASTQC = 'fastqc-dashboard'
DASHBOARD_ID_BARCODEQC = 'barcodeqc-dashboard'
DASHBOARD_ID_ALIGNMENT_PANEL = 'alignment-panel-analysis-dashboard'
DASHBOARD_ID_COVERAGE = 'coverage-analysis-dashboard'
DASHBOARD_ID_VARIANT = 'variant-analysis-dashboard'
DASHBOARD_ID_RAW = 'raw-files-dashboard'

PIPELINE_LIST = ['Targeted DNA Sequencing']
PIPELINE_DNASEQ_TARGETED_DF = {DASHBOARD_ID_FASTQC: {},
                               DASHBOARD_ID_BARCODEQC: {},
                               DASHBOARD_ID_ALIGNMENT_PANEL: {},
                               DASHBOARD_ID_COVERAGE: {},
                               DASHBOARD_ID_VARIANT: {},
                               DASHBOARD_ID_RAW: {}}

def getPipelineList():
    return PIPELINE_LIST

def getAnalysisList( pipeline ):
    if pipeline == 'Targeted DNA Sequencing':
        return list(PIPELINE_DNASEQ_TARGETED_DF.keys())

def initDataframe( pipeline, sessionid ):
    dfs = PIPELINE_DNASEQ_TARGETED_DF
    for k in list(dfs.keys()):
        if k in [DASHBOARD_ID_FASTQC, DASHBOARD_ID_BARCODEQC, DASHBOARD_ID_ALIGNMENT_PANEL]:
            dfs[k][sessionid] = []
        elif k in [DASHBOARD_ID_COVERAGE, DASHBOARD_ID_VARIANT]:
            dfs[k][sessionid] = {}
        elif k in [DASHBOARD_ID_RAW]:
            dfs[k][sessionid] = {'fastq': [], 'bam': [], 'panelbam': [], 'unmappedbam': [], 'panelcounts': [], 'barcodecounts': []}
    return dfs

def list2optionslist( L ):
    D = []
    for e in L:
        D.append({'label': e, 'value': e})
    return D
