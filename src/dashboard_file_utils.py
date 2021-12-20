#
# dashboard_file_utils
#
# Utility functions for retrieving and writing files
#
import global_keys
import file_utils

def searchDataFile( _sample_file_search_json, _file_system = 'local' ):
    """
    Given a file search JSON, searches and returns data files.

    return: LIST of data file JSONs
    """
    # local function for searching for a pattern match
    def _findMatch(f, p):
        _isMatch = False
        # prefix - file extension at beginning of filename
        if p[0]=='^':
            if f.startswith(p[1:]):
                _isMatch = True
        # file extension at end of filename
        elif p[-1]=='^':
            if f.endswith(p[0:-1]):
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
    all_files = file_utils.listFiles( _sample_file_search_json[global_keys.KEY_FILE_LOCATION], _file_system)
    matched_files = []
    for f in all_files:
        isMatch = False
        for p in _sample_file_search_json[global_keys.KEY_FILE_EXTENSIONS]:
            if _findMatch(f, p):
                matched_files.append(f)
    return matched_files


def getDataFiles( _sample_file_search_json_list, _file_system = 'local' ):
    """
    search and return data file JSONs, given list of files to search

    _sample_file_search_json_list: LIST(JSON) - list of search JSONs

    return: LIST(JSON) - list of data file JSONs
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
            sample_files = searchDataFile( file_folder, _file_system )
            for sample_file in sample_files:
                sample_file_json = file_utils.createDataFileJSON(sample_file,
                                              file_folder,
                                              file_utils.getUserIdFromLocation(file_folder),
                                              file_utils.getRunIdFromLocation(file_folder),
                                              file_utils.getModuleIdFromLocation(file_folder),
                                              file_type,
                                              file_utils.getFileIdFromLocation(file_folder))
                _sample_file_json_list.append(sample_file_json)
    
    except IOError as e:
        print('ERROR in getDataFiles(): input needs to be a list of search JSONs.')
    return _sample_file_json_list
