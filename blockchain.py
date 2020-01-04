import random
import sys
import hashlib
import json
import time
import uuid
import binascii
import numpy
import Crypto.PublicKey.RSA as RSA
import Crypto.Random as Random

class Wallet:
    def __init__(self):
        self.private_key , self.public_key = Wallet.generate_keys()
        
    @staticmethod
    def generate_keys():
        private_key = RSA.generate(bits=1024,randfunc=Random.new().read)  
        public_key = private_key.publickey().exportKey(format="DER")

        return (binascii.hexlify(private_key),binascii.hexlify(public_key))

class Transaction:
    def __init__(self,sender,receiver,amount):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        
    def JSON(self):
            return json.dumps(self.__dict__.copy(), sort_keys=True)
    def __repr__(self):
        return str(self.__dict__)

class Block:
    def __init__(self,nonce=0,pow_hash="",prevBlockHash="",transactions=[],index=0):
        super().__init__()
        self.index = index
        self.transactions = transactions
        self.pow_hash = pow_hash
        self.time = time.time()
        self.prevBlockHash = prevBlockHash
        self.nonce = nonce
    def __repr__(self):
        return str(self.__dict__)

    def JSON(self):
        return json.dumps(self.__dict__.copy(), sort_keys=True)

    def get_block_hash(self):
        x = hashlib.sha256(self.JSON()).hexdigest()
        #sort keys is necessary because serialisation not guaranteed to retain order of dictionary, since python dictionaries are orderless
        return x

class Blockchain:
    
    def __init___(self,hosting_node_id):
        self.blockchain = [Block()] #genesis block
        self.open_transactions = []
        self.origin_wallet = Wallet()
        self.wallets = [self.origin_wallet]
        self.hosting_node_id = hosting_node_id
        self.MINING_REWARD = 5
        self.hash_prefix = "00"
    
    def verifyPoWHash(self,transactions,last_hash,nonce_guess):
        guess_hash = hashlib.sha256((str(transactions)+str(last_hash)+str(nonce_guess)).encode('utf-8')).hexdigest()
        return guess_hash[0:2] == self.hash_prefix 

    def proof_of_work(self,last_hash):
        nonce_guess = 0
        while not self.verifyPoWHash(self.open_transactions,last_hash,nonce_guess):
            nonce_guess+=1
        return nonce_guess

    def print_blockchain_elements(self):
        for block in self.blockchain:
            print(block.index)
            print(block)

    def verifyChain(self):
        verifiedChain = True
        for block in self.blockchain[1:]:
                if (self.blockchain[block.index-1].get_block_hash() != block.prevBlockHash):
                    verifiedChain = False
                    break
                elif not self.verifyPoWHash(block.transactions,block.prevBlockHash,block.nonce):
                    verifiedChain = False
                    break
                
        return verifiedChain

    def getBalance(self,walletID):
        balance = 0
        for transactionBlock in [block.transactions for block in self.blockchain]:
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


    def addTransaction(self,sender_wallet,receiver_wallet,tx_amount):
        if self.verify_transaction(sender_wallet,tx_amount):
            self.open_transactions.append(Transaction(sender=sender_wallet,receiver=receiver_wallet,amount=tx_amount))
            return True
        else:
            return False

    def mineCoin(self):
        #global open_transactions,blockchain
        """assigns mining reward for block to miner wallet(random for now), is simply added to list of open transactions with origin wallet as sender
            to be processed with other open transactions when new block is created.
        """
        miner = self.hosting_node_id
        self.addTransaction(sender_wallet=self.origin_wallet,receiver_wallet=miner,tx_amount=self.MINING_REWARD)
        prev_block_hash = self.blockchain[-1].get_block_hash()
        nonce = self.proof_of_work(last_hash=prev_block_hash)
        pow_hash = hashlib.sha256((str(self.open_transactions)+str(prev_block_hash)+str(nonce)).encode('utf-8'))
        #code to calculate nonce will go here
        newblock = Block(nonce,pow_hash,prev_block_hash,self.open_transactions,len(self.blockchain))
        self.blockchain.append(newblock)
        self.open_transactions = []

    def load_blockhain(self):
        try:
            b = open("blockchain","r")
            o = open("openTransactions","r")
            self.blockchain = json.loads(str(b.read())) #deserializing from json strings into objects
            self.open_transactions = json.loads(str(o.read))
        except FileNotFoundError as ex:
            print("File Not Found.")
        except IOError as ex:
            print("Error reading blockchain from file.")
        finally:
            b.close()
            o.close()

    def save_blockchain(self):
        try:
            b = open("blockchain","w")
            o = open("openTransactions","w")
            b.write(json.dumps([block.JSON() for block in self.blockchain])) #serialising into json strings and outputting to file
            o.write(json.dumps([transaction.JSON() for transaction in self.open_transactions]))
        except IOError as ex:
            print("Error writing blockchain to file.")
        finally:
            b.close()
            o.close()
   
class Node:
    def __init__(self,blockchain=None):
        self.id = str(uuid.uuid4())
        if blockchain == None:
            self.blockchain = Blockchain(self.id)

    def listen_for_input(self):
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
                #sender_wallet = input("Enter Sender Wallet:")
                recv_wallet = input("Enter Recipient Wallet:")
                tx_amount = input("Enter Amount:")
                # Add the transaction amount to the open_transactions
                if not self.blockchain.addTransaction(sender_wallet=self.id,receiver_wallet=recv_wallet,tx_amount=tx_amount):
                    print("Insufficient Balance.")
                else:
                    print("Success.")

            elif user_choice == '2':
                self.blockchain.print_blockchain_elements()
            elif user_choice == '3':
                self.blockchain.mineCoin()
            elif user_choice == '4':
                self.blockchain.wallets.append(input("Enter Wallet ID: "))
            elif user_choice == '5':
                print(self.blockchain.getBalance(input("Enter Wallet ID: ")))
            elif user_choice == '6':
                if(self.blockchain.verify_open_transactions()):
                    print("Open Transactions OK")
                else:
                    print("Invalid transactions.")
            elif user_choice == 'h':
                pass
                # Make sure that you don't try to "hack" the blockchain if it's empty
                #if len(self.blockchain.blockchain) >= 1:
                 #   blockchain[0] = [2]
            elif user_choice == 'q':
                # This will lead to the loop to exist because it's running condition becomes False
                waiting_for_input = False
            else:
                print('Input was invalid, please pick a value from the list!')
            if not self.blockchain.verifyChain():
                self.blockchain.print_blockchain_elements()
                print('Invalid blockchain!')
                # Break out of the loop
                break
        else:
            print('User left!')


        print('Done!')


def main():
    node = Node()
    node.listen_for_input()

if(__name__=='__main__'):
    main()
