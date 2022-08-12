#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import argparse
import json
import graphviz
import requests
import web3
from dotenv import load_dotenv, dotenv_values


APP_NAME = "Contract Explorer"
APP_VERSION = "0.1"


#############################################################################
# Config.                                                                   #
#############################################################################

class Config(object):

    def __init__(self):
        load_dotenv()
        self.env: dict = dotenv_values(".env")
        self.w3: object = None
        self.etherscan: Etherscan = None
        self.recursive: bool = False


config = Config()


#############################################################################
# Etherscan.                                                                #
#############################################################################

class Etherscan(object):

    def __init__(self, endpoint_url: str, api_key: str):
        self.endpoint_url = endpoint_url
        self.api_key = api_key

    def get(self, params: str):
        params += f"&apikey={self.api_key}"
        resp = requests.get(self.endpoint_url + "/api?" + params)
        return resp.json()["result"]


class Ethereum(object):

    def __init__(self, rpc: str = config.env["ETHERSCAN_RPC"]):
        config.w3 = web3.Web3(web3.Web3.HTTPProvider(rpc))
        config.etherscan = Etherscan(
            config.env["ETHERSCAN_API_URL"],
            config.env["ETHERSCAN_API_KEY"]
        )


class Polygon(Ethereum):

    def __init__(self):
        super().__init__(config.env["POLYGON_RPC"])
        config.w3.middleware_onion.inject(
            web3.middleware.geth_poa_middleware, layer=0)
        config.etherscan = Etherscan(
            config.env["POLYGONSCAN_API_URL"],
            config.env["POLYGONSCAN_API_KEY"]
        )


class Gnosis(Ethereum):

    def __init__(self):
        super().__init__(config.env["GNOSIS_RPC"])
        config.w3.middleware_onion.inject(
            web3.middleware.geth_poa_middleware, layer=0)
        config.etherscan = Etherscan(
            config.env["GNOSIS_API_URL"],
            config.env["GNOSIS_API_KEY"]
        )


#############################################################################
# Contract Explorer.                                                        #
#############################################################################

class Argument(object):

    def __init__(self, name: str, type: str):
        self.name = name
        self.type = type

    def __str__(self):
        return f"{self.type} {self.name}"

    def to_dot(self):
        return f"<i>{self.type}</i> {self.name}"


class Function(object):

    def __init__(self, name: str, args: str, returns: str):
        self.name = name
        self.args = args
        self.returns = returns

    def __str__(self):
        args = ",".join([str(x) for x in self.args])
        returns = ",".join([str(x) for x in self.returns])

        o = f"{self.name}({args})"
        if returns:
            o += f" : {returns}"
        return o

    def to_dot(self):
        args = ", ".join([x.to_dot() for x in self.args])
        returns = ", ".join([str(x) for x in self.returns])

        o = f"<b>{self.name}</b>({args})"
        if returns:
            o += f" : {returns}"
        return o


class Contract(object):

    def __init__(self, address: str, abi: dict):
        self.address = config.w3.toChecksumAddress(address)
        self.abi = abi
        self.read: list = []
        self.write: list = []
        self.name: str = ""

        self.contract = config.w3.eth.contract(
            address=self.address, abi=self.abi)

        for line in self.abi:
            if line["type"] != "function":
                continue
            name = line["name"]

            inputs = [Argument(i['name'], i['type'])
                      for i in line["inputs"] if "type" in i]
            outputs = [Argument(i['name'], i['type'])
                       for i in line["outputs"] if "type" in i]

            f = Function(name, inputs, outputs)

            if "view" in line["stateMutability"]:  # or "pure"
                self.read.append(f)
            elif "nonpayable" or "payable" in line["stateMutability"]:
                self.write.append(f)

    def to_dot(self):
        node = '<<table BORDER="0" CELLBORDER="1" CELLSPACING="0">'
        node += f'<tr><td bgcolor="#0496FF"><font color="white" >{self.name} - {self.address}</font></td></tr>'

        node += f'<tr><td bgcolor="grey">read</td></tr>'
        for fct in self.read:
            node += f'<tr><td align="left" port="{fct.name}">{fct.to_dot()}</td></tr>'

        node += f'<tr><td bgcolor="grey">write</td></tr>'
        for fct in self.write:
            node += f'<tr><td align="left" port="{fct.name}" >{fct.to_dot()}</td></tr>'

        node += '</table>>'
        return node


