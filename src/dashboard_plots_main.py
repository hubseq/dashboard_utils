#
# dashboard_plots_main
#
# Render and callback functions for main dashboard
#
import sys, os, csv, uuid
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import pandas as pd
import flask
import dashboard_file_utils as dfu
import dashboard_plot_utils as dpu
import dashboard_server_utils as dsu


def renderDashboard_main(userid, sessionid, pipelineid):
    """ Renders the main dashboard.
    """
    pipeline_list = dsu.list2optionslist([pipelineid])
    dashboard == 'Pipeline Data Analysis Dashboard':
    return html.Div([
        html.H3(dashboard),
        html.Div(userid, id='USER_ID', style={'display': 'none'}, key=userid),
        html.Div(sessionid, id='SESSION_ID', style={'display': 'none'}, key=sessionid),
        dcc.Dropdown(id='choose-pipeline',
                     options=pipeline_list,
                     value=pipeline_list[0]['value'],
                     placeholder = "Choose pipeline"),
        dcc.Dropdown(id='choose-runs',
                     placeholder = "Choose Runs",
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
        State('pipeline-id', 'value'),
        State('userid', 'key'))
    def CB_choose_samples(selected_runs, pipelineid, USER_ID):
        if selected_runs != [] and selected_runs != None:
            return dsu.list2optionslist(file_utils.getRunFileIds(USER_ID, pipelineid, selected_runs))
        else:
            return []

    # Once run(s) are chosen and all-samples is checked, all relevant data samples will be displayed. If all-samples is unchecked, samples will be cleared.
    @app.callback(
        Output('choose-samples','value'),
        Input('choose-runs', 'value'),
        Input('choose-all-samples','value'),
        State('pipeline-id', 'value'),
        State('userid', 'key'))
    def CB_choose_all_samples( selected_runs, all_samples_checked, pipelineid, USER_ID ):
        if all_samples_checked != None and 'allsamples' in all_samples_checked:
            return file_utils.getRunFileIds(USER_ID, pipelineid, selected_runs)
        else:
            return []

    # Once a pipeline is chosen, relevant runs will be displayed for selection.
    @app.callback(
        Output('choose-runs', 'options'),
        Input('choose-pipeline', 'value'),
        State('userid', 'key'))
    def CB_choose_pipeline(selected_pipeline, USER_ID):
        if selected_pipeline != [] and selected_pipeline != None:
            return dsu.list2optionslist(file_utils.getRunIds(USER_ID, selected_pipeline))
        else:
            return []
