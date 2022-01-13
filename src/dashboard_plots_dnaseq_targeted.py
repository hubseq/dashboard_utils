#
# dashboard_plots_dnaseq_targeted
#
# Callbacks and plot functions for Targeted DNA-Seq. These plots will be displayed on the web Dashboard upon user input (within callback functions).
#
import sys, os, csv, uuid
import dash
from dash import dash_table
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
import pandas as pd
import dashboard_file_utils as dfu
import dashboard_plot_utils as dpu
import dashboard_server_utils as dsu

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


############################################################
## CALLBACK FUNCTIONS
############################################################
def defineCallbacks_DNASeqTargetedAnalysisList(app):
    # Once runs and samples are chosen, the list of possible analysis dashboards will displayed as dropdown.
    @app.callback(
        Output('choose-analysis', 'options'),
        Input('pipeline-id', 'value'),
        State('userid', 'key'))
    def CB_dnaseq_targeted_choose_analysisplots( selected_pipeline, USER_ID ):
        if selected_pipeline != [] and selected_pipeline != None:
            return dsu.list2optionslist(list(PIPELINE_DNASEQ_TARGETED_DF.keys()))
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
            flagstat_file_names, data_sample_ids = dfu.getSamples(userid, pipelineid, selected_runs, selected_sample, ['alignmentqc'], ['^flagstat.json'], 'JSON')
            hsmetrics_file_names, data_sample_ids = dfu.getSamples(userid, pipelineid, selected_runs, selected_sample, ['alignmentqc'], ['^hsmetrics.json'], 'JSON')
            # create plot figures
            flagstat_figures_list = plotFlagstat( flagstat_file_names, data_sample_ids )
            hsmetrics_figures_list = plotHsMetrics( hsmetrics_file_names, data_sample_ids )
            # create dashboard plots
            graphs = []
            graphs.append(html.H2('Targeted Alignment Analysis', id='alignqc-title'))
            ## display figures
            for i in range(0,len(flagstat_figures_list)):
                graphs.append(dcc.Graph(id='graphs_flagstat_'+str(i+1), figure=flagstat_figures_list[i]))
                graphs.append(html.Hr())
            for i in range(0,len(hsmetrics_figures_list)):
                graphs.append(dcc.Graph(id='graphs_hsmetrics_'+str(i+1), figure=hsmetrics_figures_list[i]))
                graphs.append(html.Hr())
            # return final graph elements (list) - rendered by Dash
            return graphs
        else:
            dash.no_update


############################################################
## PLOT FUNCTIONS
############################################################
def plotFlagstat( flagstat_file_names, data_sample_ids ):
    """ plots percent mapped and other alignment plots derived from samtools flagstat output

    flagstat_file_names: LIST of JSON files
    data_sample_ids: LIST of sample IDs for these files (ordered)
    return: LIST of figures
    """
    plots = []
    samtools_flagstat_dfs = []
    percent_mapped, mapped, properly_paired = [], [], []
    flagstat_howmanyempty = 0

    # read and convert JSONs to pandas dataframes
    for i in range(len(flagstat_file_names)):
        samtools_flagstat_dfs.append(pd.read_json( flagstat_file_names[i], orient='index' ))

    # get flagstat alignment info for each sample
    for i in range(len(samtools_flagstat_dfs)):
        # we skip samples that don't have samtools flagstat output
        if type(samtools_flagstat_dfs[i]) == list and samtools_flagstat_dfs[i] == []:
            flagstat_howmanyempty += 1
        else:
            _total_reads = samtools_flagstat_dfs[i]['qcpass']['total']
            percent_mapped.append(100.0*samtools_flagstat_dfs[i]['qcpass']['mapped']/_total_reads if _total_reads > 0 else 0)
            properly_paired.append(100.0*samtools_flagstat_dfs[i]['qcpass']['properly_paired']/_total_reads if _total_reads > 0 else 0)
            mapped.append(samtools_flagstat_dfs[i]['qcpass']['mapped'])

    df = pd.DataFrame( list(zip(data_sample_ids, mapped, percent_mapped, properly_paired)), columns=['sample','mapped','percent_mapped', 'properly_paired'] ) if samtools_flagstat_dfs != None and len(samtools_flagstat_dfs) > 0 and flagstat_howmanyempty < len(samtools_flagstat_dfs) else pd.DataFrame({"sample": [], "percent_mapped": [], "properly_paired": []})

    # % mapped plot
    p1 = plotBar( list(df["sample"]), list(df["percent_mapped"]), "sample", "percent_mapped", "% Reads Mapped to hg38" )
    plots.append( p1.getFigureObject())
    # % properly paired plot
    p2 = plotBar( list(df["sample"]), list(df["properly_paired"]), "sample", "properly_paired", "% Mapped Reads that are Properly Paired" )
    plots.append( p2.getFigureObject())

    return plots


