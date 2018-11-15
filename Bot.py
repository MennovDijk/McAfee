from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from io import BytesIO
from PIL import Image
from bittrex.bittrex import Bittrex, API_V1_1
import re, time, pytesseract, requests
from image_cleaner import process_image_for_ocr
from binance_python import Client

# Locate pytesseract folder for image recognition
pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files (x86)\\Tesseract-OCR\\tesseract'

# Total amount in BTC you want to use to purchase the coin
funds = 0.17

# Markup over the price you want, 1.12 indicates selling the coin for a 12% profit margin (excluding transaction costs)
markup = 1.12

# Twitter API keys
consumer_key = 'CONSUMER_KEY'
consumer_secret = 'CONSUMER_SECRET'
access_token = 'ACCESS_TOKEN'
access_token_secret = 'ACCESS_TOKEN_SECRET'

# Create Twitter API listener or whatever
auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

# Bittrex and Binance API keys
my_bittrex = Bittrex("API_KEY", "API_SECRET", api_version=API_V1_1)
my_binance = Client("API_KEY", "API_SECRET")


# REALLY UGLY CODE TO CREATE INVESTMENT UNIVERSE FOR BINANCE AND BITTREX
bittrex_markets = my_bittrex.get_markets()
bittrex_markets_set = set()
for i in range(len(bittrex_markets['result'])):
    bittrex_markets_set.add(bittrex_markets['result'][i]['MarketCurrency'])
binance_markets = my_binance.get_all_tickers()
binance_markets_l = []
for i in binance_markets:
    binance_markets_l.append(i['symbol'])
binance_markets_l = list((filter(lambda x: x.endswith('BTC'), binance_markets_l)))
for i in range(len(binance_markets_l)):
    binance_markets_l[i] = binance_markets_l[i][:-3]
binance_markets_set = set(binance_markets_l)

#Creates stream listener
class StdOutListener(StreamListener):

    # Initialize class with a count (used for keeping track of tweets)
    def __init__(self, api=None):
        super(StdOutListener, self).__init__()
        self.count = 0

    def on_status(self, status):
        if (status.user.screen_name == "officialmcafee"):
            try:
                url = status.entities['media'][0]['media_url']
                response = requests.get(url)
                img = Image.open(BytesIO(response.content))
                img.save("img1.bmp")
                img_preprocessed = process_image_for_ocr("img1.bmp")
                img2 = Image.fromarray(img_preprocessed)
                contents = pytesseract.image_to_string(img2).upper()
                self.buy_algo(text=contents)
            except Exception as e: print(e, "Probably no image in the tweet.")

            #try:
            self.buy_algo(text=status.text.upper())
            #except Exception as e: print(e)

            print(status.text)
            #playsound('D:\\Videos\\Background music\\DMM special new\\SOUND EFFECTS FOR VIDEO\\SAY WHAT.mp3')
        self.count += 1

        if self.count % 10 == 0:
            print(self.count)

        return True


    def on_error(self, status):
        print('Error in the API query:',status)

    def limit_buy_bittrex(self, market, quantity, rate):
        return my_bittrex.buy_limit(market=market, quantity=quantity, rate=rate)

    def limit_sell_bittrex(self, market, quantity, rate, markup):
        return my_bittrex.sell_limit(market=market, quantity=quantity, rate=rate * markup)

    def limit_buy_binance(self, market, quantity, rate, recv):
        stringed_rate = "{0:1.8f}".format(rate)
        return my_binance.order_limit_buy(symbol = market, quantity = quantity, price = stringed_rate, recvWindow = recv)

    def limit_sell_binance(self, market, quantity, rate, markup, recv):
        rate = round(rate * markup, 8)
        stringed_rate = "{0:1.8f}".format(rate)
        return my_binance.order_limit_sell(symbol = market, quantity = quantity, price = stringed_rate, recvWindow = recv)

    def market_buy_binance(self, market, quantity, recv):
        return my_binance.order_market_buy(symbol = market, quantity = quantity, recvWindow = recv)

    def market_sell_binance(self, market, quantity, recv):
        return my_binance.order_market_sell(symbol=market, quantity=quantity, recvWindow = recv)

    def buy_algo(self, text):
        result = re.search(r'\((.*?)\)', text)
        print("Reached buy_algo with outcome {}".format(result))

        if result:
            if result.group(1) in bittrex_markets_set:
                market = "BTC-" + result.group(1)

                rate = round((float(my_bittrex.get_ticker(market=market)['result']['Ask']) * 1.05), 8)

                quantity = round((funds / rate), 8)

                print()
                print("Bittrex", market, rate, quantity)
                print()

                while True:
                    response = self.limit_buy_bittrex(market=market, quantity=quantity, rate=rate)
                    if response['success'] == True:
                        print("Placed a buy order.")
                        print("Attempting to place sell order...")
                        break
                    time.sleep(1)

                while True:
                    response = self.limit_sell_bittrex(market=market, quantity = quantity, rate = rate, markup = 1.12)
                    if response['success'] == True:
                        print("Placed a sell order.")
                        break
                    time.sleep(1)
            elif result.group(1) in binance_markets_set:
                market = result.group(1) + "BTC"
                rate = round((float(my_binance.get_ticker(symbol = market)['askPrice']) * 1.05), 8)
                quantity = round((funds / rate), 0)
                print(market, rate, quantity)

                recv = 5000

                while True:
                    try:
                        self.limit_buy_binance(market=market, quantity=quantity, recv = recv, rate=rate)
                    except Exception as e:
                        print(e)
                        # Make sure the API doesn't block us.
                        print('Error in buying, attempting again...')
                        recv += 10000
                        time.sleep(1)
                        continue
                    else:
                        break

                recv = 5000

                while True:
                    try:
                        self.limit_sell_binance(market=market, quantity=quantity, recv = recv, rate = rate, markup = 1.12)
                    except Exception as e:
                        print(e)
                        # Make sure the API doesn't block us.
                        print('Error in selling, attempting again...')
                        recv += 10000
                        time.sleep(1)
                        continue
                    else:
                        break
            else:
                print("Crypto not found trading on Binance or Bittrex.")

l = StdOutListener()

while True:
    #try:
    stream = Stream(auth, l)
    stream.filter(follow=["961445378"])
    time.sleep(1)
