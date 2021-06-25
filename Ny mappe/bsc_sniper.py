import json
import web3
import time
from web3 import Web3
import threading
from web3.middleware import geth_poa_middleware
from hexbytes import HexBytes as hb
from datetime import datetime
from time import ctime
import copy

# TODO spot dxsale listings
# test txn_hash https://bscscan.com/tx/0xa7766c5f718df153dc717d05e318e1ac1c0fb7c043ad05365491d656f1b9962d

class BSC_sniper:
        # address = Web3.toChecksumAddress('')
        
    def __init__(self, key, address, test_network = False, version_2 = True):
        # Loads real or test network of BSC
        #self.w3 = self.load_w3(test_network)
        self.w3 = self.load_w3_wss()
        #self.w32 = self.load_w32(test_network)

        self.gas_limit = 400000
        
        # value of own private metamask keyu
        self.key = key
        
        # address of own wallet
        self.address = Web3.toChecksumAddress(address)
        
        # stores token addresses
        self.twbnb = Web3.toChecksumAddress("0xae13d989dac2f0debff460ac112a837c89baa7cd")
        self.wbnb = Web3.toChecksumAddress("0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c")
        
        # pancakeswap router addresses
        self.PCST_address = '0xD99D1c33F9fC3444f8101754aBC46c52416550D1'
        self.PCS_v1_address = '0x05fF2B0DB69458A0750badebc4f9e13aDd608C7F'
        self.PCS_v2_address = '0x10ED43C718714eb63d5aA57B78B54704E256024E'

        self.current_router = 2

        self.high_gas_price = self.w3.toWei('25', 'gwei')    
        self.low_gas_price = self.w3.toWei('10', 'gwei')    
        
        # this was needed to read BSC blocks
        

        # flag for being able to cancel snipipng
        self.input_flag = True

        # Loads the ABI interface for pancakeswap
        # ATM, i only have ABI from test network
        # but the ABI itself should be the same
        # or at least need same arguemnts
        # haven't tested this
        self.PCS_abi = self.load_PCS_abi(test_network, version_2)

        # Constructs the PCS contract from the given ABI
        self.PCS_contract = self.w3.eth.contract(abi = self.PCS_abi, address = self.get_current_PCS_router_address())


        # This also loads ABI from a token on test network
        # This also shouldn't affect approve spender
        # dunno about other functions        
        self.test_token_abi = self.load_token_abi()
        self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        #self.w3_wss.middleware_onion.inject(geth_poa_middleware, layer=0)

# ------- Start LP sniping
    '''
    takes token as input and a value as input. Creates a buy transaction and then checks for liquidiy
    TODO: if liquidity has already been added, won't ever send a buy transaction
    '''
    def PCS_LP_sniper(self, token, val):
        token = Web3.toChecksumAddress(token)
        function = self.make_buy_func(token)
        print('-' + token + '-\n')
        signed_txn = self.build_sign_func(function, val)

        log = open('log_BSC.txt', 'w')
        log.write('Looking for added liquidity of token: ' + token + "\n")

        self.LP_loop(signed_txn, token, log)

        return 0        

    def PCS_LP_sniper_sell(self, token, val):
        token = Web3.toChecksumAddress(token)
        function = self.make_sell_func(token)
        print('-' + token + '-\n')
        signed_txn = self.build_sign_func(function, val)

        log = open('log_BSC.txt', 'w')
        log.write('Looking for added liquidity of token: ' + token + "\n")

        self.LP_loop(signed_txn, token, log)
        return 0

