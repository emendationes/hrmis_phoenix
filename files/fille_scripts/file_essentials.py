def file_allowed(filename:str,allowed_extensions:dict)->bool:
    return filename.rsplit('.',1)[1].lower() in allowed_extensions

