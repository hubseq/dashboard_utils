#
# dashboard_file_utils
#
# Utility functions for retrieving and writing files given Dashboard inputs.
# Makes heavy use of the general file_utils script within the global utils repository.
#
import sys
sys.path.append('global_utils/src/')
import global_keys
import file_utils

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
    (data_files, sample_ids) = file_utils.getDataFiles(data_file_folders, extensions, extensions2exclude )
    return data_files, sample_ids

    # get file search JSONs (search these folders)
    # data_file_search_jsons = file_utils.createSearchFileJSONs(data_file_folders, extensions, filetype)
    # get the data files in these folders
    # data_file_jsons = file_utils.getDataFiles( data_file_search_jsons )
    # return data file names and sample IDs
    # return file_utils.getDataFileNames( data_file_jsons ), file_utils.getDataSampleIds( data_file_jsons )
