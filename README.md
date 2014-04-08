inuit
======

I have a modest and mixed portfolio of crypto-currencies which I wanted to take off-line and put into cold storage. I found that to do this I would have to generate paper wallets for each currency using a different paper wallet generator each time.
What I really wanted was a single application that could generate addresses and private keys for multiple currencies so that I could install it on a Raspberry Pi or Linux Live USB stick. This would allow me to cold store all my currencies in one place and with a small amount of effort.

To this end I have created inuit, cold storage address generator for crypto-currency portfolios.

 * inuit can currently generate compressed address / private key pairs for Bitcoin, Litecoin, Namecoin, Peercoin, Primecoin, Dogecoin, Vertcoin, Feathercoin, Quarkcoin, Anoncoin, BBQcoin, Devcoin, Freicoin, Franko, Novacoin, Terracoin, Worldcoin and Yacoin
 
 * The key pairs are stored in an sqlite database which is AES encrypted when not in use.
 
 * There is optional BIP38 encryption and decryption available for all currency pairs.
 
 * New currencies can be added to the system by scanning an example private key
 
For more information, take a look at the website [http://inuit-wallet.co.uk](http://inuit-wallet.co.uk)

inuit is written in Python and the source code is available on [github](https://github.com/inuitwallet/inuit). It is still in active development and features will be added as time and demand allow.

I hope you find inuit as useful as I do. If you have any questions or suggestions, leave a comment on the website or email (details on the website)
