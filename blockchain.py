blockchain = []
open_transactions = []
wallets = []

def blockHash(block):
    return None

def print_blockchain_elements():
    for block in blockchain:
        print(block.index)
        print(block)


class Transaction:
    def __init__(self,sender,receiver,amount):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount

class Block:
    def __init__(self):
        super().__init__()
        if(len(blockchain)>0):
            self.index = len(blockchain)
            self.prevBlockHash = blockHash(blockchain[-1])
            self.transactions = open_transactions
            open_transactions = []
        else:
            self.index = 0
            self.prevBlockHash = ""
            self.transactions = []

