# Introduction
McAfee Pump and Dump bot.

Was used around a year ago when John McAfee was pumping and dumping cryptocurrencies from his Twitter account. 

Could be rewritten to play into pump and dumps in the future. Even though I would highly advice to not participate in pump and dump schemes, the bot works and made me some profit.

# Dependencies
  - PIL (pip install PIL)
  - Tweepy w/ Twitter API key (pip install tweepy, [Twitter API](https://apps.twitter.com/))
  - Bittrex-python w/ API key (pip install python-bittrex, [Bittrex API](https://support.3commas.io/hc/en-us/articles/360000235254-Bittrex-creating-an-API-key))
  - [Binance API Key](https://support.binance.com/hc/en-us/articles/360002502072-How-to-create-API)
  - Pytesseract (follow the instructions from [here](https://pypi.org/project/pytesseract/))

# Usage 

Set up the funds and markup variables (it doesn't ask the user, you'll have to do it in the code) and run the code. It then automatically starts monitoring for tweets with images (or text) of cryptocurrencies on McAfee's Twitter and buy those with all the funds you specified previously, selling it for your specified markup afterwards.

# TODO
  - None as of now.
