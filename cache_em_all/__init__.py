import os
import pickle
import json

import pandas as pd
import pyarrow as pa


cache_folder = "cache"


def _ensure_dir(path):
    if not os.path.isdir(path):
        os.makedirs(path)

def _read_json_file(fname):
    with open(fname) as jsonFile:
        data = json.load(jsonFile)
        return data

def _write_json_file(f, data):
    with open(f, 'w') as jsonFile:
        json.dump(data, jsonFile)

class Cachable(object):
    def __init__(self, fname, folder=cache_folder, use=True, version=0):
        self.fname = fname
        self.ext = self._get_extension()

        _ensure_dir(folder)
        self.path = os.path.join(folder, fname)
        self.use_cache = use
        self.version = version

        self.version_file = os.path.join(folder, "versions.json")
        if not os.path.isfile(self.version_file):
            _write_json_file(self.version_file, {})


    def _load_file(self, file_path):
        if self.ext == ".json":
            return _read_json_file(file_path)
        elif self.ext == ".csv":
            return pd.read_csv(file_path, index_col=0, parse_dates=True)
        elif self.ext == ".pkl":
            with open(file_path, "rb") as f:
                return pickle.load(f)
        elif self.fname.endswith(".pa"):
            return pa.read_serialized(pa.OSFile(file_path, "rb")).deserialize()
        else:
            raise Exception("Unknown file type")


    def _save_file(self, file_path, data):
        if self.ext == ".json":
            _write_json_file(file_path, data)
        elif self.ext ==".csv":
            data.to_csv(file_path)
        elif self.ext == ".pkl":
            with open(file_path, "wb") as f:
                pickle.dump(data, f)
        elif self.fname.endswith(".pa"):
            open(file_path, "wb").write(pa.serialize(data).to_buffer())
        else:
            raise Exception("Unknown file type")


    def _get_extension(self):
        if self.fname.endswith(".json"):
            return ".json"
        elif self.fname.endswith(".csv"):
            return ".csv"
        elif self.fname.endswith(".pkl"):
            return ".pkl"
        elif self.fname.endswith(".pa"):
            return ".pa"
        else:
            raise Exception("Unknown file type")

    def str_for_arg(self, value):
        if isinstance(value, (int, float, str, bool)):
            return str(value)
        if isinstance(value, (list, pd.Series)):
            return None
        if isinstance(value, dict):
            return str(hash(json.dumps(value, sort_keys=True)))

        return None

    def _get_full_path(self, *args, **kwargs):
        path = self.path
        ext = self.ext

        path = path[:path.rindex(ext)]
        _ensure_dir(path)

        fname = os.path.basename(path)


        add_to_path = []

        if args:
            add_to_path.extend([self.str_for_arg(s) for s in args])

        if kwargs:
            _kwargs = [self.str_for_arg(x) for x in kwargs.values()]
            add_to_path.extend(x for x in sorted(_kwargs))

        if add_to_path:
            add_to_path = filter(lambda x: x is not None, add_to_path)
            fname = fname + "__" + "__".join(add_to_path).replace("/", "-")

        path = os.path.join(path, fname + ext)
        return path


    def __call__(self, func):
        def wrapped_f(*args, **kwargs):
            path = self._get_full_path(*args, **kwargs)

            version_data = _read_json_file(self.version_file)

            if self.use_cache and os.path.isfile(path) and version_data.get(self.fname, 0) == self.version:
                res = self._load_file(path)
            else:
                res = func(*args, **kwargs)
                self._save_file(path, res)

            version_data[self.fname] = self.version
            _write_json_file(self.version_file, version_data)

            return res

        return wrapped_f