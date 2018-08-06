
from collections import OrderedDict

import binascii
import psycopg2
import Crypto
import Crypto.Random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

import requests
from flask import Flask, jsonify, request, render_template

'''conn=psycopg2.connect(
                database='hackathon',
                user='harsh',
                password='***********',
                host='localhost',
                port=5432
)'''

class Transaction:

    def __init__(self, sender_address, sender_private_key, recipient_address, value):
        self.sender_address = sender_address
        self.sender_private_key = sender_private_key
        self.recipient_address = recipient_address
        self.value = value

    def __getattr__(self, attr):
        return self.data[attr]

    def dict_con(self):
        return OrderedDict({'sender_address': self.sender_address,
                            'recipient_address': self.recipient_address,
                            'value': self.value})

    def generate_sign(self):
        private_key = RSA.importKey(binascii.unhexlify(self.sender_private_key))
        signer = PKCS1_v1_5.new(private_key)
        h = SHA.new(str(self.dict_con()).encode('utf8'))
        return binascii.hexlify(signer.sign(h)).decode('ascii')



app = Flask(__name__)

@app.route('/')
def index():
	return render_template('./index.html')

@app.route('/make/transaction')
def make_transaction():
    return render_template('./make_transaction.html')

@app.route('/view/transactions')
def view_transaction():
    return render_template('./view_transactions.html')

@app.route('/wallet/new', methods=['GET'])
def create_wallet():
	random_gen = Crypto.Random.new().read
	private_key = RSA.generate(1024, random_gen)
	public_key = private_key.publickey()
	#cur.execute('insert into account values (address,)
	response = {
		'private_key': binascii.hexlify(private_key.exportKey(format='DER')).decode('ascii'),
		'public_key': binascii.hexlify(public_key.exportKey(format='DER')).decode('ascii')
	}

	return jsonify(response), 200

@app.route('/generate/transaction', methods=['POST'])
def generate_transaction():
	
	sender_address = request.form['sender_address']
	sender_private_key = request.form['sender_private_key']
	recipient_address = request.form['recipient_address']
	value = request.form['amount']

	transaction = Transaction(sender_address, sender_private_key, recipient_address, value)
	response = {'transaction': transaction.dict_con(), 'signature': transaction.generate_sign()}

	return jsonify(response), 200


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=8080, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port
#    curr=conn.cursor()
#    print('connection made')  
#    curr.execute('create table if not exists account (id BIGSERIAL, address varchar(2000), privatekey varchar(2000),ifsc_code varchar(10) #NULL,  account_number varchar(100) NULL, name varchar(100) NULL)')       
   # curr.execute('insert into account ()  
    app.run(host='127.0.0.1', port=port)