# ------- LP check loop function
    def LP_loop(self, signed_txn, token, log):
        # start_time = time.time()
        print("Transaction prepared, starting LP checking\n")
        log.write('starting new loop\n')
        # filter for getting latest block       
        #self.w3 = self.load_w3() 
        #self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        
        latest_block = self.w3.eth.get_block('latest')
        latest_block_num = int(latest_block['number'])
        #latest_block_num = 7383547
        # 7383646 bugs out?
        filt = self.w3.eth.filter({'fromBlock': latest_block_num, 'toBlock': 'latest', 'address':token})
        token = token.lower()
        # keep going till other thread flips input_flag
        d = 0
        loop_bool = True
        while loop_bool:
            d += 1
            print(" - ", end = '', flush = True)
            # get filter entries
            #time.sleep(0.1)
            #ll = l.get_new_entries()
            try:
                #next_block = self.w3.eth.getBlock(latest_block_num, full_transactions=True)
                entries = filt.get_new_entries()
                #log.write('\nReading block: ' + str(latest_block_num) + '\n')
                #latest_block_num += 1
                loop_bool = self.read_block(token, entries, log, signed_txn)
            except AttributeError:
                print(str(d), end = '', flush= True)
                time.sleep(0.1)
            
    
    def read_block(self, token, entries, log, signed_txn):
        # For each block in filter
        # print("\nFound new block, and going through transactions\n")
        for txn in entries:
            print("found token transaction")
            # 0xf305d719 is method ID for adding liquidity on pancakerouter on test network.
            
            txn_address = str(self.w3.toHex(txn['transactionHash']))
            txn = self.w3.eth.get_transaction(txn_address)
            print(txn_address)
            log.write('reading transaction: ' + txn_address + str(ctime()) + '\n')
            if txn['input'][:10] == "0xf305d719":
                print("found standard LP transaction\n")
                # Check if first argument is the token specified

            #    tok = self.get_next_num(txn['input'] + '\n')
            #    log.write('added liquidity for token: ' + str(tok) + '\n' + str(self.w3.toHex(txn['hash'])) + '\n' + 'comparison: ' + token + '\n' + tok + '\n')
            #    log.write(ctime() + '\n')
                #if tok == token:
                self.send_signed_txn(signed_txn)
                
                # send saved transaction, and flag for checking to stop
                
                # feedback string, so you know it happened and can go check BSC scan urself
                print("executed snipe, closing\n")
                log.write('executed snipe\n')
                log.write(ctime() + '\n')
                log.close()
                return False
            elif txn['input'] == '0x267dd102':
                print("found DXsale LP listing\n")
                self.send_signed_txn(signed_txn)
                # send saved transaction, and flag for checking to stop
                
                # feedback string, so you know it happened and can go check BSC scan urself
                print("executed snipe, closing\n")
                log.write('executed snipe\n')
                log.write(ctime() + '\n')
                log.close()
                return False
            elif txn['input'][:10] == '0x267dd102':
                print("found DXsale LP listing\n")
                self.send_signed_txn(signed_txn)
                # send saved transaction, and flag for checking to stop
                
                # feedback string, so you know it happened and can go check BSC scan urself
                print("executed snipe, closing\n")
                log.write('executed snipe\n')
                log.write(ctime() + '\n')
                log.close()
                return False
            
        # print("did not find LP added for specified " + token + ", in current block\n")
        return True
    
        
# ------- helper functions for managing flow and threading

    '''
    Waits for enter to be pressed,
    and flips the boolean keeping the LP check looping
    '''
    def get_input(self):
        keystrk=input('')
        # thread doesn't continue until key is pressed
        print('You pressed enter and stopped the liquidity pool check loop\n', keystrk)
        self.input_flag=False

