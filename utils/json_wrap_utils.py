

def _wrap(args):
    if isinstance(args, str) or isinstance(args, int) or isinstance(args, float) or isinstance(args, bool):
        return {"value" : args}
    elif isinstance(args, list):
        return {"list": args}
    elif isinstance(args, dict):
        return args 
    else:
        raise Exception("Argument type not supported: ", args)
    
def _stringify(args):
    if isinstance(args, list):
        return ",".join([_stringify(arg) for arg in args])
    else :
        return str(args)
    


    
def _stringify_list(args):
    if isinstance(args, list):
        return [_stringify(arg) for arg in args]
    else:
        return args
    
    
def _stringify_and_wrap_list(args):
    return _wrap(_stringify_list(args))