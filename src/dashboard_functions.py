#
# dashboard_functions
#
# Render and callback functions for each pipeline, analysis and main dashboard
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


def displayDashboard( selected_pipeline, selected_analysis, selected_runs, selected_samples, dashboard_type = 'analysis'):
    """ Given pipeline, analysis, run, and data sample information, displays a dashboard of appropriate plots.
    This will call the appropriate subfunction to load the correct dashboard.

    return: LIST of figures (plots), tables and other HTML components to display.
    """
    return []


def defineCallbacks_mainDashboard(app):
    """ Defines the callbacks for main dashboard
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

    # Once runs and samples are chosen, the list of possible analysis dashboards will displayed as dropdown.
    @app.callback(
        Output('choose-analysis', 'options'),
        Input('pipeline-id', 'value'),
        State('userid', 'key'))
    def CB_choose_analysisplots( selected_pipeline, USER_ID ):
        if selected_pipeline != [] and selected_pipeline != None:
            return dsu.list2optionslist(file_utils.getAnalysisList(USER_ID, selected_pipeline))
        else:
            return []

    # Display analysis dashboard
    @app.callback(
        Output('graphdiv', 'children'),
        Input('choose-analysis', 'value'),
        State('choose-runs', 'value'),
        State('choose-samples', 'value'),
        State('pipeline-id', 'value'))
    def CB_display_analysis_dashboard( selected_analysis, selected_runs, selected_samples, selected_pipeline ):
        if selected_pipeline != [] and selected_pipeline != None and
           selected_runs != [] and selected_runs != None and
           selected_samples != [] and selected_samples != None and
           selected_analysis != [] and selected_analysis != None:
           return dsu.displayDashboard( selected_pipeline, selected_analysis, selected_runs, selected_samples, 'analysis')
        else:
           return []


def defineCallbacks_fastqcAnalysisDashboard(app):
    """ Callbacks for FASTQC analysis dashboard.
    """
    @app.callback(
        Output('graphdiv', 'children'),
        Input('choose-samples', 'value'),
        Input('choose-runs', 'value'),
        Input('choose-analysis', 'value'),
        State('session_id', 'key'),
        State('userid', 'key'),
        State('choose-pipeline', 'value'))
    def CB_fastqc_analysis_dashboard(selected_samples, selected_runs, selected_analysis, sessionid, userid, pipelineid):
        if selected_analysis == dsu.DASHBOARD_ID_FASTQC:
            # get sample files and IDs
            data_file_names, data_sample_ids = dfu.getSamples(userid, pipelineid, selected_runs, selected_sample, ['fastqc'], ['^HTML'], 'HTML')
            # create dashboard plots
            graphs = []
            graphs.append(html.P(''))
            graphs.append(html.H2('Read FASTQC', id='fastqc-title'))
            graphs.append(html.P('Right-Click to open FASTQC HTML in new tab or window.', id='fastqc-desc'))
            list_elements = []
            for k in range(0,len(data_file_names)):
                s_name = data_sample_ids[k]
                f_name = data_file_names[k]
                list_elements.append(html.Li(id=f_name+'_listitem', children=html.A(id=f_name,href=os.path.join(STATIC_PATH,f_name), children=s_name + ': '+f_name)))
            graphs.append(html.Ul(id='fastqc-files', children=list_elements))
            return graphs
        else:
            dash.no_update


def defineCallbacks_alignmentPanelAnalysisDashboard(app):
    """ Callbacks for panel-based alignment analysis dashboard.
    """
    @app.callback(
        Output('graphdiv', 'children'),
        Input('choose-samples', 'value'),
        Input('choose-runs', 'value'),
        Input('choose-analysis', 'value'),
        State('session_id', 'key'),
        State('userid', 'key'),
        State('choose-pipeline', 'value'),
        State('graphdiv', 'children'))
    def CB_alignment_panel_analysis_dashboard(selected_samples, selected_runs, selected_analysis, sessionid, userid, pipelineid):
        if selected_analysis == dsu.DASHBOARD_ID_ALIGNMENT_PANEL:
            # get sample files and IDs
            data_file_names, data_sample_ids = dfu.getSamples(userid, pipelineid, selected_runs, selected_sample, ['fastqc'], ['^HTML'], 'HTML')
            # create dashboard plots
            graphs = []
            graphs.append(html.H2('Targeted Alignment Analysis', id='alignqc-title'))
            ## CREATE ACTUAL PLOTS
            return graphs
        else:
            dash.no_update
            
"""
       if 'alignqc' in selected_qcplots:
            graphs.append(html.H2('Alignment QC', id='alignqc-title'))
            qcfiles_df = su.get_qcfiles( selected_runs, sampleids, samplenames, subdirs )
            dfs['alignqc'][sessionid] = [pd.concat(qcfiles_df['samtools_flagstat_dfs'], keys=qcfiles_df['samplenames'], names=['Sample','Stat'])]
            print('QC FILES: ')
            print(qcfiles_df)
            # allow download of dataframes
            graphs.append(html.Div(id="alignqc-download-buttons", children=[html.Button("Download Read Mapping Statistics (CSV)", id="samtools_stats_button", style={"margin": "5px"}), html.Button("Download AlignQC Run Logs", id="alignqc-runlogs")]))
            graphs.append(dcc.Download(id="download_samtools_stats_csv"))
            graphs.append(dcc.Download(id="download_alignqc_runlogs_csv"))
            # create figures
            fig, fig2 = su.plot_percent_mapped( qcfiles_df['samtools_flagstat_dfs'], samplenames )
            fig.update_layout(transition_duration=250, xaxis_tickangle=-90,uniformtext_minsize=8, uniformtext_mode='hide', title_x=0.5)
            fig2.update_layout(transition_duration=250, xaxis_tickangle=-90,uniformtext_minsize=8, uniformtext_mode='hide', title_x=0.5)
            graphs.append(dcc.Graph(id='graphs1', figure=fig))
            graphs.append(html.Hr())
            graphs.append(dcc.Graph(id='graphs2', figure=fig2))
            graphs.append(html.Hr())

            if assay=='Amplicon':
                fig3, fig4, fig5 = su.plot_percent_ontarget_and_fold80( qcfiles_df['picard_hsmetrics_dfs'], samplenames )
                fig3.update_layout(transition_duration=250, xaxis_tickangle=-90,uniformtext_minsize=8, uniformtext_mode='hide', title_x=0.5)
                fig4.update_layout(transition_duration=250, xaxis_tickangle=-90,uniformtext_minsize=8, uniformtext_mode='hide', title_x=0.5)
                fig5.update_layout(transition_duration=250, xaxis_tickangle=-90,uniformtext_minsize=8, uniformtext_mode='hide', title_x=0.5)
                graphs.append(dcc.Graph(id='graphs3', figure=fig3))
                graphs.append(html.Hr())
                graphs.append(dcc.Graph(id='graphs4', figure=fig4))
                graphs.append(html.Hr())
                graphs.append(dcc.Graph(id='graphs5', figure=fig5))
                graphs.append(html.Hr())
  """
