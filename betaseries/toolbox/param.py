from sys import argv

from betaseries.toolbox.logger import log


def get_params():
    init_param = []
    log('----------------')
    log(repr(argv))
    log('----------------')
    if len(argv) > 2 and len(argv[2]) >= 2:
        cleaned_params = argv[2].replace('?', '')
        pairs_of_params = cleaned_params.split('&')
        init_param = {}
        for i in range(len(pairs_of_params)):
            splitparams = pairs_of_params[i].split('=')
            if (len(splitparams)) == 2:
                init_param[splitparams[0]] = splitparams[1]
    return init_param
