def str_to_float(s:str, default=0.0)->float:
    """
    convert str value to float
    on bad value returns default
    """
    try:
        return float(s.strip().replace(',', '.'))
    except:
        return default


def str_to_int(s:str, default=0)->int:
    """
    convert str value to int
    on bad value returns default
    """
    try:
        return int(s.strip())
    except:
        return default


def str_to_bool(s:str, default=False)->bool:
    """
    convert str boolean value to bool
    on bad value returns default
    """
    s = s.lower()
    if s == 'true' or s == 'yes' or s == 'aye' or s == 'да' or s == 'y' or s == '1':
        return True
    if s == 'false' or s == 'no' or s == 'not' or s == 'nay' or s == 'нет' or s == 'n' or s == '0':
        return False
    return default


def str_to_ibool(s:str, default=0)->int:
    """
    convert str value to integer 0 or 1
    on bad value returns default
    """
    s = s.lower()
    if s == 'true' or s == 'yes' or s == 'aye' or s == 'да' or s == 'y' or s == '1':
        return 1
    if s == 'false' or s == 'no' or s == 'not' or s == 'nay' or s == 'нет' or s == 'n' or s == '0':
        return 0
    return default