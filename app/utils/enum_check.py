def check_enum(val, enum_value):
    if type(val) is list and type(enum_value) is list:
        if len(val) != len(enum_value):
            return False
        for i in range(len(val)):
            if val[i] not in enum_value[i]:
                return False
        return True
    elif type(val) is str and type(enum_value) is dict:
        return val in enum_value.keys()
    else:
        return False
