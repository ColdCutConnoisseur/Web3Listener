"""Use web3 to listen for contract events"""

import sys
import time
import pprint
from web3.exceptions import InfuraKeyNotFound

try:
    from web3.auto.infura import w3

except InfuraKeyNotFound:
    print("Make sure that you've correctly set environment variables for ",
          "web3 before running--see the README.md")
    sys.exit(0)

import contract_abis_and_addresses

SLEEP_BETWEEN_CALLS = 5 #minutes

class EventFetcher:

    def __init__(self, collection_address, collection_abi, event_name):

        w3_connected = w3.isConnected()
        print(f"Web3 is connected?: {w3_connected}")        

        self.collection_address = collection_address
        self.collection_abi = collection_abi
        self.event_name = event_name

        self.nft_contract = w3.eth.contract(address=collection_address, abi=collection_abi)
        self.historical_block = None
        self.latest_block = None

        self.pretty = pprint.PrettyPrinter(indent=4, width=1, sort_dicts=False)

        self.on = False

    def set_latest_and_historical_blocks(self):
        #self.latest_block = w3.eth.get_block('latest').number
        self.latest_block = w3.eth.get_block_number()

        print(f"Latest Block #: {self.latest_block}")
        self.historical_block = self.latest_block - 5000000

    def fetch_events(self):
        historical_events = self.nft_contract.getPastEvents(
                self.event_name,
                { 'fromBlock' : self.historical_block, 'toBlock' : self.latest_block }
        )

        print(historical_events[0])

        self.historical_block = self.latest_block

    def start_listener(self):
        self.set_latest_and_historical_blocks()
        self.on = True

        self.fetch_events()

        while self.on:
            print("Sleeping...")
            time.sleep(SLEEP_BETWEEN_CALLS)
            print("Sleep exited")

            self.latest_block = w3.eth.getBlockNumber()

            if self.latest_block > self.historical_block:

                self.fetch_events()

    def run_filter(self):
        self.set_latest_and_historical_blocks()

        new_filter = self.nft_contract.events.Transfer.createFilter(fromBlock=15296100) #'latest'

        old_entries = new_filter.get_all_entries()

        for event_dict in old_entries:
            self.pretty.pprint(dict(event_dict))

        print("Sleeping...")
        time.sleep(SLEEP_BETWEEN_CALLS*60)
        print("Sleep exited")


        new_filter = self.nft_contract.events.Transfer.createFilter(fromBlock='latest')
        print(new_filter.get_new_entries())

        print("Done")


    """ALTERNATIVES
    
        event_filter = w3.eth.filter({"address": contract_address})
    """




if __name__ == "__main__":
    collection_address = "0xa3b7CEe4e082183E69a03Fc03476f28b12c545A7"
    collection_abi = contract_abis_and_addresses.CHILL_FROGS_ABI
    event_name = 'Transfer'

    test_listener = EventFetcher(collection_address, collection_abi, event_name)

    #test_listener.start_listener()

    test_listener.run_filter()
