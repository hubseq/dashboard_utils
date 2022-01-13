#
# dashboard_app_dnaseq_targeted
#
# Main entry point for dashboard for Targeted DNA sequencing.
# Using Plotly Dash. Serves front-end that has callback listeners that respond to user inputs.
#
import sys, os, csv, uuid, socket
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
import dashboard_plots_main as dpm
import dashboard_plots_dnaseq_targeted as dpdt

sys.path.append('global_utils/src/')
import file_utils
import global_keys

external_stylesheets = dsu.DASH_STYLESHEETS
STATIC_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), dsu.USER_SCRATCH_DIR)
SESSION_ID = '.'
USER_ID = '.'
PIPELINE_ID = 'Targeted DNA Sequencing'

# main Pandas dataframe that contains all data to display on dashboard
dfs = {}
# log files for each sample - has info about each pipeline run
dflogs = {}

############################################################
## APP OBJECT AND SERVE FRONTEND LAYOUT
############################################################
app = dash.Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)

def serve_layout():
    global dfs
    SESSION_ID = str(uuid.uuid4())
    USER_ID = global_keys.USER_ID  # constant for now. FUTURE: get user ID from client.
    dfs = dpdt.initDataframe( PIPELINE_ID, SESSION_ID ) # user needs to define structure of data frame
    return dpm.renderDashboard_main(USER_ID, SESSION_ID, PIPELINE_ID)

app.layout = serve_layout

############################################################
## CALLBACK FUNCTIONS
############################################################
dpm.defineCallbacks_mainDashboard(app)
dpdt.defineCallbacks_DNASeqTargetedAnalysisList(app)
dpdt.defineCallbacks_fastqcAnalysisDashboard(app)
# dpdt.defineCallbacks_barcodeqcAnalysisDashboard(app)
dpdt.defineCallbacks_alignmentPanelAnalysisDashboard(app)
# dpdt.defineCallbacks_coverageAnalysisDashboard(app)
# dpdt.defineCallbacks_variantAnalysisDashboard(app)

