def custom_error_handler(function):
    def new_func(*args):
        new_args = list(args)
        if check_for_suspisious_chars(new_args):
            raise AttributeError(f"Invalid argument found for function {function.__name__}")    
        return function(*new_args)
    new_func.__name__ = function.__name__
    return new_func

def check_for_suspisious_chars(request_params:list):
    for key,val in enumerate(request_params):
        if type(val) != str:
            continue
        request_params[key] = pre_proc_string(val)
        if run_checks_for_str(request_params[key]):
            return True
    return False
        
def pre_proc_string(to_proc:str):
    ref = "''"
    if to_proc.find("'")!=-1:
        to_proc = ref.join(to_proc.split("'"))
    if to_proc == -1 or to_proc == "-1" or to_proc is None or to_proc == "":
        to_proc = "NULL"
    return to_proc

def run_checks_for_str(to_check:str):
    sus_chars = ["--"]
    for ch in sus_chars:
        if to_check.upper().find(ch) !=-1:
            return True
    return False
