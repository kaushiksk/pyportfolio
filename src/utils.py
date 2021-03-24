import logging

def and_filter(filters):
    return lambda x: all(f(x) for f in filters)

def or_filter(filters):
    return lambda x: any(f(x) for f in filters)

def filter_dict(mydict, keys):
    return {key: mydict[key] for key in keys }

logging.basicConfig()
logger = logging.getLogger('portfolio-cli')
logger.setLevel(logging.INFO)