def plotHsMetrics( hsmetrics_file_names, data_sample_ids ):
    """ plots % on-target, % off-target and FOLD-80 from picard tools HS metrics.
    Note that on-target includes "near-target" from HS metrics.

    hsmetrics_file_names: LIST of JSON files
    data_sample_ids: LIST of sample IDs for these files (ordered)
    return: LIST of figures
    """
    plots = []
    picard_hsmetrics_dfs = []
    on_targets, off_targets, fold_80 = [], [], []
    hsmetrics_howmanyempty = 0

    # read and convert JSONs to pandas dataframes
    for i in range(len(hsmetrics_file_names)):
        picard_hsmetrics_dfs.append(pd.read_json( hsmetrics_file_names[i], orient='records' ))

    # get all HS metrics information
    for sindex in range(0,len(data_sample_ids)):
        # we skip samples that don't have picardtools HSmetrics output
        if type(picard_hsmetrics_dfs[sindex]) == list and picard_hsmetrics_dfs[sindex] == []:
            hsmetrics_howmanyempty += 1
        else:
            # ON/OFF TARGET
            on_target = int(picard_hsmetrics_dfs[sindex]['ON_BAIT_BASES'])
            near_target = int(picard_hsmetrics_dfs[sindex]['NEAR_BAIT_BASES'])
            off_target = int(picard_hsmetrics_dfs[sindex]['OFF_BAIT_BASES'])
            total_bases = on_target + near_target + off_target

            on_targets.append(100.0*(on_target+near_target)/total_bases if total_bases > 0 else 0)
            off_targets.append(100.0*off_target/total_bases if total_bases > 0 else 0)

            # FOLD-80
            fold_80_penalty = picard_hsmetrics_dfs[sindex]['FOLD_80_BASE_PENALTY']
            fold_80 = (fold_80 + [float(picard_hsmetrics_dfs[sindex]['FOLD_80_BASE_PENALTY'])]) if isfloat(fold_80_penalty) else (fold_80 + [0])

    # create combined data frame
    df = pd.DataFrame( list(zip(shorten(data_sample_ids), on_targets, off_targets, fold_80)), columns=['sample','percent_on_target','percent_off_target','fold-80']) if picard_hsmetrics_dfs != None and len(picard_hsmetrics_dfs) > 0 and hsmetrics_howmanyempty < len(samplenames) else pd.DataFrame({"sample": [], "percent_on_target": [], "percent_off_target": [], "fold-80": []})

    # create plots
    p1 = plotBar(list(df["sample"]), list(df["percent_on_target"]), "sample", "percent_on_target", "% Reads on-target")
    plots.append(p1.getFigureObject())

    p2 = plotBar(list(df["sample"]), list(df["percent_off_target"]), "sample", "percent_off_target", "% Reads off-target")
    plots.append(p2.getFigureObject())

    p3 = plotBar(list(df["sample"]), list(df["fold-80"]), "sample", "fold-80", "FOLD-80 Penalty Per Sample")
    plots.append(p3.getFigureObject())

    return plots