"""
@app.callback(
    Output("download_samtools_stats_csv", "data"),
    Input("samtools_stats_button", "n_clicks"),
    State('choose-samples', 'value'),
    State('SESSION_ID', 'key'),
    prevent_initial_call=True)
def click_download_samtools_stats(n_clicks, sampleids, sessionid):
    if n_clicks != None and n_clicks > 0:
        return dcc.send_data_frame(dfs['alignqc'][sessionid][0].to_csv, "samtools_stats.csv")
    else:
        return None


@app.callback(
    Output("barcodeqc-graphs1", 'figure'),
    Output('barcodeqc-graphs2', 'figure'),
    Input('choose-runs', 'value'),
    Input('choose-subruns', 'value'),
    Input('choose-samples', 'options'),
    Input("choose-barcodeqc-sample", 'value'),
    State('SESSION_ID', 'key'),
    prevent_initial_call=True)
def update_barcodeqc_figure( runids, selected_subruns, selected_samplesfull, sampleid, sessionid ):
    global dfs
    subdirs = selected_subruns
    samplenames = su.getSampleNames( [sampleid], selected_samplesfull )
    barcode_summary_files, barcode_json_files = su.get_barcodeqcfiles( runids, [sampleid], samplenames, subdirs )
    dfs['barcodeqc'][sessionid] = [pd.read_json(barcode_json_files[0][0]), pd.read_json(barcode_json_files[0][1])]
    # graph distribution of barcode counts - allow selection of sample to view barcode distributions
    fig, fig2 = su.plot_barcodeqcfiles( dfs['barcodeqc'][sessionid][0], dfs['barcodeqc'][sessionid][1] )
    fig.update_layout(transition_duration=250, uniformtext_minsize=8, uniformtext_mode='hide', title_x=0.5)
    fig2.update_layout(transition_duration=250, uniformtext_minsize=8, uniformtext_mode='hide', title_x=0.5)
    return fig, fig2


@app.callback(
    Output("coverageqc-graphs1", 'figure'),
    Output('coverageqc-graphs2', 'figure'),
    Output('coverageqc-graphs3', 'figure'),
    Output('coverageqc-graphs4', 'figure'),
    Input('choose-runs', 'value'),
    Input('choose-subruns', 'value'),
    Input('choose-samples', 'options'),
    Input('choose-samples', 'value'),
    Input("choose-coverageqc-samples1", 'value'),
    Input("choose-coverageqc-samples2", 'value'),
    State('SESSION_ID', 'key'),
    prevent_initial_call=True)
def update_coverageqc_figure( runids, selected_subruns, selected_samplesfull, selected_sampleids, sampleid1, sampleid2, sessionid ):
    global dfs
    print(' IN update_coverageqc_figure')
    print(str(dfs['coverageqc']))
    print(f'{sampleid1} vs {sampleid2}')
    subdirs = selected_subruns
    samplenames = su.getSampleNames( [sampleid1, sampleid2], selected_samplesfull )
    df_cov1 = dfs['coverageqc'][sessionid][sampleid1] if sampleid1 in dfs['coverageqc'][sessionid] else pd.DataFrame()
    df_cov2 = dfs['coverageqc'][sessionid][sampleid2] if sampleid2 in dfs['coverageqc'][sessionid] else pd.DataFrame()
    # graph distribution of barcode counts - allow selection of sample to view barcode distributions
    fig, fig2, fig3 = su.plot_coverageqcfiles( df_cov1, df_cov2, [sampleid1,sampleid2] )
    fig4 = su.plot_coverageqc_heatmap( runids, selected_subruns, selected_samplesfull, selected_sampleids, dfs['coverageqc'][sessionid] )
#    fig.update_layout(transition_duration=250, uniformtext_minsize=8, uniformtext_mode='hide', title_x=0.5)
#    fig2.update_layout(transition_duration=250, uniformtext_minsize=8, uniformtext_mode='hide', title_x=0.5)
#    fig3.update_layout(transition_duration=250, uniformtext_minsize=8, uniformtext_mode='hide', title_x=0.5)
    return fig, fig2, fig3, fig4


@app.callback(
    Output("preclusterqc-graphs1", 'figure'),
    Output('preclusterqc-graphs2', 'figure'),
    Output('preclusterqc-graphs3', 'figure'),
    Output('preclusterqc-graphs4', 'figure'),
    Output('preclusterqc-graphs5', 'figure'),
    Output('preclusterqc-graphs6', 'figure'),
    Output('preclusterqc-graphs7', 'figure'),
    Output('preclusterqc-graphs8', 'figure'),
    Output('preclusterqc-graphs9', 'figure'),
    Input('choose-runs', 'value'),
    Input('choose-subruns', 'value'),
    Input('choose-samples', 'options'),
    Input('choose-samples', 'value'),
    Input("choose-preclusterqc-sample", 'value'),
    State('SESSION_ID', 'key'),
    prevent_initial_call=True)
def update_preclusterqc_figure( runids, selected_subruns, selected_samplesfull, selected_sampleids, sampleid, sessionid ):
    global dfs
    print(' IN update_preclusterqc_figure')
    print(str(dfs['preclusterqc']))
    subdirs = selected_subruns
    samplenames = su.getSampleNames( [sampleid], selected_samplesfull )
    df_edgelist = dfs['preclusterqc'][sessionid][sampleid] if sampleid in dfs['preclusterqc'][sessionid] else pd.DataFrame()
    # graph distribution of barcode counts - allow selection of sample to view barcode distributions
    precluster_stats, fig, fig2, fig3, fig4, fig5, fig6, fig7, fig8, fig9 = su.plot_preclusterqcfiles( df_edgelist, [sampleid] )
#    fig.update_layout(transition_duration=250, uniformtext_minsize=8, uniformtext_mode='hide', title_x=0.5)
    return fig, fig2, fig3, fig4, fig5, fig6, fig7, fig8, fig9


@app.callback(
    Output("postclusterqc-graphs1", 'figure'),
    Output('postclusterqc-graphs2', 'figure'),
    Output('postclusterqc-graphs3', 'figure'),
    Output('postclusterqc-graphs4', 'figure'),
    Output('postclusterqc-graphs5', 'figure'),
    Output('postclusterqc-graphs6', 'figure'),
    Output('postclusterqc-graphs7', 'figure'),
    Output('postclusterqc-graphs8', 'figure'),
    Output('postclusterqc-graphs9', 'figure'),
    Output('postclusterqc-graphs10', 'figure'),
    Input('choose-runs', 'value'),
    Input('choose-subruns', 'value'),
    Input('choose-samples', 'options'),
    Input('choose-samples', 'value'),
    Input("choose-postclusterqc-sample", 'value'),
    State('SESSION_ID', 'key'),
    prevent_initial_call=True)
def update_postclusterqc_figure( runids, selected_subruns, selected_samplesfull, selected_sampleids, sampleid, sessionid ):
    global dfs
    print(' IN update_postclusterqc_figure')
    print(str(dfs['postclusterqc']))
    subdirs = selected_subruns
    samplenames = su.getSampleNames( [sampleid], selected_samplesfull )
    df_edgelist = dfs['postclusterqc'][sessionid][sampleid][0] if sampleid in dfs['postclusterqc'][sessionid] else pd.DataFrame()
    df_cluster = dfs['postclusterqc'][sessionid][sampleid][1] if sampleid in dfs['postclusterqc'][sessionid] else pd.DataFrame()
    df_node = dfs['postclusterqc'][sessionid][sampleid][2] if sampleid in dfs['postclusterqc'][sessionid] else pd.DataFrame()

    # graph distribution of barcode counts - allow selection of sample to view barcode distributions
    postcluster_stats, fig, fig2, fig3, fig4, fig5, fig6, fig7, fig8, fig9, fig10 = su.plot_postclusterqcfiles( df_edgelist, df_cluster, df_node, [sampleid] )
#    fig.update_layout(transition_duration=250, uniformtext_minsize=8, uniformtext_mode='hide', title_x=0.5)
    return fig, fig2, fig3, fig4, fig5, fig6, fig7, fig8, fig9, fig10


@app.callback(
    Output("variantqc-graphs", 'figure'),
    Input('choose-runs', 'value'),
    Input('choose-subruns', 'value'),
    Input('choose-samples', 'options'),
    Input('choose-samples', 'value'),
    prevent_initial_call=True)
def update_variantqc_figure( runids, selected_subruns, selected_samplesfull, selected_sampleids ):
    global dfs
    print('AM I GETTING IN HERE?????')
    print(' IN update_variantqc_figure')
    print(str(dfs['variantqc']))
    subdirs = selected_subruns
    fig = su.plot_variantqc_heatmap( runids, selected_subruns, selected_samplesfull, selected_sampleids, dfs['variantqc'], 'bcftools' )
    return fig

@app.callback(
    Output("download_barcode_I1_csv", "data"),
    Input("barcode-I1-button", "n_clicks"),
    State('choose-samples', 'value'),
    State('SESSION_ID', 'key'),
    prevent_initial_call=True)
def click_download_barcode_I1(n_clicks, sampleids, sessionid):
    if n_clicks != None and n_clicks > 0:
        return dcc.send_data_frame(dfs['barcodeqc'][sessionid][0].to_csv, "barcodeqc_I1.csv")
    else:
        return None


@app.callback(
    Output("download_barcode_I2_csv", "data"),
    Input("barcode-I2-button", "n_clicks"),
    State('choose-samples', 'value'),
    State('SESSION_ID', 'key'),
    prevent_initial_call=True)
def click_download_barcode_I2(n_clicks, sampleids, sessionid):
    if n_clicks != None and n_clicks > 0:
        return dcc.send_data_frame(dfs['barcodeqc'][sessionid][1].to_csv, "barcodeqc_I2.csv")
    else:
        return None


@app.callback(
    Output("download_coverage_csv", "data"),
    Input("coverage-button", "n_clicks"),
    State('choose-samples', 'value'),
    State('SESSION_ID', 'key'),
    prevent_initial_call=True)
def click_download_coverage(n_clicks, sampleids, sessionid):
    global dfs
    print('NCLICKS: '+str(n_clicks))
    if n_clicks != None and n_clicks > 0:
        dfs_filtered = {k: v for k, v in dfs['coverageqc'][sessionid].items() if k in sampleids}
        df_cov = pd.concat( list(dfs_filtered.values()), keys=list(dfs_filtered.keys()))
        print(df_cov)
        return dcc.send_data_frame(df_cov.to_csv, "coveragecounts.csv")
    else:
        return None

@app.callback(
    Output("download_barcodeqc_runlogs_csv", "data"),
    Input("barcodeqc-runlogs", "n_clicks"),
    State('choose-runs', 'value'),
    State('choose-subruns', 'value'),
    State('choose-samples', 'value'),
    State('SESSION_ID', 'key'),
    prevent_initial_call=True)
def click_download_barcodeqc_runlogs(n_clicks, runs, subruns, sampleids, sessionid):
    if n_clicks != None and n_clicks > 0:
        dflogs = su.getLogfileParams( runs, sampleids, subruns, 'barcodeqc' )
        return dcc.send_data_frame(dflogs.to_csv, "barcodeqc_runlogs.csv")
    else:
        return None


@app.callback(
    Output("download_alignqc_runlogs_csv", "data"),
    Input("alignqc-runlogs", "n_clicks"),
    State('choose-runs', 'value'),
    State('choose-subruns', 'value'),
    State('choose-samples', 'value'),
    State('SESSION_ID', 'key'),
    prevent_initial_call=True)
def click_download_alignqc_runlogs(n_clicks, runs, subruns, sampleids, sessionid):
    if n_clicks != None and n_clicks > 0:
        dflogs = su.getLogfileParams( runs, sampleids, subruns, 'alignqc' )
        return dcc.send_data_frame(dflogs.to_csv, "alignqc_runlogs.csv")
    else:
        return None


@app.callback(
    Output("download_coverageqc_runlogs_csv", "data"),
    Input("coverageqc-runlogs", "n_clicks"),
    State('choose-runs', 'value'),
    State('choose-subruns', 'value'),
    State('choose-samples', 'value'),
    State('SESSION_ID', 'key'),
    prevent_initial_call=True)
def click_download_coverageqc_runlogs(n_clicks, runs, subruns, sampleids, sessionid):
    if n_clicks != None and n_clicks > 0:
        dflogs = su.getLogfileParams( runs, sampleids, subruns, 'coverageqc' )
        return dcc.send_data_frame(dflogs.to_csv, "coverageqc_runlogs.csv")
    else:
        return None


@app.callback(
    Output('graphdiv', 'children'),
    Input('choose-samples', 'value'),
    Input('choose-samples', 'options'),
    Input('choose-runs', 'value'),
    Input('choose-subruns', 'value'),
    Input('choose-qcplots', 'value'),
    State('SESSION_ID', 'key'),
    State('choose-pipeline', 'value'))
def update_figure(sampleids, selected_samplesfull, selected_runs, selected_subruns, selected_qcplots, sessionid, pipeline):
    global dfs
    graphs = []
    # rid = selected_runs[0] # for now - single run
    print('in update figure main')
    print('SELECTED SUBRUNS IN UPDATE FIGURE: '+str(selected_subruns))
    subdirs = selected_subruns
    samplenames = []
    print('SELECTED SAMPLES: '+str(sampleids))
    print('SELECTED SAMPLENAMES: '+str(selected_samplesfull))
    if (sampleids != None and sampleids != []) and (selected_runs != [] and selected_runs != '' and selected_runs != None):
        samplenames = su.getSampleNames( sampleids, selected_samplesfull )
        if 'raw' in selected_qcplots:
            graphs.append(html.P('', id='raw-spacer'))
            graphs.append(html.H2('Raw Sequencing Files', id='raw-title'))
            graphs.append(html.P('Right-Click and Download Link.', id='raw-desc'))
            rawfiles_all, rawnames_all = su.get_rawfiles( selected_runs, sampleids, samplenames, subdirs )
            list_elements = []
            for k in range(0,len(rawfiles_all)):
                s_name = rawnames_all[k]
                f = rawfiles_all[k]
                f_name = f.split('/')[-1]
                list_elements.append(html.Li(id=f_name+'_listitem', children=html.A(id=f_name,href=os.path.join(STATIC_PATH,f_name), children=s_name + ': '+f_name)))
            graphs.append(html.Ul(id='raw-files', children=list_elements))

        if 'fastqc' in selected_qcplots:
            graphs.append(html.P('', id='fastqc-spacer'))
            graphs.append(html.H2('Read FASTQC', id='fastqc-title'))
            graphs.append(html.P('Right-Click to open FASTQC HTML in new tab or window.', id='fastqc-desc'))
            fastqcfiles_all, fastqcnames_all = su.get_fastqcfiles( selected_runs, sampleids, samplenames, subdirs )
            list_elements = []
            for k in range(0,len(fastqcfiles_all)):
                s_name = fastqcnames_all[k]
                f = fastqcfiles_all[k]
                f_name = f.split('/')[-1]
                list_elements.append(html.Li(id=f_name+'_listitem', children=html.A(id=f_name,href=os.path.join(STATIC_PATH,f_name), children=s_name + ': '+f_name)))
            graphs.append(html.Ul(id='fastqc-files', children=list_elements))

        if 'barcodeqc' in selected_qcplots:
            graphs.append(html.H2('Barcode QC', id='barcodeqc-title'))
            barcode_summary_files, barcode_json_files = su.get_barcodeqcfiles( selected_runs, sampleids, samplenames, subdirs )
            print('BARCODE SUMMARY FILES: '+str(barcode_summary_files))
            print('BARCODE JSON FILES: '+str(barcode_json_files))
            print('SAMPLEIDS: '+str(sampleids))
            if len(barcode_json_files)>0 and len(sampleids) > 0:
                dfs['barcodeqc'][sessionid] = [pd.read_json(barcode_json_files[0][0]), pd.read_json(barcode_json_files[0][1])]
                # graph distribution of barcode counts - allow selection of sample to view barcode distributions
                fig, fig2 = su.plot_barcodeqcfiles( dfs['barcodeqc'][sessionid][0], dfs['barcodeqc'][sessionid][1] )
                fig.update_layout(transition_duration=250, uniformtext_minsize=8, uniformtext_mode='hide', title_x=0.5)
                fig2.update_layout(transition_duration=250, uniformtext_minsize=8, uniformtext_mode='hide', title_x=0.5)
                graphs.append(html.Div(id='barcodeqc-wrapper-div', children=[
                    # dropdown to choose which sample to look at Barcode QC
                    dcc.Dropdown(id='choose-barcodeqc-sample',
                                 options=dsu.list2optionslist(sampleids),
                                 value=dsu.list2optionslist(sampleids)[0]['value'],
                                 placeholder = "Choose BarcodeQC Sample"),
                    # allow download of barcode dataframe files
                    html.Div(id='barcode-download-buttons', children=[html.Button("Download Barcode I1", id="barcode-I1-button"),
                                                                      html.Button("Download Barcode I2", id="barcode-I2-button", style={"margin": "5px"}),
                                                                      html.Button("Download BarcodeQC Run Logs", id="barcodeqc-runlogs", style={"margin": "5px"})]),
                    dcc.Download(id="download_barcode_I1_csv"),
                    dcc.Download(id="download_barcode_I2_csv"),
                    dcc.Download(id="download_barcodeqc_runlogs_csv"),
                    html.Div(id="barcodeqc-graphs-div", children=[
                        # barcode QC plots
                        dcc.Graph(id='barcodeqc-graphs1', figure=fig),
                        dcc.Graph(id='barcodeqc-graphs2', figure=fig2)])
                ]))

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

            if pipeline=='Amplicon':
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

        if 'coverageqc' in selected_qcplots and pipeline == 'WGS':
            coverage_hist_json_files, coverage_hist_sampleids = su.get_coveragehistqcfiles( selected_runs, sampleids, samplenames, subdirs )
            print('COVERAGE HIST JSON FILES: '+str(coverage_hist_json_files))
            if len(coverage_hist_json_files)>0 and len(coverage_hist_sampleids) > 0:
                for k in range(0,len(coverage_hist_json_files)):
                    coverage_file = coverage_hist_json_files[k]
                    coverage_sampleid = coverage_hist_sampleids[k]
                    dfs['coverageqc'][sessionid][coverage_sampleid] = coverage_file   # don't create dataframe - just keep file name
                graphs.append(html.H2('Coverage QC', id='coverageqc-title'))
                hist_figs, df_hist_summary = su.plot_coverage_histograms( selected_runs, selected_subruns, selected_samplesfull, sampleids, dfs['coverageqc'][sessionid] )
                graphs.append(dash_table.DataTable(id='coverageqc-hist-table',columns=[{"name": i, "id": i} for i in df_hist_summary.columns], data=df_hist_summary.to_dict('records')))
                fig_list = []
                for m in range(0,len(hist_figs)):
                    hist_fig = hist_figs[m]
                    fig_list.append(dcc.Graph(id='coverageqc-hist-graphs'+str(m), figure=hist_fig))
                graphs.append(html.Div(id="coverageqc-hist-graphs-div", children=fig_list))

        if 'coverageqc' in selected_qcplots and pipeline == 'Amplicon':
            coverage_json_files, coverage_sampleids = su.get_coverageqcfiles( selected_runs, sampleids, samplenames, subdirs )
            print('COVERAGE JSON FILES: '+str(coverage_json_files))
            if len(coverage_json_files)>0 and len(sampleids) > 0:
                for k in range(0,len(coverage_json_files)):
                    coverage_file = coverage_json_files[k]
                    coverage_sampleid = coverage_sampleids[k]
                    dfs['coverageqc'][sessionid][coverage_sampleid] = pd.read_csv(coverage_file,sep='\t',header=1,names=['AmpliconId','Chr','Start','End','Strand','Length','Counts'])
                # this re-renders and re-inits on every added sample / changed run - this needs to be fixed.
                graphs.append(html.H2('Coverage QC', id='coverageqc-title'))
                # graph distribution of barcode counts - allow selection of sample to view barcode distributions
                fig, fig2, fig3 = su.plot_coverageqcfiles( pd.DataFrame(), pd.DataFrame(), [] )
                fig4 = su.plot_coverageqc_heatmap( selected_runs, selected_subruns, selected_samplesfull, sampleids, dfs['coverageqc'][sessionid] )
                fig.update_layout(transition_duration=250, uniformtext_minsize=8, uniformtext_mode='hide', title_x=0.5)
                fig2.update_layout(transition_duration=250, uniformtext_minsize=8, uniformtext_mode='hide', title_x=0.5)
                fig3.update_layout(transition_duration=250, uniformtext_minsize=8, uniformtext_mode='hide', title_x=0.5)
                fig4.update_layout(transition_duration=250, uniformtext_minsize=4, uniformtext_mode='hide', title_x=0.5)
                graphs.append(html.Div(id='coverageqc-wrapper-div', children=[
                    # allow download of coverage dataframe files (for samples selected)
                    html.Div(id='coverage-download-button', children=[html.Button("Download Coverage Counts", id='coverage-button'),
                                                                      html.Button("Download CoverageQC Run Logs", id="coverageqc-runlogs", style={"margin": "5px"}),
                                                                      dcc.Download(id="download_coverage_csv"),
                                                                      dcc.Download(id="download_coverageqc_runlogs_csv")]),
                    html.Div(id="coverageqc-graphs-heatmap-div", children=[
                        dcc.Graph(id='coverageqc-graphs4', figure=fig4)
                        ]),
                        # coverage heatmap
                    # dropdown to choose which sample to look at coverage for
                    html.Hr(),
                    html.P('Select 2 samples to compare coverage:'),
                    dcc.Dropdown(id='choose-coverageqc-samples1',
                                 options=dsu.list2optionslist(sampleids),
                                 placeholder = "Choose Sample 1"),
                    dcc.Dropdown(id='choose-coverageqc-samples2',
                                 options=dsu.list2optionslist(sampleids),
                                 placeholder = "Choose Sample 2"),
                    html.Div(id="coverageqc-graphs-div", children=[
                        # coverage QC plots
                        dcc.Graph(id='coverageqc-graphs1', figure=fig),
                        dcc.Graph(id='coverageqc-graphs2', figure=fig2),
                        dcc.Graph(id='coverageqc-graphs3', figure=fig3)])
                ]))
        if 'preclusterqc' in selected_qcplots:
            precluster_csv_files, precluster_sampleids = su.get_preclusterqcfiles( selected_runs, sampleids, samplenames, subdirs )
            print('PRECLUSTER CSV FILES: '+str(precluster_csv_files))
            if len(precluster_csv_files)>0 and len(sampleids) > 0:
                for k in range(0,len(precluster_csv_files)):
                    precluster_file = precluster_csv_files[k]
                    precluster_sampleid = precluster_sampleids[k]
                    dfs['preclusterqc'][sessionid][precluster_sampleid] = pd.read_csv(precluster_file,sep='\t')

            precluster_stats, fig, fig2, fig3, fig4, fig5, fig6, fig7, fig8, fig9 = su.plot_preclusterqcfiles( pd.DataFrame(), [] )
            graphs.append(html.H2('Pre-Cluster QC', id='preclusterqc-title'))
            graphs.append(html.Div(id='preclusterqc-wrapper-div', children=[
                html.P('Select a sample to view pre-cluster QC.'),
                    dcc.Dropdown(id='choose-preclusterqc-sample',
                                 options=dsu.list2optionslist(sampleids),
                                 placeholder = "Choose Sample"),
                    html.Div(id="preclusterqc-graphs-div", children=[
                        # coverage QC plots
                        dcc.Graph(id='preclusterqc-graphs1', figure=fig),
                        dcc.Graph(id='preclusterqc-graphs2', figure=fig2),
                        dcc.Graph(id='preclusterqc-graphs3', figure=fig3),
                        dcc.Graph(id='preclusterqc-graphs4', figure=fig4),
                        dcc.Graph(id='preclusterqc-graphs5', figure=fig5),
                        dcc.Graph(id='preclusterqc-graphs6', figure=fig6),
                        dcc.Graph(id='preclusterqc-graphs7', figure=fig7),
                        dcc.Graph(id='preclusterqc-graphs8', figure=fig8),
                        dcc.Graph(id='preclusterqc-graphs9', figure=fig9),
                    ])]))
        if 'postclusterqc' in selected_qcplots:
            filtered_edgelist_csv_files, cluster_csv_files, node_csv_files, postcluster_sampleids = su.get_postclusterqcfiles( selected_runs, sampleids, samplenames, subdirs )
            print('cluster CSV FILES: '+str(cluster_csv_files))
            if len(filtered_edgelist_csv_files)>0 and len(cluster_csv_files)>0 and len(node_csv_files)>0 and len(sampleids) > 0:
                for k in range(0,len(cluster_csv_files)):
                    filtered_edgelist_file = filtered_edgelist_csv_files[k]
                    node_file = node_csv_files[k]
                    postcluster_sampleid = postcluster_sampleids[k]
                    cluster_file = cluster_csv_files[k]
                    # each sample has 3 files: edgelist_file, cluster_file, node_file
                    dfs['postclusterqc'][sessionid][postcluster_sampleid] = [pd.read_csv(filtered_edgelist_file), pd.read_csv(cluster_file), pd.read_csv(node_file)]

            postcluster_stats, fig, fig2, fig3, fig4, fig5, fig6, fig7, fig8, fig9, fig10 = su.plot_postclusterqcfiles( pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), [] )
            graphs.append(html.H2('Post-Cluster QC', id='postclusterqc-title'))
            graphs.append(html.Div(id='postclusterqc-wrapper-div', children=[
                html.P('Select a sample to view post-cluster QC.'),
                    dcc.Dropdown(id='choose-postclusterqc-sample',
                                 options=dsu.list2optionslist(sampleids),
                                 placeholder = "Choose Sample"),
                    html.Div(id="postclusterqc-graphs-div", children=[
                        # coverage QC plots
                        dcc.Graph(id='postclusterqc-graphs1', figure=fig),
                        dcc.Graph(id='postclusterqc-graphs2', figure=fig2),
                        dcc.Graph(id='postclusterqc-graphs3', figure=fig3),
                        dcc.Graph(id='postclusterqc-graphs4', figure=fig4),
                        dcc.Graph(id='postclusterqc-graphs5', figure=fig5),
                        dcc.Graph(id='postclusterqc-graphs6', figure=fig6),
                        dcc.Graph(id='postclusterqc-graphs7', figure=fig7),
                        dcc.Graph(id='postclusterqc-graphs8', figure=fig8),
                        dcc.Graph(id='postclusterqc-graphs9', figure=fig9),
                        dcc.Graph(id='postclusterqc-graphs10', figure=fig10),
                    ])]))
        if 'variantqc' in selected_qcplots:
            variant_vcf_files, variant_sampleids = su.get_variantqcfiles( selected_runs, sampleids, samplenames, subdirs, 'bcftools' )
            if len(variant_vcf_files)>0 and len(variant_sampleids) > 0:
                for k in range(0,len(variant_vcf_files)):
                    variant_file = variant_vcf_files[k]
                    variant_sampleid = variant_sampleids[k]
                    dfs['variantqc'][variant_sampleid] = pd.read_csv(variant_file,sep='\t',dtype=str,index_col=False,header=1,skip_blank_lines=True,comment='#', \
                                                                     names=['Chrom','Position','ID','Ref','Var','Qual','Skip','Freqs','Format', 'More'])

                # this re-renders and re-inits on every added sample / changed run - this needs to be fixed.
                graphs.append(html.H2('Variant QC', id='variantqc-title'))
                # graphs
                fig = su.plot_variantqc_heatmap( selected_runs, selected_subruns, selected_samplesfull, sampleids, dfs['variantqc'], 'bcftools' )
                fig.update_layout(transition_duration=250, uniformtext_minsize=4, uniformtext_mode='hide', title_x=0.5)
                graphs.append(html.Div(id='variantqc-wrapper-div', children=[
                    html.Div(id="variantqc-graphs-heatmap-div", children=[
                        dcc.Graph(id='variantqc-graphs', figure=fig)
                        ]),
                ]))
    return graphs
"""

@app.server.route(os.path.join(STATIC_PATH,'<resource>'))
def serve_static(resource):
    print('RESOURCE: '+str(resource))
    return flask.send_from_directory(STATIC_PATH, resource)

if __name__ == '__main__':
    local_ip = socket.gethostbyname(socket.gethostname())
    app.run_server(host=local_ip, port='8050', debug=False,dev_tools_ui=False,dev_tools_props_check=False)
