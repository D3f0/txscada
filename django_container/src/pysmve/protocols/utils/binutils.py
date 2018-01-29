def str2hexa(data):
    '''Raw data to hex representation'''
    data = ' '.join([ '%.2x' % ord(x) for x in str(data)])
    return data.upper()
