import json
#from tools import Tools

if __package__ is None or __package__ == '':
 #   # uses current directory visibility
    from tools import Tools


class sniper_interface:

    def __init__(self):
        self.tcake = "0xfCcD0a3De337004B4Ea466AbE775dc7bdC292785"
        self.cake = "0x0e09fabb73bd3ade0a17ecc321fd13a19e81ce82"
        self.network = ''
        self.saved_bool = True
        self.wait_LP = False
        self.fast_track_bool = False
        data = self.read_user()
        self.address = data[0]
        self.key = data[1]
        self.sell = False
        self.tools = Tools(self.key, self.address, data[6], data[7])
        self.tools.set_bsc_high_gas_price(data[2])
        self.tools.set_bsc_low_gas_price(data[3])
        self.tools.set_POLY_high_gas_price(data[4])
        self.tools.set_POLY_low_gas_price(data[5])

    def start_program(self):
        print("Hello, madpacket LP sniper starting\n")

        self.start_sniper()

    def start_sniper(self):
        cmd = input("BSC buying/sniping, 'b', Polygon buying/sniping, 'p', options + add key/address, 'o'\n")

        if cmd == 'o':
            self.ask_key_address()
            self.ask_router()
            self.ask_edit_gas()
            self.ask_network()
            self.start_sniper()
        elif cmd == 'b' or cmd == ' ':
            self.network = 'BSC'
            loop = True
            while(loop):
                cmd_BSC = input("Buyng, 'b' or space, sniping, 's', approve selling token, 'a', back/exit, 'x'\n")
                if cmd_BSC == 'b' or cmd_BSC == ' ':
                    self.snipe()
                elif cmd_BSC == 's':
                    self.wait_LP = True
                    self.snipe()
                elif cmd_BSC == 'a':
                    token = input('token address\n')
                    try:
                        self.tools.PCS_approve_sell(token)
                    except:
                        pass
                elif cmd_BSC == 'x':
                    loop = False
                

        elif cmd == 'p':
            self.network = 'POLY'
            cmd_BSC = input("Buyng, 'b' or space, sniping, 's'\n")
            if cmd_BSC == 'b' or cmd_BSC == ' ':
                self.snipe()
            elif cmd_BSC == 's':
                self.wait_LP = True
                self.snipe()
        
        
    def sell_sniper(self):
        txt = input("Want to snipe rugged token for selling?\n")
        if txt == 'y' or txt == ' ':
            self.sell = True
            self.wait_LP = True
            return True
        else:
            return False


# ----- functions reading txt file for user-data
    def read_user(self):
        data = [None, None, None, None, None, None, None, None]
        with open('user_data.txt') as f:
            lines = f.readlines()
            for line in lines:
                if line[0] == '#':
                    pass
                else:
                    
                    if line[:7] == 'address':
                        print(line)
                        data[0] = line[10:-1]
                    elif line[:3] == 'key':
                        data[1] = line[6:-1]
                    elif line[:18] == 'BSC high gas price':
                        data[2] = line[21:-1]
                    elif line[:17] == 'BSC low gas price':
                        data[3] = line[20:-1]
                    elif line[:19] == 'POLY high gas price':
                        data[4] = line[22:-1]
                    elif line[:18] == 'POLY low gas price':
                        data[5] = line[21:-1]
                    elif line[:17] == 'BSC HTTP node API':
                        data[6] = line[20:-1]
                    elif line[:18] == 'POLY HTTP node API':
                        data[7] = line[21:-1]
                    else:
                        pass
        return data
                

