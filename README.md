# Sniper

SCript that reads through every new block for added liquidity of specified token.

User's address and api-key is specified in the user_data.txt file, for each respective network. 

Currently only works from command-line

Atm, i have my API key from quicknode in code still, as i don't use these anymore, and dont care if the alloted amount of calls get spent. 

People using a local node will be about 5 seconds faster than if using quicknode.
As such this script will most likely not allow you to get in early enough, before this botter starts dumping the price to china.

It does however allow to make a straight buyorder, without sniping. Which can circumvent the horribly slow UI of pancakeswap. 
There has been zero effort made to handle slippage, so slippage is pretty much at max possible. So be careful. 