class ContractExplorer(object):

    def __init__(self, address: str, output_filename: str):
        self.address = address
        self.contracts: dict = {}
        self.output_filename = output_filename

    def download_abi(self, address: str):
        # TODO: In a next version, try to grab the bytecode and decompile it. For smart contracts that did not provide the source code.
        params = f"module=contract&action=getabi&address={address}"
        try:
            return json.loads(config.etherscan.get(params))
        except (json.decoder.JSONDecodeError, TypeError):
            # The dev did not provided the smart contract.
            return None

    def download_sourcecode(self, address: str):
        params = f"module=contract&action=getsourcecode&address={address}"
        return config.etherscan.get(params)

    def child_contract(self, dot: graphviz.Digraph, address: str):
        # If we already know this contract, leave recursion.
        if address in self.contracts:
            return

        # Download the smart contract's abi.
        abi = self.download_abi(address)
        if abi is None:
            return

        # The smart contract's name is included in the source code.
        sourcecode = self.download_sourcecode(address)[0]
        name = sourcecode["ContractName"]

        contract = Contract(address, abi)
        contract.name = name
        self.contracts[contract.address] = contract
        print(f"[+] {contract.address} - {name}")
        dot.node(f"{contract.address}", contract.to_dot())

        if config.recursive is True:
            for read in contract.read:
                for ret in read.returns:

                    # If there is only one return value of type address, that's probably a link to another smart contract.
                    if len(read.returns) == 1 and ret.type == "address" and len(read.args) == 0:
                        child_address = contract.contract.functions[read.name](
                        ).call()
                        dot.edge(f"{contract.address}:{read.name}",
                                 f"{child_address}")
                        self.child_contract(dot, child_address)

    def graph(self):
        dot = graphviz.Digraph(comment=f"{self.address} smart contract", node_attr={
                               'shape': 'plaintext'})
        self.child_contract(dot, self.address)
        print(
            f"[+] Graph rendered. Check `{self.output_filename}` and `{self.output_filename}.pdf`")
        dot.render(self.output_filename, format='pdf', view=True)


#############################################################################
# Main.                                                                     #
#############################################################################

def main(args):
    if args.ethereum is True:
        Ethereum()
    elif args.gnosis is True:
        Gnosis()
    elif args.polygon is True:
        Polygon()

    if args.recursive is True:
        config.recursive = True

    if args.output[-4:] == ".pdf":
        args.output = args.output[:-4]

    explorer = ContractExplorer(args.address, args.output)
    explorer.graph()


if __name__ == "__main__":
    print("-=[ {0} v{1} ]=-\n".format(APP_NAME, APP_VERSION))
    parser = argparse.ArgumentParser(description=APP_NAME)

    parser.add_argument('-a', '--address',
                        type=str,
                        required=True,
                        help='Target smart contract address.')
    parser.add_argument('-r', '--recursive',
                        required=False,
                        action='store_true',
                        help='Recursive search.')
    parser.add_argument('-o', '--output',
                        required=False,
                        type=str,
                        default="output",
                        help='Output filename.')

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-e', '--ethereum',
                       required=False,
                       action='store_true',
                       help='Ethereum Network')
    group.add_argument('-g', '--gnosis',
                       required=False,
                       action='store_true',
                       help='Gnosis Network')
    group.add_argument('-p', '--polygon',
                       required=False,
                       action='store_true',
                       help='Polygon')

    args = parser.parse_args()
    raise SystemExit(main(args))