# ------- Builder functions used for the LP sniper        

    def make_buy_func(self, token):
        # get time and add a bunch of time to it
        trans_time = int(time.time() + 60*60*60*60*60) 
        
        # create the function call
        return self.PCS_contract.functions.swapExactETHForTokens( 1, [self.get_wrapped(), token], self.address, trans_time)

    def make_sell_func(self, token):
        # get time and add a bunch of time to it
        trans_time = int(time.time() + 60*60*60*60*60) 
        
        # create the function call
        # 20000000000000000000 is 20 for the EYFI token
        return self.PCS_contract.functions.swapExactTokensForETH( 44705000000000000000000, 1, [token, self.get_wrapped()], self.address, trans_time)

    
    '''
    Takes a function_call and value as argument
    builds a transaction from given function and value
    '''
    def build_sign_func(self, function, val):

        # get the nonce, transaction number 1, has nonce 0, so transaction count = next Nonce
        # NOTE: this means making any transaction while the sniper is running, will give an error
        # this is because the nonce has increased, and the saved transaction's nonce is too low
        txn_count = self.w3.eth.get_transaction_count(self.address)
        # create the transaction
        transaction = function.buildTransaction({'gas': self.gas_limit, 'gasPrice': self.high_gas_price, 'from': self.address, 'nonce': txn_count, 'value': self.vETH(val)})

        # sign transaction
        return self.w3.eth.account.signTransaction(transaction, private_key=self.key)

    '''
    Takes a transaction already signed and ready for being send. 
    And sends it
    '''
    def send_signed_txn(self, signed_txn):
        # send transaction
        self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        return 0

# ------- simple straight buy function
    '''
    Buying a token with max slippage and no waiting for LP
    uses high gas price
    '''
    def PCS_swap_buy_with_ETH(self, token, val):
        # making sure a fast copy-paste of the address doesn't fuck shit up
        token = Web3.toChecksumAddress(token)
        
        # get time and add a bunch of time to it
        trans_time = int(time.time() + 60*60*60*60*60) 
        
        # create the function call for swapping BNB for tokens
        function = self.PCS_contract.functions.swapExactETHForTokens( 1, [self.get_wrapped(), token], self.address, trans_time)

        # build transaction, and sign with key, ready to be send. .
        signed_txn = self.build_sign_func(function, val)

        # send transaction 
        return self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)

# ------- Approve spender function

    def approve_PCS(self, token, extra_nonce = 0):
        self.PCS_approve_sell(self.get_current_PCS_router_address(), token, extra_nonce)




    '''
    Function approving the given address
    as spender for 115792089237316195423570985008687907853269984665640564039457584007913129639935 tokens
    this value is taken from taking the hex version of the value pancakeswap sends
    Uses the low gas price for the transaction
    '''
    def PCS_approve_sell(self, router, token, extra_nonce):
        token = Web3.toChecksumAddress(token)
        router = Web3.toChecksumAddress(router)

        test = self.w3.eth.contract(abi = self.test_token_abi, address = Web3.toChecksumAddress(token))

        function = test.functions.approve(router, 115792089237316195423570985008687907853269984665640564039457584007913129639935)
        
        txn_count = self.w3.eth.get_transaction_count(self.address) + extra_nonce
        
        transaction = function.buildTransaction({'gas': self.gas_limit, 'gasPrice': self.low_gas_price, 'from': self.address, 'nonce': txn_count, 'value': 0})
        
        signed_txn = self.w3.eth.account.signTransaction(transaction, private_key=self.key)
        
        self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)

# -------- Various helper functions

    '''
    Just a wrapper so it's easier to turn to eth
    dunno why it's vETH
    '''
    def vETH(self, eth):
        return self.w3.toWei(eth, 'ether')


    '''
    Removes function call and first set of 0's from input
    0's should mark "empty data" and as such no argument can start with a 0
    '''
    def get_next_num(self, str):
        global w3
        str = str[10:74]
        d = 0
        for i in str:
            if i == '0':
                d += 1
            else:
                break
        str = str[d:]
        return '0x' + str

