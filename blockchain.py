import random
import sys
import hashlib
import json
import time as _time 
import uuid
import binascii
import numpy
import Crypto.PublicKey.RSA as RSA
import Crypto.Random as Random

class Wallet:
    def __init__(self,public_key="", private_key=""):
        if (public_key == "" and private_key == ""):
            self.private_key , self.public_key = Wallet.generate_keys()
        else: 
            self.private_key = private_key
            self.public_key = public_key
    
    def save_keys(self):
        if (self.private_key != None) and (self.public_key != None):
            try:
                with open("wallet.txt","w") as f:
                    f.write(self.public_key)
                    f.write("\n")
                    f.write(self.private_key)
                    return True
            except IOError as ex:
                print(ex.errno)
                return False
        else: 
            return False

    def load_keys(self):
        try:
            with open("wallet.txt","r") as f:
                keys = f.readlines()
                self.public_key = keys[0]
                self.private_key = keys[1]
        except IOError as ex:
            print(ex.errno)
            return False
        return True

    @staticmethod
    def generate_keys():
        private_key = RSA.generate(bits=1024,randfunc=Random.new().read)  
        public_key = private_key.publickey().exportKey(format="DER")

        return (binascii.hexlify(private_key.exportKey(format="DER")).decode('ascii'),binascii.hexlify(public_key).decode('ascii'))

class Transaction:
    def __init__(self,sender,receiver,amount):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        
    def JSON(self):
            return json.dumps(self.__dict__, sort_keys=True)
    def __repr__(self):
        return str(self.__dict__)

class Block:
    def __init__(self,nonce=0,pow_hash="",prevBlockHash="",transactions=[],index=0,time=None):
        super().__init__()
        self.index = index
        self.transactions = transactions
        self.pow_hash = pow_hash
        if(time==None):
            self.time = _time.time()
        else:
            self.time = time
        self.prevBlockHash = prevBlockHash
        self.nonce = nonce
    def __repr__(self):
        return str(self.__dict__)

    def JSON(self):
        _dict = self.__dict__.copy()
        _dict["transactions"] = [t.__dict__.copy() for t in self.transactions]
        return json.dumps(_dict, sort_keys=True)

    def get_block_hash(self):
        x = hashlib.sha256(self.JSON().encode("utf-8")).hexdigest()
        #sort keys is necessary because serialisation not guaranteed to retain order of dictionary, since python dictionaries are orderless
        return x

class Blockchain:
    
    def __init__(self,hosting_node_id):
        self.chain = [Block()] #genesis block
        self.open_transactions = []
        #self.origin_wallet = Wallet()
        #self.wallets = [self.origin_wallet]
        self.hosting_node_id = hosting_node_id
        self.MINING_REWARD = 5
        self.hash_prefix = "00"
        self.load_blockhain()
        #self.save_blockchain()
    
    
    def verifyPoWHash(self,transactions,last_hash,nonce_guess):
        guess_hash = hashlib.sha256((str(transactions)+str(last_hash)+str(nonce_guess)).encode('utf-8')).hexdigest()
        return guess_hash[0:2] == self.hash_prefix 

    def proof_of_work(self,last_hash):
        nonce_guess = 0
        while not self.verifyPoWHash(self.open_transactions,last_hash,nonce_guess):
            nonce_guess+=1
        return nonce_guess

    def print_blockchain_elements(self):
        for block in self.chain:
            print(block.index)
            print(block)

    def verifyChain(self):
        verifiedChain = True
        for block in self.chain[1:]:
                if (self.chain[block.index-1].get_block_hash() != block.prevBlockHash):
                    verifiedChain = False
                    break
                elif not self.verifyPoWHash(block.transactions,block.prevBlockHash,block.nonce):
                    verifiedChain = False
                    break
                
        return verifiedChain

    def getBalance(self,walletID):
        balance = 0
        for transactionBlock in [block.transactions for block in self.chain]:
            for transaction in transactionBlock:
                if(transaction.sender==walletID):
                    balance -= transaction.amount
                elif(transaction.receiver==walletID):
                    balance += transaction.amount
            
        return balance

    def verify_transaction(self,sender_wallet,tx_amount):
        #determines whether sender has enough balance to make transaction; takes into account open transactions as well to prevent double spending
    
        balance = self.getBalance(sender_wallet)
        for transaction in self.open_transactions:
            if(transaction.sender==sender_wallet):
                balance -= transaction.amount
        
        if(balance - tx_amount >= 0):
            return True
        else:
            return False

    def verify_open_transactions(self):
        return all([self.verify_transaction(t.sender,t.amount) for t in self.open_transactions])


    def addTransaction(self,sender,receiver,tx_amount):
        if self.verify_transaction(sender,tx_amount):
            self.open_transactions.append(Transaction(sender=sender,receiver=receiver,amount=tx_amount))
            self.save_blockchain()
            return True
        else:
            return False

    def mineCoin(self):
        #global open_transactions,blockchain
        """assigns mining reward for block to miner wallet(random for now), is simply added to list of open transactions with origin wallet as sender
            to be processed with other open transactions when new block is created.
        """
        self.open_transactions.append(Transaction(sender='MINING' ,receiver=self.hosting_node_id,amount=self.MINING_REWARD))
        prev_block_hash = self.chain[-1].get_block_hash()
        nonce = self.proof_of_work(last_hash=prev_block_hash)
        pow_hash = hashlib.sha256((str(self.open_transactions)+str(prev_block_hash)+str(nonce)).encode('utf-8')).hexdigest()
        #code to calculate nonce will go here
        newblock = Block(nonce,pow_hash,prev_block_hash,self.open_transactions,len(self.chain))
        self.chain.append(newblock)
        self.open_transactions = []
        self.save_blockchain()

    def load_blockhain(self):
        try:
            b_f = open("blockchain","r")
            o_f = open("openTransactions","r")
            
            b_s = json.loads(str(b_f.read()))
            b_dicts = [json.loads(b) for b in b_s]
            self.chain = []

            for b in b_dicts:
                transactions = [Transaction(sender = tx['sender'], receiver = tx['receiver'], amount= tx['amount']) for tx in b['transactions']]
                block = Block(time=b['time'] ,index=b['index'], prevBlockHash=b['prevBlockHash'], transactions=transactions, pow_hash=b['pow_hash'])
                self.chain.append(block)

            o_s = o_f.read()
            self.open_transactions = [json.loads(t) for t in json.loads(o_s)]
            b_f.close()
            o_f.close()
        except FileNotFoundError:
            print("File Not Found.")
        except IOError:
            print("Error reading blockchain from file.")

           

    def save_blockchain(self):
        try:
            b = open("blockchain","w")
            o = open("openTransactions","w")
            b_a = [block.JSON() for block in self.chain]
            b_s = json.dumps(b_a)
            o_s = json.dumps([transaction.JSON() for transaction in self.open_transactions])

            b.write(b_s) #serialising into json strings and outputting to file
            o.write(o_s)
        except Exception as err:
            print("Error writing blockchain to file.")
        finally:
            b.close()
            o.close()
   
