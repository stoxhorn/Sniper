check = True
address = ''
token = ''
transactions = []
added_lp = []
blocks = []
transaction_str = 'reading transaction: '
block_str = 'reading block: '
lp_added_str = 'added liquidity for token: '
comparison = 'comparison: '

found_it = False

extra_line = 1


def check_liquidity(str, txn, comp1, comp2, time):
    global extra_line
    global lp_added_str
    global added_lp
    global token
    length = len(lp_added_str)
    length_comp = len(comparison)

    if str[:length] == lp_added_str:
        added_lp.append((str[length:-1], txn[:-1], comp1[length_comp:-1], comp2[:-1], time[:-1]))
        extra_line += 4
    else:
        pass

def check_transaction(str):
    global extra_line
    global transaction_str
    global transactions
    length = len(transaction_str)
    if str[:length] == transaction_str:
        transactions.append((str[length:-1], '-'))
    else:
        pass

def check_block(str, next_line):
    global extra_line
    global block_str
    global blocks
    length = len(block_str)
    if str[:length] == block_str:
        blocks.append((str[length:-1], next_line))
        extra_line += 1
    else:
        pass



with open('log.txt') as f:
    lines = f.readlines()

    token = lines[0][38:-1]
    print('-' + token + '-\n')
    for i in range(len(lines)):
        i += extra_line
        check_transaction(lines[i])
        if not (i+1) < len(lines):
            break
        check_block(lines[i], lines[i+1])
        if not (i+4) < len(lines):
            break
        check_liquidity(lines[i], lines[i+1], lines[i+2], lines[i+3], lines[i+4])
        if not i < len(lines):
            break
        if lines[i][:13] == 'executed snipe':
            found_it = True
        

print('Scanned following blocks')

prev_block = 0
missed_blocks = []
for i in blocks:
    block_num = int(i[0])
    if prev_block == 0:
        prev_block = block_num
    elif prev_block == (block_num -1):
        prev_block = block_num
    else:
        if (prev_block+1) != block_num:
            list = []
            for i in range(block_num-prev_block+1):
                i += prev_block +1
                list.append(i)
            missed_blocks.append(list)
    print(i)

print("missed blocks: \n")
for i in missed_blocks:
    print(i, end = ' - ')

for i in added_lp:
    print(i[0])
    print(token)
    print(" - ")


if found_it:
    print("found pool")
else:
    print("didn't find it")

