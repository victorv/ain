#!/usr/bin/env python3
# Copyright (c) 2014-2019 The Bitcoin Core developers
# Copyright (c) DeFi Blockchain Developers
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.
"""Test EVM behaviour"""

from test_framework.test_framework import DefiTestFramework
from test_framework.util import assert_equal, assert_raises_rpc_error

rawTx = "f9044e808502540be450832dc6c08080b903fb608060405234801561001057600080fd5b506103db806100206000396000f3fe608060405234801561001057600080fd5b50600436106100365760003560e01c8063131a06801461003b5780632e64cec114610050575b600080fd5b61004e61004936600461015d565b61006e565b005b6100586100b5565b604051610065919061020e565b60405180910390f35b600061007a82826102e5565b507ffe3101cc3119e1fe29a9c3464a3ff7e98501e65122abab6937026311367dc516816040516100aa919061020e565b60405180910390a150565b6060600080546100c49061025c565b80601f01602080910402602001604051908101604052809291908181526020018280546100f09061025c565b801561013d5780601f106101125761010080835404028352916020019161013d565b820191906000526020600020905b81548152906001019060200180831161012057829003601f168201915b5050505050905090565b634e487b7160e01b600052604160045260246000fd5b60006020828403121561016f57600080fd5b813567ffffffffffffffff8082111561018757600080fd5b818401915084601f83011261019b57600080fd5b8135818111156101ad576101ad610147565b604051601f8201601f19908116603f011681019083821181831017156101d5576101d5610147565b816040528281528760208487010111156101ee57600080fd5b826020860160208301376000928101602001929092525095945050505050565b600060208083528351808285015260005b8181101561023b5785810183015185820160400152820161021f565b506000604082860101526040601f19601f8301168501019250505092915050565b600181811c9082168061027057607f821691505b60208210810361029057634e487b7160e01b600052602260045260246000fd5b50919050565b601f8211156102e057600081815260208120601f850160051c810160208610156102bd5750805b601f850160051c820191505b818110156102dc578281556001016102c9565b5050505b505050565b815167ffffffffffffffff8111156102ff576102ff610147565b6103138161030d845461025c565b84610296565b602080601f83116001811461034857600084156103305750858301515b600019600386901b1c1916600185901b1785556102dc565b600085815260208120601f198616915b8281101561037757888601518255948401946001909101908401610358565b50858210156103955787850151600019600388901b60f8161c191681555b5050505050600190811b0190555056fea2646970667358221220f5c9bb4feb3fa563cfe06a38d411044d98edf92f98726288036607edd71587b564736f6c6343000811003329a002d4dafabf2dbbf475724f6950e80936a69010d5f759d0562570dbd0c042ef8da03dc881e654beb5e83eb63e2b8a3262c9b054bab2f0a6376f26c407903c14dfc1"