# -------- Functions for initializing

    def update_PCS_router(self):
        self.PCS_contract = self.w3.eth.contract(abi = self.PCS_abi, address = self.get_current_PCS_router_address())

    '''
    atm, i'm just using the ABI of a token selfmade
    only used to approve a spender, should be same arguments for all tokens
    TODO research/test if this matters
    '''
    def load_PCS_abi(self, test_network, version_2):
        PCS_abi = None
        file_str = ""        
        if not test_network and version_2:
            file_str = "PCS_v2_abi.json"
        elif not test_network and not version_2:
            file_str = "PCSTabi.json"
        elif test_network:
            file_str = "PCSTabi.json"

        with open(file_str) as jsonF:
            PCS_abi = json.load(jsonF)
        return PCS_abi

    '''
    initializes the web3 object
    will load testnetwork, if specified
    '''
    def load_w3(self, test_network):
        #Web3(Web3.WebsocketProvider())
        bscTURL = 'https://data-seed-prebsc-1-s1.binance.org:8545'
        bscURL = 'https://bsc-dataseed1.binance.org:443'
        getBlockURL = 'wss://bsc.getblock.io/mainnet/ws/api/ed6d727e-31b5-4dee-9879-2447cfab0819'
        quicknodeURL = 'wss://billowing-muddy-glade.bsc.quiknode.pro/0c1d1395d189ab42e9a03901bed0ff61a6b9e774/'
        quicknodeHTTP = 'https://billowing-muddy-glade.bsc.quiknode.pro/0c1d1395d189ab42e9a03901bed0ff61a6b9e774/'
        #ws3 = Web3(Web3.WebsocketProvider(infura_url_ws,request_kwargs={'timeout':60}))

        if not test_network:
            tmp = Web3(Web3.WebsocketProvider(quicknodeURL))
            #tmp = Web3(Web3.HTTPProvider(quicknodeHTTP))
            if tmp.isConnected():
                print("connected to BSC network\n")
            else:
                print("could not connect to BSC network\n")
                return None
            return tmp
            #return Web3(Web3.HTTPProvider(bscURL))

        elif test_network:
            print("connected to BSC TEST! network\n")
            return Web3(Web3.HTTPProvider(bscTURL))

    def load_w3_wss(self):
        quicknodeURL = 'wss://billowing-muddy-glade.bsc.quiknode.pro/0c1d1395d189ab42e9a03901bed0ff61a6b9e774/'
        quicknodeHTTP = 'https://billowing-muddy-glade.bsc.quiknode.pro/0c1d1395d189ab42e9a03901bed0ff61a6b9e774/'
        return Web3(Web3.WebsocketProvider(quicknodeURL, websocket_kwargs = {'ping_interval':None})) # Web3(Web3.HTTPProvider(quicknodeHTTP))
    
    '''
    Loads the token ABI from an old testtoken
    ATM, only used for approving spender
    this function should use same arguments across the board
    '''
    def load_token_abi(self):
        test_abi = None

        with open("test_token_abi.json") as jsonF:
            test_abi = json.load(jsonF)
        return test_abi

# -------- getters and setters
    
    def set_current_PCS_router(self, val):
        self.current_router = val
        self.PCS_contract = self.w3.eth.contract(abi = self.PCS_abi, address = self.get_current_PCS_router_address())

    def get_current_PCS_router(self):
        return copy.copy(self.current_router)
    
    def get_current_PCS_router_address(self):
        if self.current_router == 2:
            return copy.copy(self.PCS_v2_address)
        elif self.current_router == 1:
            return copy.copy(self.PCS_v1_address)
        elif self.current_router == 0:
            return copy.copy(self.PCST_address)
        else:
            return "ERROR, No router specified"
        
    
    '''
    Specified value is expected to be a spring indicating price in the unit of gwei
    '''
    def set_high_gas_price(self, val):
        self.high_gas_price = self.w3.toWei(val, 'gwei')

    def get_high_gas_price(self):
        return copy.copy(self.high_gas_price)

    def set_low_gas_price(self, val):
        self.high_low_price = val
    
    def get_low_gas_price(self):
        return copy.copy(self.high_low_price)

    def set_gas_limit(self, val):
        self.gas_limit = val

    def get_gas_limit(self):
        return copy.copy(self.geas_limit)

    def set_address(self, address):
        self.address = self.w3.toChecksumAddress(address)

    def get_address(self):
        return copy.copy(self.address)

    def set_key(self, key):
        self.key = key

    def get_key(self):
        return copy.copy(self.key)

    def get_wrapped(self):
        if self.current_router == 0:
            return self.twbnb
        else:
            return self.wbnb