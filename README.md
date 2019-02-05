A simple decorator to cache the results of function calls. 

## Installation

```bash
pip install cache_em_all
```


## Example

```python
from cache_em_all import Cachable

@Cachable("answer.json")
def answer_to(question):
    if question == "life":
        import time
        time.sleep(236500000000000)
        return 42

answer_to("life") # Takes 7.5 million years
answer_to("life") # Pretty much instant
```

After the first call to `answer_to`, the result of the function is stored in a file `cache/answer/answer__life.json`.
When the function is called again (with the same parameters), instead of executing the function, the decorator will get the result from the file.

## Advanced usage

### File types
Various file types are supported. 

| extension  | Description  |
|-----|---|
| csv | Uses pandas to save the result in a csv file. The return value for the function must be a DataFrame or Series. |
| json| Saves the result in a json file. Useful for lists, dictionaries and primitive types. |
| pkl | Pickles the return value. Return type can be just about anything. May not work well for large (>~2GB) files |
| pa | Uses pyarrow to save files. This is generally faster than pkl and supports larger files (tested up to 50GB) |

### Versioning
The `Cachable` decorator can accept a version number. This is useful for when you update a function. For example,

You had the following code:
```python
from cache_em_all import Cachable

@Cachable("add.json")
def add(x, y):
    return x + x
```

This is a bug (should be `x+y`, not `x+x`), but you've run this function multiple times and there are lots of cached results. Rather than manually deleting
the cache folder, you can bump the version number (version numbers start at 0). 

```python
from cache_em_all import Cachable

@Cachable("add.json", version=1)
def add(x, y):
    return x + y
```
Now next time the function is called it will invalidate the cache and re-run the function.

Do not use this feature in multi-processing code because the writes to the version file do not (yet) use locks.

### Folder
By default all cached files are stored in a folder called `cache`. This can be changed by passing `folder` to `Cachable`.
```python
from cache_em_all import Cachable

@Cachable("add.json", folder="/mnt/ram/fastcache")
def add(x, y):
    return x + x
```

### Disable cache
You can also disable the cache by setting `use` to `False`. 
```python
from cache_em_all import Cachable

@Cachable("add.json", use=False)
def add(x, y):
    return x + x
```
This can be useful for debugging or optmizing the function.
