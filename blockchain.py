import random
import sys
import hashlib
import json
import time

blockchain = []
wallets = []
open_transactions=[]
origin_wallet = 0
hash_prefix = "00" #default

MINING_REWARD = 5

class Transaction:
    def __init__(self,sender,receiver,amount):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
    def JSON(self):
            return json.dumps(self.__dict__.copy(), sort_keys=True)
class Block:
    def __init__(self,nonce=0,pow_hash="",prevBlockHash=""):
        """Default constructor values create genesis block"""
        super().__init__()
            self.index = len(blockchain)
            self.prevBlockHash = prevBlockHash
            self.transactions = open_transactions
            self.nonce = nonce
            self.pow_hash = pow_hash
            self.time = time.time()

        def JSON(self):
            return json.dumps(self.__dict__.copy(), sort_keys=True)


def blockHash(block):
    x = hashlib.sha256(block.JSON()).hexdigest()
    #sort keys is necessary because serialisation not guaranteed to retain order of dictionary, since python dictionaries are orderless
    return x

def verifyPoWHash(open_transactions,last_hash,nonce_guess):
    guess_hash = hashlib.sha256((str(open_transactions)+str(last_hash)+str(nonce_guess)).encode('utf-8')).hexdigest()
    return guess_hash[0:2] == hash_prefix 

def proof_of_work(open_transactions,last_hash):
    nonce_guess = 0
    while not verifyPoWHash(open_transactions,last_hash,nonce_guess,hash_prefix):
        nonce_guess+=1
    return nonce_guess

def print_blockchain_elements():
    for block in blockchain:
        print(block.index)
        print(block)

def verifyChain():
    verifiedChain = True
    for block in blockchain[1:]:
            if (blockHash(blockchain[block.index-1]) != block.prevBlockHash):
                verifiedChain = False
                break
            elif verifyPoWHash(block.transactions,block.prevBlockHash,block.nonce):
                verifiedChain = False
                break
            
    return verifiedChain


def getBalance(walletID):
    balance = 0
    for transactionBlock in [block.transactions for block in blockchain]:
        for transaction in transactionBlock:
            if(transaction.sender==walletID):
                balance -= transaction.amount
            elif(transaction.receiver==walletID):
                balance+= transaction.amount
        
    return balance

def verify_open_transactions():
    return all([verify_transaction(t.sender,t.amount) for t in open_transactions])


def verify_transaction(sender_wallet,tx_amount):
        #determines whether sender has enough balance to make transaction; takes into account open transactions as well to prevent double spending
        balance = getBalance(sender_wallet)
        for transaction in open_transactions:
            if(transaction.sender==sender_wallet):
                balance -= transaction.amount
        
        if(balance - tx_amount >= 0):
            return True
        else:
            return False

def addTransaction(sender_wallet,receiver_wallet,tx_amount):
    if verify_transaction(sender_wallet,tx_amount):
        open_transactions.append(Transaction(sender=sender_wallet,receiver=receiver_wallet,amount=tx_amount))
        return True
    else:
        return False

def mineCoin():
    global open_transactions,blockchain
    """assigns mining reward for block to miner wallet(random for now), is simply added to list of open transactions with origin wallet as sender
        to be processed with other open transactions when new block is created.
    """
    miner = random.randint(1,len(wallets)-1)
    addTransaction(sender_wallet=origin_wallet,receiver_wallet=miner,tx_amount=MINING_REWARD)
    prev_block_hash = blockHash(blockchain[-1])
    nonce = proof_of_work(open_transactions=open_transactions,prev_block_hash)
    pow_hash = hashlib.sha256((str(open_transactions)+str(prev_block_hash)+str(nonce)).encode('utf-8'))
    #code to calculate nonce will go here
    newblock = Block(nonce,pow_hash,prev_block_hash)
    blockchain.append(newblock)
    open_transactions = []

def load_blockhain():
    global blockchain, open_transactions
    try:
        b = open("blockchain","r")
        o = open("openTransactions","r")
        blockchain = json.loads(str(b.read())) #deserializing from json strings into objects
        open_transactions = json.loads(str(o.read))
    except FileNotFoundError as ex:
        print("File Not Found.")
    except IOError as ex:
        print("Error reading blockchain from file.")
    finally:
        b.close()
        o.close()

def save_blockchain():
    try:
        b = open("blockchain","w")
        o = open("openTransactions","w")
        b.write(json.dumps([block.JSON() for block in blockchain])) #serialising into json strings and outputting to file
        o.write(json.dumps(blockchain.JSON()))
    except IOError as ex:
        print("Error writing blockchain to file.")
    finally:
        b.close()
        o.close()
   
def main():
    global blockchain,open_transactions,wallets,origin_wallet

    genesis_block = Block()
    blockchain += [genesis_block]
    wallets.append(random.randint(0,sys.maxint)) #origin wallet
    origin_wallet = wallets[0]

    waiting_for_input = True
    while waiting_for_input:
        print('Please choose')
        print('1: Add a new transaction value:')
        print('2: Output the blockchain blocks:')
        print('3: Mine new Block:')
        print('4: Enter new wallet id:')
        print('5: Get Balance:')
        print('h: Manipulate the chain')
        print('q: Quit')
        user_choice = input()
        if user_choice == '1':
            sender_wallet = input("Enter Sender Wallet:")
            recv_wallet = input("Enter Recipient Wallet:")
            tx_amount = input("Enter Amount:")
            # Add the transaction amount to the open_transactions
            if not addTransaction(sender_wallet=sender_wallet,recv_wallet=recv_wallet,tx_amount=tx_amount):
                print("Insufficient Balance.")
            else:
                print("Success.")

        elif user_choice == '2':
            print_blockchain_elements()
        elif user_choice == '3':
            mineCoin()
        elif user_choice == '4':
            wallets.append(input("Enter Wallet ID: "))
        elif user_choice == '5':
            print(getBalance(input("Enter Wallet ID: ")))
        elif user_choice == '6':
            if(verify_open_transactions()):
                print("Open Transactions OK")
            else:
                print("Invalid transactions.")
        elif user_choice == 'h':
            # Make sure that you don't try to "hack" the blockchain if it's empty
            if len(blockchain) >= 1:
                blockchain[0] = [2]
        elif user_choice == 'q':
            # This will lead to the loop to exist because it's running condition becomes False
            waiting_for_input = False
        else:
            print('Input was invalid, please pick a value from the list!')
        if not verifyChain():
            print_blockchain_elements()
            print('Invalid blockchain!')
            # Break out of the loop
            break
    else:
        print('User left!')


    print('Done!')



if(__name__=='__main__'):
    main()
