def get_theories(logic):
    _logic = logic[:].replace('QF_', '').replace('IA', 'I').replace('RA', 'R')
    ret = []
    if _logic.find('A') != -1:
        ret.append('A')
    if _logic.find('BV') != -1:
        ret.append('BV')
    if _logic.find('R') != -1:
        ret.append('R')
    if _logic.find('I') != -1:
        ret.append('I')
    if _logic.find('FP') != -1:
        ret.append('FP')
    if _logic.find('S') != -1:
        ret.append('S')
    if _logic.find('UF') != -1:
        ret.append('UF')
    if _logic.find('DL') != -1:
        ret.append('DL')

    return sorted(ret)
