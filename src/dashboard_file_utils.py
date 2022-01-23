#
# dashboard_file_utils
#
# Utility functions for retrieving and writing files given Dashboard inputs.
# Makes heavy use of the general file_utils script within the global utils repository.
#
import sys, os
sys.path.append('global_utils/src/')
import global_keys
import file_utils

DASHBOARD_CONFIG_DIR = './'

# dfu.getSamples(dsu.ROOT_FOLDER, teamid, [userid], [pipelineid], selected_runs, selected_samples, [], ['fastqc'], ['^HTML'])
def getSamples(team_root_folder, teamid, userids, pipelineids, selected_runs, selected_samples, moduleids, extensions = [], extensions2exclude = []):
    """ Get all sample files and IDs of a particular file type, given the list of choices on the dashboard.
    Assumes the standard folder structure for pipeline runs.

    team_root_folder: STRING - 's3://' or '/'

    Return LIST of filenames, LIST of sample IDs (ordered)
    """
    # get file folders
    data_file_folders = file_utils.getRunSampleOutputFolders(team_root_folder, teamid, userids, pipelineids, selected_runs, selected_samples, moduleids)
    # get data files matching extension patterns in these folders
    data_file_json_list = file_utils.getDataFiles(data_file_folders, extensions, extensions2exclude )
    return data_file_json_list

    # get file search JSONs (search these folders)
    # data_file_search_jsons = file_utils.createSearchFileJSONs(data_file_folders, extensions, filetype)
    # get the data files in these folders
    # data_file_jsons = file_utils.getDataFiles( data_file_search_jsons )
    # return data file names and sample IDs
    # return file_utils.getDataFileNames( data_file_jsons ), file_utils.getDataSampleIds( data_file_jsons )


def getDashboardConfigJSON( pipeline_id ):
    """ Given a pipeline ID, loads and returns a JSON containing info for loading a dashboard for this pipeline.
    Config file must be named 'dashboard_config.<PIPELINE_ID>.json'
    """
    config_file = os.path.join(DASHBOARD_CONFIG_DIR, 'dashboard_config.{}.json'.format(pipeline_id))
    return file_utils.loadJSON( config_file )


def getSessionDataFiles( session_dataframe, pipelineid, sessionid, analysis ):
    """ Returns the list of data files currently loaded in this session of the pipeline dashboard.
    Follows the JSON specification for dashboard sessions.
    """
    return session_dataframe[pipelineid][sessionid][analysis]


def saveSessionDataFiles( session_dataframe, data_files_list, pipelineid, sessionid, analysis):
    """ Save or update data files list in the session data frame.
    This will prevent re-rendering of a dashboard if the files list (and hence the graphs) haven't changed.
    Follows the JSON specification for dashboard sessions.
    """
    session_dataframe[pipelineid][sessionid][analysis] = data_files_list
    return session_dataframe