# ----- functions running the questions for editing sniper data
    def ask_network(self):
        val = input("What network, BSC (b), Polygon (p)\n")
        if val == 'b':
            self.network = 'BSC'
        elif val == 'p':
            self.network = 'POLY'
        else:
            print('did not understand\n')
            self.ask_nework()


    def ask_fast_track(self):
        val = input("Fast track to buy, space, fast track to snipe, 1, anything else is non fast track\n")
        if val == ' ':
            self.fast_track_bool = True
            return
        elif val == '1':
            self.wait_LP = True
            self.fast_track_bool = True
            return
        else:
            return

    def snipe(self):
        if self.network == 'BSC':
            val = input("How much BNB?\n")

            token = input("Address\n")
            if self.wait_LP:
                self.tools.PCS_LP_sniper(token, val)
            else:
                self.tools.PCS_buy_token(token, val)
        elif self.network == 'POLY':
            val = input("How much MATIC?\n")

            token = input("Address\n")
            if self.wait_LP:
                self.tools.QS_LP_sniper(token, val)
            else:
                self.tools.QS_buy_token(token, val)
        return self.ask_continue()

    def ask_continue(self):
        bool = True
        while(bool):
            txt = input("Do you want to edit data (y), or wait for next token (n/(spacebar))?\n")
            if txt == 'y':
                bool = False
                return False
            elif txt == 'n':
                bool = False
                return True
            elif txt == ' ':
                bool = False
                return True
            else:
                print('did not understand\n')


    def ask_LP_snipe(self):
        bool = True
        while(bool):
            txt = input("do you want to wait for liquidity? y/n\n")
            if txt == 'y' or txt == 'n' or txt ==  ' ':
                bool = False
                if txt == 'y':
                    self.wait_LP = True
                else:
                    pass
            else:
                print('did not understand\n')
                pass

    def ask_key_address(self):
        bool = True
        while(bool):
            txt = input("Do you want to input ur key and address (y), or use the ones saved in snipe.py? (n)\n")
            if txt == 'y':
                bool = False
                self.saved_bool = False
            elif txt == 'n':
                bool = False
            elif txt == ' ':
                bool = False
            else:
                print('did not understand\n')
                pass

        if not self.saved_bool:
            txt = input("Input private key\n")
            self.key = txt
            txt = input("input address\n")
            self.address = txt
        else:
            pass
    
    def ask_router(self):
        router = 2
        bool = True
        while(bool):
            txt = input("which router are you using? v1 (1), v2 (2) or test-network (0)\n")
            if txt == '0':
                bool = False
                router = 0
            elif txt == '1':
                bool = False
                router = 1
            elif txt == '2':
                bool = False
                pass
            elif txt == ' ':
                bool = False
                pass
            else:
                print('did not understand\n')
                pass
        self.tools.set_bsc_router(int(router))

    def ask_edit_gas(self):
        bool = True
        edit_gas_bool = False
        while(bool):
            txt = input("do you want to edit gas price? y/n\n")
            if txt == 'y' or txt == 'n' or txt ==  ' ':
                bool = False
                if txt == 'y':
                    edit_gas_bool = True
                elif txt == ' ':
                    pass
                else:
                    pass
            else:
                print('did not understand\n')
                pass
        
        if edit_gas_bool:
            bool = True
            while(bool):
                network = input("What network? b = BSC, p = Polygon\n")
                if network == "b":
                    bool = False
                elif network == "p":
                    bool = False
                else:
                    print("Sorry, did not understand input\n")


            high_price = input("what should be the gwei price for high cost transactions? integer numbers only\nBuy and sell transactions\n")
            tmp = int(high_price)

            if network == "b":
                self.tools.set_bsc_high_gas_price(tmp)
            elif network == "p":
                self.tools.set_POLY_high_gas_price(tmp)

            low_price = input("what should be the gwei price for low cost transactions? integer numbers only\nApprove token transaction\n")
            tmp = int(low_price)
            
            if network == "b":
                self.tools.set_bsc_low_gas_price(tmp)
            elif network == "p":
                self.tools.set_POLY_low_gas_price(tmp)

            gas_limit = input("what should be the gas limit? integer numbers only\n")
            tmp = int(gas_limit)
            
            if network == "b":
                self.tools.set_bsc_gas_limit(tmp)
            elif network == "p":
                self.tools.set_POLY_gas_limit(tmp)

        else:
            pass


if __name__ == "__main__":
    tmp = sniper_interface()
    tmp.start_program()


