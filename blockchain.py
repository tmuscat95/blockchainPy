blockchain = []
open_transactions = []
wallets = []

def blockHash():
	return None

def print_blockchain_elements():
	for block in blockchain:
		print(block.index)
		print(block)

class Block:
	__init__():
		if len(blockchain)>0:
			self.prevBlockHash = blockHash(blockchain[-1])
		else:
			self.prevBlockHash = ""
			
		self.transactions = open_transactions
		self.index = len(blockchain)

class Transaction:
	__init__(sender,receiver,amount):
		self.sender = sender
		self.receiver = receiver
		self.amount = amount

def verifyChain():
	verified = True
	for block in blockchain:
		if block.index == 0:
			continue
		else
			if blockHash(blockchain[block.index-1]) != block.prevBlockHash:
				verified = False
				break
	return verified
	
genesis_block = Block()
blockchain += genesis_block

while waiting_for_input:
    print('Please choose')
    print('1: Add a new transaction value')
    print('2: Output the blockchain blocks')
    print('h: Manipulate the chain')
    print('q: Quit')
    user_choice = get_user_choice()
    if user_choice == '1':
		sender_wallet = input("Enter Sender Wallet")
		recv_wallet = input("Enter Recipient Wallet")
        tx_amount = input("Enter Amount")
        # Add the transaction amount to the blockchain
        blockchain.append(Transaction(sender=sender_wallet,receiver=recv_wallet,amount=tx_amount))
    elif user_choice == '2':
        print_blockchain_elements()
    elif user_choice == 'h':
        # Make sure that you don't try to "hack" the blockchain if it's empty
        if len(blockchain) >= 1:
            blockchain[0] = [2]
    elif user_choice == 'q':
        # This will lead to the loop to exist because it's running condition becomes False
        waiting_for_input = False
    else:
        print('Input was invalid, please pick a value from the list!')
    if not verify_chain():
        print_blockchain_elements()
        print('Invalid blockchain!')
        # Break out of the loop
        break
else:
    print('User left!')


print('Done!')






