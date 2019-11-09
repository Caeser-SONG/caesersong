import hashlib
import json
from time import time
from uuid import uuid4
from flask import Flask,jsonify,request
from textwrap import dedent


class Blockchain():
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        #被实例化时先创建一个创世区块，用new_block来创建
        self.new_block(previous_hash=1, proof=100)


    def new_block(self,proof,previous_hash=None):
        #创建一个新的区块，并加入链中
        #每个区块包含属性：索引（index）、Unix 时间戳（timestamp）、交易列表（transactions）、
        #工作量证明（稍后解释）以及前一个区块的 Hash 值。
        pass
        block = {
            'index': len(self.chain)+1,
            'timestamp':time,
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }
        self.current_transactions = []
        self.chain.append(block)
        return block
    def new_transaction(self,sender,recipient,amount):
        #创建一个交易信息,交易信息会被打包成一个区块，
        #返回即将被打包成的区块的索引
        self.current_transactions.append({
            'sender':sender,
            'recipient':recipient,
            'amount':amount
        })
        #目前链上最后一个区块的索引+1即为下一个区块的索引
        return self.last_block['index'] +1
    @staticmethod
    def hash(block):
        #  求一个区块的哈希值
        block_string = json.dumps(block,sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()
    @property
    def last_block(self):
        #返回链中最后一个区块
        return self.chain[-1]
    

    def proof_of_work(self, last_proof):
        """
        简单的工作量证明:
         - 查找一个 p' 使得 hash(pp') 以4个0开头
         - p 是上一个块的证明,  p' 是当前的证明
        :param last_proof: <int>
        :return: <int>
        """
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1
        return proof

    @staticmethod
    def valid_proof(last_proof,proof):
        """
        验证证明: 是否hash(last_proof, proof)以4个0开头?
        :param last_proof: <int> Previous Proof
        :param proof: <int> Current Proof
        :return: <bool> True if correct, False if not.
        """
        guess = '{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[0] =="0"
        

app = Flask(__name__)
node_identifier = str(uuid4()).replace('-','')
blockchain = Blockchain()
@app.route('/mine',methods = ['GET'])
def mine():
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)
    # 给工作量证明的节点提供奖励.
    # 发送者为 "0" 表明是新挖出的币
    blockchain.new_transaction(
        sender="0",
        recipient=node_identifier,
        amount=1,
    )
    # Forge the new Block by adding it to the chain
    block = blockchain.new_block(proof)
    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()
    # Check that the required fields are in the POST'ed data
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400
    # Create a new Transaction
    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])
    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 201


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200
@app.route('/', methods=['GET'])
def index():
    return '200'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)