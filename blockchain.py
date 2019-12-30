blockchain = [1]

def get_last_blockchain_value():
    return blockchain[-1]

def add_value(last_transaction_amount=0,transaction_amount=0):
    blockchain.append([last_transaction_amount,transaction_amount])
    print(blockchain)

tx_amount = float(input("Enter transaction amount:"))
add_value(last_transaction_amount=blockchain[-1],transaction_amount=tx_amount)