class EVMTest(DefiTestFramework):
    def set_test_params(self):
        self.num_nodes = 1
        self.setup_clean_chain = True
        self.extra_args = [
            [
                "-dummypos=0",
                "-txnotokens=0",
                "-amkheight=50",
                "-bayfrontheight=51",
                "-dakotaheight=51",
                "-eunosheight=80",
                "-fortcanningheight=82",
                "-fortcanninghillheight=84",
                "-fortcanningroadheight=86",
                "-fortcanningcrunchheight=88",
                "-fortcanningspringheight=90",
                "-fortcanninggreatworldheight=94",
                "-fortcanningepilogueheight=96",
                "-grandcentralheight=101",
                "-metachainheight=105",
                "-df23upgradeheight=105",
                "-subsidytest=1",
            ],
        ]

    def setup(self):
        self.address = self.nodes[0].get_genesis_keys().ownerAuthAddress
        self.ethAddress = self.nodes[0].getnewaddress("", "erc55")
        self.to_address = self.nodes[0].getnewaddress("", "erc55")

        # Generate chain
        self.nodes[0].generate(101)

        assert_raises_rpc_error(
            -32600,
            "called before Metachain height",
            self.nodes[0].evmtx,
            self.ethAddress,
            0,
            21,
            21000,
            self.to_address,
            0.1,
        )

        # Move to fork height
        self.nodes[0].generate(4)

        self.nodes[0].getbalance()
        self.nodes[0].utxostoaccount({self.address: "201@DFI"})
        self.nodes[0].setgov(
            {
                "ATTRIBUTES": {
                    "v0/params/feature/evm": "true",
                    "v0/params/feature/transferdomain": "true",
                    "v0/transferdomain/dvm-evm/enabled": "true",
                    "v0/transferdomain/dvm-evm/src-formats": ["p2pkh", "bech32"],
                    "v0/transferdomain/dvm-evm/dest-formats": ["erc55"],
                    "v0/transferdomain/evm-dvm/src-formats": ["erc55"],
                    "v0/transferdomain/evm-dvm/auth-formats": ["bech32-erc55"],
                    "v0/transferdomain/evm-dvm/dest-formats": ["p2pkh", "bech32"],
                }
            }
        )
        self.nodes[0].generate(2)

        self.creationAddress = "0xe61a3a6eb316d773c773f4ce757a542f673023c6"
        self.nodes[0].importprivkey(
            "957ac3be2a08afe1fafb55bd3e1d479c4ae6d7bf1c9b2a0dcc5caad6929e6617"
        )

    def test_deploy_smart_contract(self):
        # deploy smart contract
        rawTx = "f9044e808502540be400832dc6c08080b903fb608060405234801561001057600080fd5b506103db806100206000396000f3fe608060405234801561001057600080fd5b50600436106100365760003560e01c8063131a06801461003b5780632e64cec114610050575b600080fd5b61004e61004936600461015d565b61006e565b005b6100586100b5565b604051610065919061020e565b60405180910390f35b600061007a82826102e5565b507ffe3101cc3119e1fe29a9c3464a3ff7e98501e65122abab6937026311367dc516816040516100aa919061020e565b60405180910390a150565b6060600080546100c49061025c565b80601f01602080910402602001604051908101604052809291908181526020018280546100f09061025c565b801561013d5780601f106101125761010080835404028352916020019161013d565b820191906000526020600020905b81548152906001019060200180831161012057829003601f168201915b5050505050905090565b634e487b7160e01b600052604160045260246000fd5b60006020828403121561016f57600080fd5b813567ffffffffffffffff8082111561018757600080fd5b818401915084601f83011261019b57600080fd5b8135818111156101ad576101ad610147565b604051601f8201601f19908116603f011681019083821181831017156101d5576101d5610147565b816040528281528760208487010111156101ee57600080fd5b826020860160208301376000928101602001929092525095945050505050565b600060208083528351808285015260005b8181101561023b5785810183015185820160400152820161021f565b506000604082860101526040601f19601f8301168501019250505092915050565b600181811c9082168061027057607f821691505b60208210810361029057634e487b7160e01b600052602260045260246000fd5b50919050565b601f8211156102e057600081815260208120601f850160051c810160208610156102bd5750805b601f850160051c820191505b818110156102dc578281556001016102c9565b5050505b505050565b815167ffffffffffffffff8111156102ff576102ff610147565b6103138161030d845461025c565b84610296565b602080601f83116001811461034857600084156103305750858301515b600019600386901b1c1916600185901b1785556102dc565b600085815260208120601f198616915b8281101561037757888601518255948401946001909101908401610358565b50858210156103955787850151600019600388901b60f8161c191681555b5050505050600190811b0190555056fea2646970667358221220f5c9bb4feb3fa563cfe06a38d411044d98edf92f98726288036607edd71587b564736f6c634300081100332aa04ba71a6cfe81e1fc346a9720140e01bfff57a8712fbdd57394306dadf1668ac6a02407389762aa0e9c5dd4c79dc6c4fcf550eb6309fe3aaa776d45d5a5874b892c"
        self.nodes[0].eth_sendRawTransaction(rawTx)
        self.nodes[0].generate(1)

        # get smart contract address
        blockNumber = self.nodes[0].eth_blockNumber()
        block = self.nodes[0].eth_getBlockByNumber(blockNumber, False)

        smartContractInfoReceipt = self.nodes[0].eth_getTransactionReceipt(
            block["transactions"][0]
        )
        self.smartContractAddress = smartContractInfoReceipt["contractAddress"]

        code = self.nodes[0].eth_getCode(self.smartContractAddress)
        assert_equal(
            code,
            "0x608060405234801561001057600080fd5b50600436106100365760003560e01c8063131a06801461003b5780632e64cec114610050575b600080fd5b61004e61004936600461015d565b61006e565b005b6100586100b5565b604051610065919061020e565b60405180910390f35b600061007a82826102e5565b507ffe3101cc3119e1fe29a9c3464a3ff7e98501e65122abab6937026311367dc516816040516100aa919061020e565b60405180910390a150565b6060600080546100c49061025c565b80601f01602080910402602001604051908101604052809291908181526020018280546100f09061025c565b801561013d5780601f106101125761010080835404028352916020019161013d565b820191906000526020600020905b81548152906001019060200180831161012057829003601f168201915b5050505050905090565b634e487b7160e01b600052604160045260246000fd5b60006020828403121561016f57600080fd5b813567ffffffffffffffff8082111561018757600080fd5b818401915084601f83011261019b57600080fd5b8135818111156101ad576101ad610147565b604051601f8201601f19908116603f011681019083821181831017156101d5576101d5610147565b816040528281528760208487010111156101ee57600080fd5b826020860160208301376000928101602001929092525095945050505050565b600060208083528351808285015260005b8181101561023b5785810183015185820160400152820161021f565b506000604082860101526040601f19601f8301168501019250505092915050565b600181811c9082168061027057607f821691505b60208210810361029057634e487b7160e01b600052602260045260246000fd5b50919050565b601f8211156102e057600081815260208120601f850160051c810160208610156102bd5750805b601f850160051c820191505b818110156102dc578281556001016102c9565b5050505b505050565b815167ffffffffffffffff8111156102ff576102ff610147565b6103138161030d845461025c565b84610296565b602080601f83116001811461034857600084156103305750858301515b600019600386901b1c1916600185901b1785556102dc565b600085815260208120601f198616915b8281101561037757888601518255948401946001909101908401610358565b50858210156103955787850151600019600388901b60f8161c191681555b5050505050600190811b0190555056fea2646970667358221220f5c9bb4feb3fa563cfe06a38d411044d98edf92f98726288036607edd71587b564736f6c63430008110033",
        )

    def test_smart_contract_address_state_storage(self):
        initialBlockNumber = self.nodes[0].eth_blockNumber()

        storage = self.nodes[0].eth_getStorageAt(
            self.smartContractAddress, "0x0", "latest"
        )
        assert_equal(
            storage,
            "0x0000000000000000000000000000000000000000000000000000000000000000",
        )

        # Fund address
        self.nodes[0].transferdomain(
            [
                {
                    "src": {"address": self.address, "amount": "10@DFI", "domain": 2},
                    "dst": {
                        "address": self.creationAddress,
                        "amount": "10@DFI",
                        "domain": 3,
                    },
                    "singlekeycheck": False,
                }
            ]
        )
        self.nodes[0].generate(1)

        callRawTx = "f8ca018502e90edd00832dc6c094e27a95f0d6fafa131927ac50861a4190f5a9c60b80b864131a06800000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000000d48656c6c6f2c20576f726c6421000000000000000000000000000000000000002aa06a6f62a09f44429dadb681de8bb821dd8d3fc4a27f591859cccbc3dbcd30a52ca06222e9a02143a1a6c625d3aee7d5797489e40b1006b067ad5593fc76e84983be"
        # Call smart contract
        self.nodes[0].eth_sendRawTransaction(callRawTx)
        self.nodes[0].generate(1)

        storage = self.nodes[0].eth_getStorageAt(
            self.smartContractAddress, "0x0", "latest"
        )
        assert_equal(
            storage,
            "0x48656c6c6f2c20576f726c64210000000000000000000000000000000000001a",
        )

        storage = self.nodes[0].eth_getStorageAt(
            self.smartContractAddress, "0x0", initialBlockNumber
        )  # Test querying previous block
        assert_equal(
            storage,
            "0x0000000000000000000000000000000000000000000000000000000000000000",
        )

    def run_test(self):
        self.setup()

        self.nodes[0].transferdomain(
            [
                {
                    "src": {"address": self.address, "amount": "100@DFI", "domain": 2},
                    "dst": {
                        "address": self.creationAddress,
                        "amount": "100@DFI",
                        "domain": 3,
                    },
                    "singlekeycheck": False,
                }
            ]
        )
        self.nodes[0].generate(1)

        self.test_deploy_smart_contract()

        self.test_smart_contract_address_state_storage()


if __name__ == "__main__":
    EVMTest().main()
