def args(*args,**kwargs):
    def _decorator(func):
        func.__dict__.setdefault("arguments",[]).insert(0,(args,kwargs))
        return func
    return _decorator