class Node:
    def __init__(self,blockchain=None,wallet=None):
        self.id = str(uuid.uuid4())
        
        if wallet != None:
            self.wallet = wallet
        else:
            self.wallet = Wallet()

        if blockchain == None:
            self.blockchain = Blockchain(self.wallet.public_key)
        else:
            self.blockchain = blockchain 
        
    def new_wallet(self):
        print("Generating New Wallet:\n")
        self.wallet = Wallet()
        print(f"Private Key:\n{self.wallet.private_key}")
        print(f"Public Key:\n{self.wallet.public_key}")

    def listen_for_input(self):
        waiting_for_input = True
        while waiting_for_input:
            print('Please choose')
            print('1: Add a new transaction value')
            print('2: Mine a new block')
            print('3: Output the blockchain blocks')
            print('4: Check transaction validity')
            print('5: Create wallet')
            print('6: Load wallet')
            print('7: Save keys')
            print('8: Get Balance')
            print('9: Check Chain Validity')
            print('q: Quit')
            user_choice = input()
            if user_choice == '1':
                #sender_wallet = input("Enter Sender Wallet:")
                recv_wallet = input("Enter Recipient Wallet:")
                tx_amount = input("Enter Amount:")
                # Add the transaction amount to the open_transactions
                if not self.blockchain.addTransaction(sender_wallet=self.id,receiver_wallet=recv_wallet,tx_amount=tx_amount):
                    print("Insufficient Balance.")
                else:
                    print("Success.")

            elif user_choice == '2':
                self.blockchain.mineCoin()
            elif user_choice == '3':
                self.blockchain.print_blockchain_elements()
            elif user_choice == '5':
                self.wallet = Wallet()
            elif user_choice == '8':
                print(self.blockchain.getBalance(self.id))
            elif user_choice == '4':
                if(self.blockchain.verify_open_transactions()):
                    print("Open Transactions OK")
                else:
                    print("Invalid transactions.")
            elif user_choice == '6':
                self.wallet.load_keys()
                self.blockchain = Blockchain(self.wallet.public_key)
            elif user_choice == '7':
                self.wallet.save_keys()
            elif user_choice == '9':  
                self.blockchain.print_blockchain_elements()
                if(not self.blockchain.verifyChain()):
                    print('Invalid blockchain!')
                # Break out of the loop
            elif user_choice == 'q':
                # This will lead to the loop to exist because it's running condition becomes False
                waiting_for_input = False
            else:
                print('Input was invalid, please pick a value from the list!')
            


        


def main():
    node = Node()
    node.listen_for_input()

if(__name__=='__main__'):
    main()
