#
# dashboard_plots_main
#
# Render and callback functions for main dashboard
#
import sys, os, csv, uuid
import dash
from dash import dash_table
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
import pandas as pd
import flask
import dashboard_file_utils as dfu
import dashboard_plot_utils as dpu
import dashboard_server_utils as dsu
sys.path.append('global_utils/src/')
import file_utils

def initDataframe( pipeline, sessionid ):
    print('in initDataframe()')
    dfs = {}
    if pipeline == dsu.DNASEQ_TARGETED_PIPELINE_ID:
        dfs = dsu.PIPELINE_DNASEQ_TARGETED_DF
        for k in list(dfs.keys()):
            if k in [dsu.DASHBOARD_ID_FASTQC, dsu.DASHBOARD_ID_BARCODEQC, dsu.DASHBOARD_ID_ALIGNMENT_PANEL]:
                dfs[k][sessionid] = []
            elif k in [dsu.DASHBOARD_ID_COVERAGE, dsu.DASHBOARD_ID_VARIANT]:
                dfs[k][sessionid] = {}
            elif k in [dsu.DASHBOARD_ID_RAW]:
                dfs[k][sessionid] = {'fastq': [], 'bam': [], 'panelbam': [], 'unmappedbam': [], 'panelcounts': [], 'barcodecounts': []}
    print('data frame: '+str(dfs))
    return dfs


def renderDashboard_main(teamid, userid, pipelineid):
    """ Renders the main dashboard.
    """
    sessionid = str(uuid.uuid4())
    dfs = initDataframe( pipelineid, sessionid ) # user needs to define structure of data frame
    print('in renderDashboard_main(), teamid: {}, userid: {}, sessionid: {}'.format(str(teamid), str(userid), str(sessionid)))
    pipeline_list = dsu.list2optionslist([pipelineid])
    dashboard = 'Pipeline Data Analysis Dashboard'
    return html.Div([
        html.H3(dashboard),
        html.Div(teamid, id='teamid', style={'display': 'none'}, key=teamid),
        html.Div(userid, id='userid', style={'display': 'none'}, key=userid),
        html.Div(sessionid, id='sessionid', style={'display': 'none'}, key=sessionid),
        dcc.Dropdown(id='choose-pipeline',
                     options=pipeline_list,
                     value=pipeline_list[0]['value'],
                     placeholder = "Choose pipeline"),
        dcc.Dropdown(id='choose-runs',
                     placeholder = "Choose Runs",
                     searchable=True,
                     multi=True),
        dcc.Dropdown(id='choose-samples',
                     placeholder = "Choose Samples",
                     searchable=True,
                     multi=True),
        dcc.Checklist(id='choose-all-samples',
                      options=[{'label': 'Choose All Samples ', 'value': 'allsamples'}],
                      value=[],
                      labelStyle={'display': 'inline-block'}),
        dcc.Dropdown(id='choose-analysis',
                     placeholder = "Choose Analysis",
                     searchable=True,
                     multi=True),
        html.Div(id='graphdiv', style={'width': '100%'}, children=[])
    ])


def defineCallbacks_mainDashboard(app):
    """ Defines the callbacks for main dashboard. This defines the main navigation callbacks within the dashboard.
    The 'graphdiv' callback is pipeline-specific and analysis-specific, and needs to be defined separately.
    """
    # Once run(s) are chosen, relevant data samples will be displayed for selection.
    @app.callback(
        Output('choose-samples', 'options'),
        Input('choose-runs', 'value'),
        State('choose-pipeline', 'value'),
        State('teamid', 'key'),
        State('userid', 'key'))
    def CB_choose_samples(selected_runs, pipelineid, teamid, userid):
        print('in CB_choose_samples callback')
        if selected_runs != [] and selected_runs != None:
            # print(file_utils.getRunFileIds(dsu.ROOT_FOLDER, teamid, userid, pipelineid, selected_runs))
            # [{'label': 'dnaseq_test', 'value': 'dnaseq_test'}]#
            (sampleids, runids) = file_utils.getRunFileIds(dsu.ROOT_FOLDER, teamid, userid, pipelineid, selected_runs)
            return dsu.list2optionslist(sampleids, runids)
        else:
            return []

    # Once run(s) are chosen and all-samples is checked, all relevant data samples will be displayed. If all-samples is unchecked, samples will be cleared.
    @app.callback(
        Output('choose-samples','value'),
        Input('choose-runs', 'value'),
        Input('choose-all-samples','value'),
        State('choose-pipeline', 'value'),
        State('teamid', 'key'),
        State('userid', 'key'))
    def CB_choose_all_samples( selected_runs, all_samples_checked, pipelineid, teamid, userid ):
        print('in CB_choose_all_samples callback')
        if all_samples_checked != None and 'allsamples' in all_samples_checked:
            (sampleids, runids) = file_utils.getRunFileIds(dsu.ROOT_FOLDER, teamid, userid, pipelineid, selected_runs)
            return sampleids
        else:
            return []

    # Once a pipeline is chosen, relevant runs will be displayed for selection.
    @app.callback(
        Output('choose-runs', 'options'),
        Input('choose-pipeline', 'value'),
        State('teamid', 'key'),
        State('userid', 'key'))
    def CB_choose_pipeline(selected_pipeline, teamid, userid):
        print('in CB_choose_pipeline callback')
        if selected_pipeline != [] and selected_pipeline != None:
            return dsu.list2optionslist(file_utils.getRunIds(dsu.ROOT_FOLDER, teamid, userid, selected_pipeline))
        else:
            return []
