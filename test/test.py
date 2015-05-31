#!coding=utf8
# import time


d = {
    '211': 112,
    '213': 111,
    '215': 111,
    '21': 11,
    '31': 3,
    '11': 44,
    '111232': 0,
    '1111111': 0,
    '11111': 0,
    '1111': 0,
}


def sort_dict_by_value_return_keys(d):
    l = []
    temp = d.items()
    for value in sorted(d.values()):
        index = 0
        for k, v in temp:
            if v == value:
                l.append(k)
                del temp[index]
                index += 1
                break
            index += 1
    return l


for i in sort_dict_by_value_return_keys(d):
    print i