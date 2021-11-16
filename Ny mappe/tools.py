import json
import web3
import time
from copy import copy
from web3 import Web3
import threading
from web3.middleware import geth_poa_middleware
from hexbytes import HexBytes as hb
from datetime import datetime

from bsc_sniper import BSC_sniper
from poly_sniper import POLY_sniper

#if __package__ is None or __package__ == '':
    # uses current directory visibility
 #   from bsc_sniper import BSC_sniper
  #  from poly_sniper import POLY_sniper


class Tools:    # future plans:
    #       a list of open transactions ready to send. 
    #       a list of "open" functions ready to send. 

    def __init__(self, key, address, BSC_url, POLY_url):
        self.key = key
        print(address)
        self.address = Web3.toChecksumAddress(address)

        self.w3 = self.load_w3()
        self.BSC_sniper = BSC_sniper(self.key, self.address, BSC_url, False, True)
        self.POLY_sniper = POLY_sniper(self.key, self.address, POLY_url)

# ----- load of web3     
    # keeping this, as it could be needed for other class objects for copy paste 
    # also need the w3 object for toChecksumAddress() calls
    def load_w3(self):
        
        bscURL = 'https://bsc-dataseed1.binance.org:443'

        return Web3(Web3.HTTPProvider(bscURL))

    # buys a token on pancakeswap and afterwards calls approve spender
    def PCS_buy_token(self, token, val):
        self.BSC_sniper.PCS_swap_buy_with_ETH(token, val)

    def PCS_LP_sniper(self, token, val):
        self.BSC_sniper.PCS_LP_sniper(token, val)
        self.BSC_sniper.approve_PCS(token, 1)
        
    def PCS_approve_sell(self, token):
        token = self.w3.toChecksumAddress(token)
        self.BSC_sniper.approve_PCS(token)
        print(token + " has been approved for selling")
        '''try:
            token = self.w3.toChecksumAddress(token)
            print("1")
            self.BSC_sniper.approve_PCS(token)      
        except:
            print('wrong input')'''

    def QS_LP_sniper(self, token, val):
        self.POLY_sniper.PCS_LP_sniper(token, val)
        self.POLY_sniper.approve_PCS(token)        

    def QS_buy_token(self, token, val):
        self.POLY_sniper.PCS_swap_buy_with_ETH(token, val)
       # self.POLY_sniper.approve_PCS(token)        

    def PCS_LP_seller(self, token):
        self.BSC_sniper.PCS_LP_sniper_sell(token)

# ------ setters and getters for own key and address
    def set_bsc_router(self, version):
        tmp = 0
        if version > 1:
            tmp = 2
        elif version == 1:
            tmp = 1
        elif version < 1:
            tmp = 0
        self.BSC_sniper.set_current_PCS_router(tmp)
    
    
    
    '''
    sets key for own object
    then calls a function updating all snipers
    in the future can remove function call, and maybe make individual calls
    in case of feature of handling multiple keys on different networks
    '''
    def set_key(self, key):
        key = self.w3.toChecksumAddress(key)
        self.key = key
        self.set_keys()
    
    def get_key(self):
        return copy(self.key)

    '''
    sets address for own object
    then calls a function updating all snipers
    in the future can remove function call, and maybe make individual calls
    in case of feature of handling multiple addresses on different networks
    '''
    def set_address(self, address):
        address = self.w3.toChecksumAddress(address)
        self.address = address
        self.set_addresses()

    def get_address(self, address):
        return copy(self.address)

    '''
    Only got a BSC sniper ATM
    But in future, should call setters for all networks
    '''
    def set_addresses(self):
        self.set_bsc_address(self.address)

    '''
    Only got a BSC sniper ATM
    But in future, should call setters for all networks
    '''
    def set_keys(self):
        self.set_bsc_keys(self.keys)

# ----- getters and setters for BSC sniper
    def set_bsc_high_gas_price(self, val):
        self.BSC_sniper.set_high_gas_price(val)

    def get_bsc_high_gas_price(self):
        return self.BSC_sniper.get_high_gas_price()

    def set_bsc_low_gas_price(self, val):
        self.BSC_sniper.set_low_gas_price(val)

    def get_bsc_low_gas_price(self):
        return self.BSC_sniper.get_low_gas_price()
    
    def set_bsc_gas_limit(self, val):
        self.BSC_sniper.set_gas_limit(val)

    def get_bsc_gas_limit(self):
        return self.BSC_sniper.get_gas_limit()
    
    def set_bsc_address(self, val):
        self.BSC_sniper.set_address(val)

    def get_bsc_address(self):
        return self.BSC_sniper.get_address()

    def set_bsc_key(self, val):
        self.BSC_sniper.set_key(val)

    def get_bsc_key(self):
        return self.BSC_sniper.get_key()
    
# ----- getters and setters for POLY sniper
    def set_POLY_high_gas_price(self, val):
        self.POLY_sniper.set_high_gas_price(val)

    def get_POLY_high_gas_price(self):
        return self.POLY_sniper.get_high_gas_price()

    def set_POLY_low_gas_price(self, val):
        self.POLY_sniper.set_low_gas_price(val)

    def get_POLY_low_gas_price(self):
        return self.POLY_sniper.get_low_gas_price()
    
    def set_POLY_gas_limit(self, val):
        self.POLY_sniper.set_gas_limit(val)

    def get_POLY_gas_limit(self):
        return self.POLY_sniper.get_gas_limit()
    
    def set_POLY_address(self, val):
        self.POLY_sniper.set_address(val)

    def get_POLY_address(self):
        return self.POLY_sniper.get_address()

    def set_POLY_key(self, val):
        self.POLY_sniper.set_key(val)

    def get_POLY_key(self):
        return self.POLY_sniper.get_key()