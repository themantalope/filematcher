import re
import pandas as pd
import os
from scipy import stats
import warnings
# default pattern to break filenames: '([0-9a-zA-Z]+)'

def compose_path(dirpath, fn):
    return os.path.join(dirpath, fn)


class FileMatcher(object):

    def _check_if_unique(self, substring, index, set_list):
        check_list = set_list[0:index] + set_list[index+1:]
        return all(substring not in fn for fn in check_list)

    def __init__(self, pattern='([0-9a-zA-Z]+)'):
        self.patt = re.compile(pattern)
        self.unique_dict = {}
        self.non_unique = []
        self.non_matched = []
        self.unique = {}

    def find_unique_ids_in_file_list(self, file_list, name, use_mode_length=True, return_output=False, max_length=int(1e3):
        """
        returns a set of unique ids
        """
        patt = re.compile(name)
        file_list = [f for f in file_list if re.search(patt, f)]
        
        pattern_sets = [set(re.findall(self.patt, fn)) for fn in file_list]
        counts = {}
        for ps in pattern_sets:
            for p in ps:
                if p in counts:
                    counts[p] += 1
                else:
                    counts[p] = 1
                    
        
        # get the mode of string length of the counts
        str_lengths = [len(str(k)) for k,v in counts.items() if v == 1]
        str_mode_len = stats.mode(str_lengths)[0][-1]
        # print('mode length', str_mode)
        
        uniques = []
        for k, v in counts.items():
            if use_mode_length and v == 1 and len(k) == str_mode_len:
                uniques.append(k)
            elif v == 1 and not use_mode_length and len(k) < max_length:
                uniques.append(k)
            elif v > 1:
                self.non_unique.append(k)
        
        self.unique = set(uniques)
        self.unique_dict = {k:{} for k in self.unique}
        if return_output: return self.unique, self.non_unique

    

    def match_list_to_unique_ids(self, file_list, name_patt='.*', key_name=None, return_output=False, warn_on_dup=True):
        assert self.unique is not None, 'you must have already filtered a list and gotten unique ids.'
        patt = re.compile(name_patt)
        file_list = [f for f in file_list if re.search(patt, f)]
        pattern_sets = [set(re.findall(self.patt, fn)) for fn in file_list]
        unique_keys = set(list(self.unique))
        
        if key_name is None:
            key_name = name_patt
        
        for (ps, fn) in zip(pattern_sets, file_list):
            inter = unique_keys.intersection(ps)
            if len(inter) == 1:
                key = inter.pop()
                
                if key_name in self.unique_dict[key] and warn_on_dup:
                    warnings.warn('multiple files with unique key {k}, overwriting with {f}'.format(k=key, f=fn))
                self.unique_dict[key].update({key_name:fn})
            elif len(inter) == 0:
                self.non_matched.append(fn)
            elif len(inter) > 1:
                raise ValueError("something went wrong, more than 1 match... : {i}".format(i=inter))
        
        if return_output: return self.unique_dict

    def match_lists_to_unique_ids(self, files_lists, names_list, key_names=None, return_output=False):
        if key_names is not None:
            assert len(key_names) == len(names_list), 'names_list and key_names must be the same length'
        else:
            key_names = [None for i in range(len(names_list))]
            
        for fl, name, kn in zip(files_lists, names_list, key_names):
            self.match_list_to_unique_ids(fl, name, kn)

        if return_output: return self.unique_dict


    def export_as_pandas_dataframe(self):
        assert self.unique_dict is not None
        df = pd.DataFrame()
        data = self.unique_dict.copy()
        df = df.from_dict(data, orient='index')
        df.sort_index(inplace=True)
        return df
    
    def collect_file_names(self, root_dir, patts, ext=None):
        # print(exts)
        # print(type(exts))
        patt = re.compile('|'.join([str(s) for s in patts]))
        if ext is None:
            ext = '.*'
        ext_patt = re.compile(ext)
        results = []
        for dp, _, fn in os.walk(root_dir):
            if len(fn) == 0:continue
            else:
                for f in fn:
                    if re.search(patt, compose_path(dp, f)) and re.search(ext_patt, f):
                        results.append(compose_path(dp, f))

        return results

    def load_pandas_dataframe(self, df):
        self.unique_dict = df.to_dict('index')
