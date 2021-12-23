#
# dashboard_file_utils
#
# Utility functions for retrieving and writing files given Dashboard inputs.
# Makes heavy use of the general file_utils script within the global utils repository.
#
sys.path.append('global_utils/src/')
import global_keys
import file_utils


def getSamples(userid, pipelineid, selected_runs, selected_sample, moduleids, extensions, filetype):
    """ Get all sample files and IDs of a particular file type, given the list of choices on the dashboard.
    Assumes the standard folder structure for pipeline runs.

    Return LIST of filenames, LIST of sample IDs (ordered)
    """
    # get file folders
    data_file_folders = file_utils.getRunSampleOutputFolders(userid, pipelineid, selected_runs, moduleids, selected_samples)
    # get file search JSONs (search these folders)
    data_file_search_jsons = file_utils.createSearchFileJSONs(data_file_folders, extensions, filetype)
    # get the data files in these folders
    data_file_jsons = file_utils.getDataFiles( data_file_search_jsons )
    # return data file names and sample IDs
    return file_utils.getDataFileNames( data_file_jsons ), file_utils.getDataSampleIds( data_file_jsons )
