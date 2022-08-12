# Description

This is a small tool to quickly identify some interactions between smart contracts.

Currently, it only supports contracts that the dev have pushed the source code.
A version that grabs the bytecode and decompile it is considered.

# Usage

**Installing dependencies**

```console
$ virtualenv -p python3 venv3
$ source venv3/bin/activate
$ pip install -r requirements.txt
$ cp .env.example .env
$ vim .env
```

**Usage**

```console
$ ./contract-explorer.py
-=[ Contract Explorer v0.1 ]=-

usage: contract-explorer.py [-h] -a ADDRESS [-r] (-e | -g | -p)
contract-explorer.py: error: the following arguments are required: -a/--address
```

**Display a simple contract**

```console
$ ./contract-explorer.py -p -a 0xE95DC4d81A4707884E7Db4A53954763b36CB45aE
-=[ Contract Explorer v0.1 ]=-

[+] 0xE95DC4d81A4707884E7Db4A53954763b36CB45aE - AccessController
```

**Recursive example**

```console
$ ./contract-explorer.py -p -a 0xCAe2CaE9a4384B196c0f1bAE59724e0eb9a347e0 -r -o example
-=[ Contract Explorer v0.1 ]=-

[+] 0xCAe2CaE9a4384B196c0f1bAE59724e0eb9a347e0 - ConfigProvider
[+] 0xa802eE4bd9f449295ADb6d73f65118352420758A - AddressProvider
[+] 0xE95DC4d81A4707884E7Db4A53954763b36CB45aE - AccessController
[+] 0x03175c19CB1d30Fa6060331A9ec181e04CAC6aB0 - VaultsCore
[+] 0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270 - WMATIC
[+] 0xc7d868954009Df558ac5fD54032F2B6FB6Ef926c - DebtNotifier
[+] 0x2489DF1F40BcA6DBa1554AafeCc237BBc6d0453c - GovernanceAddressProvider
[+] 0xADAC33f543267c4D59a8c299cF804c303BC3e4aC - UChildERC20Proxy
[+] 0x3D9653936dCd25EA7B23ca81eFe7aE7fB36c282C - UChildERC20
[+] 0x355b8E02e7F5301E6fac9b7cAc1D6D9c86C0343f - MultiSigWalletWithDailyLimit
[+] 0x6Df4822a7e71Ef497bD09845d6B865F2B015DA0b - VotingEscrow
[+] 0xF8cDE3E56b72fD0D7bE77604F396A366912e332f - VotingMiner
[+] 0x2d49E60555D0372bE23e2B24aeB3E5EA55dCB417 - VaultsCoreState
[+] 0x313d1d48430721370EcC57262A7664E375a347Fb - FeeDistributor
[+] 0x57896e135f845301c706F643506629493b6660Ab - LiquidationManager
[+] 0x1f4d9879327E2Ecc488CcC49566286C844aF6f2c - PriceFeed
[+] 0x73366Fe0AA0Ded304479862808e02506FE556a98 - EACAggregatorProxy
[+] 0x310990E8091b5cF083fA55F500F140CFBb959016 - AccessControlledOffchainAggregator
[+] 0x494E19780C3fE5B2a61eE6D6380fEA4B408A2c07 - SimpleWriteAccessController
[+] 0x5A3ca642fdEd17296adDdb53A496ce4f26901596 - GnosisSafeProxy
[+] 0xb0897686c545045aFc77CF20eC7A532E3120E0F1 - LinkToken
[+] 0x6a9F4359350172aC4B1d4132639fE23f9562D778 - SimpleWriteAccessController
[+] 0x74419Ec5Ed2f745beCe0D4e4118DB2f33Eb88367 - RatesManager
[+] 0xE2Aa7db6dA1dAE97C5f5C6914d285fBfCC32A128 - PAR
[+] 0xDe1996189EE1857d79f1F2bebe2A4a2B200bCb44 - VaultsDataProvider
[+] Graph rendered. Check `example` and `example.pdf`
```

**Example of output**

Check [https://github.com/Cizeon/BlockchainTools/blob/main/ContractExplorer/example.pdf](example.pdf).
