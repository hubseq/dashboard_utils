#
# dashboard_file_utils
#
# Utility functions for retrieving and writing files
#
import global_keys
sys.path.append('global_utils/src/')
import file_utils

def searchDataFile( _folder, _extensions, _file_system = 'local' ):
    """ Given a folder to search, searches and returns data files matching the input extensions.

    _folder:     STRING e.g., '/myfolder/subfolder/'
    _extensions: LIST e.g., ['.bam^', '^hepg2', 'I1'] where
                 '^.bam' => file ends with BAM
                 'hepg2^' => file begins with hepg2
                 'I1' => file contains the word I1

    return: LIST of data file JSONs
    """
    # local function for searching for a pattern match
    def _findMatch(f, p):
        _isMatch = False
        # file extension at end of filename
        if p[0]=='^':
            if f.endswith(p[1:]):
                _isMatch = True
        # prefix - file extension at beginning of filename
        elif p[-1]=='^':
            if f.startswith(p[0:-1]):
                _isMatch = True
        # search pattern ONLY in the middle
        elif p.rfind('^') > p.find('^'):
            i = p.find('^')
            j = p.rfind('^')
            if f.find(p[i+1:j]) >= 0 and not f.startswith(p[i+1:j]) and not f.endswith(p[i+1:j]):
                _isMatch = True
        # search pattern anywhere in file name
        else:
            if f.find(p) >= 0:
                _isMatch = True
        return _isMatch

    # main search through all files in the directory
    all_files = file_utils.listFiles( _folder, _file_system)
    matched_files = []
    for f in all_files:
        isMatch = False
        for p in _extensions:
            if _findMatch(f, p):
                matched_files.append(f)
    return matched_files


def getDataFiles( _sample_file_search_json_list, _file_system = 'local' ):
    """ Given a list of JSON file search queries, function searches and returns found data files (as JSON).
    See repo > global_utils > file_utils.py for JSON specifications for file search queries and data files.

    _sample_file_search_json_list: LIST(JSON) - list of search query JSONs

    return: LIST(JSON) - list of data file JSONs

    >>> getDataFiles([])
    []
    """
    _sample_file_json_list = []
    try:
        # if single JSON then convert to single-element list
        if type(_sample_file_search_json_list ) == type({'a': 2}):
            _sample_file_search_json_list = [_sample_file_search_json_list]
        elif type(_sample_file_search_json_list ) == type([1,2]):
            pass
        else:
            raise IOError

        for _sample_file_search_json in _sample_file_search_json_list:
            file_folder = _sample_file_search_json[global_keys.KEY_FILE_LOCATION]
            file_type = _sample_file_search_json[global_keys.KEY_FILE_TYPE]
            file_extensions = _sample_file_search_json[global_keys.KEY_FILE_EXTENSIONS]
            sample_files = searchDataFile( file_folder, file_extensions, _file_system )
            for sample_file in sample_files:
                sample_file_json = file_utils.createDataFileJSON(sample_file,
                                              file_folder,
                                              file_type)
                _sample_file_json_list.append(sample_file_json)

    except IOError as e:
        print('ERROR in getDataFiles(): input needs to be a list of search JSONs.')
    return _sample_file_json_list

def getSamples(userid, pipelineid, selected_runs, selected_sample, moduleids, extensions, filetype):
    """ Get all sample files and IDs of a particular file type.
    Assumes the standard folder structure for pipeline runs.

    Return LIST of filenames, LIST of sample IDs (ordered)
    """
    # get file folders
    data_file_folders = file_utils.getRunSampleOutputFolders(userid, pipelineid, selected_runs, moduleids, selected_samples)
    # get file search JSONs (search these folders)
    data_file_search_jsons = file_utils.createSearchFileJSONs(data_file_folders, extensions, filetype)
    # get the data files in these folders
    data_file_jsons = dfu.getDataFiles( data_file_search_jsons )
    # return data file names and sample IDs
    return file_utils.getDataFileNames( data_file_jsons ), file_utils.getDataSampleIds( data_file_jsons )
