def get_transaction_type_filter(transaction_type):
    return lambda transaction: transaction["type"] == transaction_type
    
def get_transaction_older_than_filter(days):
    return lambda transaction: transaction["Days"] > days