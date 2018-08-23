import requests
from lxml import html
from lxml.etree import ParserError
import json
from time import sleep
import argparse
import unicodecsv as csv
import traceback


def parse_offer_details(url):
    '''
    Function to parse seller details from amazon offer listing page
    eg:https://www.amazon.com/gp/offer-listing/
    :param url:offer listing url
    :rtype: seller details as json
    '''
    # Add some recent user agent to prevent blocking from amazon
    headers = {
                'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
    }

    for retry in range(5):
        try:
            print("Downloading and processing page :", url)
            response = requests.get(url, headers=headers)
            if response.status_code == 403:
                raise ValueError("Captcha found. Retrying")

            response_text = response.text
            parser = html.fromstring(response_text)
            base_url = "https://www.amazon.com/"
            parser.make_links_absolute(base_url)
            XPATH_PRODUCT_LISTINGS = "//div[contains(@class, 'a-row a-spacing-mini olpOffer')]"
            # Parsing seller list
            listings = parser.xpath(XPATH_PRODUCT_LISTINGS)
            offer_list = []

            if not listings:
                print("no sellers found")
                return offer_list

            # parsing individual seller
            for listing in listings:
                XPATH_PRODUCT_PRICE = ".//span[contains(@class, 'olpOfferPrice')]//text()"
                XPATH_PRODUCT_PRIME = ".//i/@aria-label"
                XPATH_PRODUCT_SHIPPING = ".//p[contains(@class, 'olpShippingInfo')]//text()"
                XPATH_PRODUCT_CONDITION = ".//span[contains(@class, 'olpCondition')]//text()"
                XPATH_PRODUCT_DELIVERY = ".//div[contains(@class, 'olpDeliveryColumn')]//text()"
                XPATH_PRODUCT_SELLER1 = ".//h3[contains(@class, 'olpSellerName')]//a/text()"
                XPATH_PRODUCT_SELLER2 = ".//h3[contains(@class, 'olpSellerName')]//img//@alt"
                XPATH_PRODUCT_SELLER_RATTING = ".//div[contains(@class, 'olpSellerColumn')]//span[contains(@class, 'a-icon-alt')]//text()"
                XPATH_PRODUCT_SELLER_PERCENTAGE = ".//div[contains(@class, 'olpSellerColumn')]//b/text()"
                XPATH_PRODUCT_SELLER_URL = ".//h3[contains(@class, 'olpSellerName')]//a/@href"
                
                product_price = listing.xpath(XPATH_PRODUCT_PRICE)
                product_price = product_price[0].strip()
                product_prime = listing.xpath(XPATH_PRODUCT_PRIME)
                product_condition = listing.xpath(XPATH_PRODUCT_CONDITION)
                product_shipping = listing.xpath(XPATH_PRODUCT_SHIPPING)
                delivery = listing.xpath(XPATH_PRODUCT_DELIVERY)
                seller1 = listing.xpath(XPATH_PRODUCT_SELLER1)
                seller2 = listing.xpath(XPATH_PRODUCT_SELLER2)
                seller_ratting =listing.xpath(XPATH_PRODUCT_SELLER_RATTING)
                seller_percentage = listing.xpath(XPATH_PRODUCT_SELLER_PERCENTAGE)
                seller_url = listing.xpath(XPATH_PRODUCT_SELLER_URL)

                # cleaning parsed data
                product_prime = product_prime[0].strip() if product_prime else None
                product_condition = ''.join(''.join(product_condition).split()) if product_condition else None
                product_shipping_details = ' '.join(''.join(product_shipping).split()).lstrip("&").rstrip("Details") if product_shipping else None
                cleaned_delivery = ' '.join(''.join(delivery).split()).replace("Shipping rates and return policy.", "").strip() if delivery else None
                product_seller = ''.join(seller1).strip() if seller1 else ''.join(seller2).strip()
                seller_ratting = seller_ratting[0].split()[0].strip() if seller_ratting else None
                seller_percentage = seller_percentage[0].strip() if seller_percentage else None
                seller_url = seller_url[0].strip() if seller_url else None

                offer_details = {
                                'price': product_price,
                                'shipping_detais': product_shipping_details,
                                'condition': product_condition,
                                'prime': product_prime,
                                'delivery': cleaned_delivery,
                                'seller': product_seller,
                                'seller_rating':seller_ratting,
                                'seller_percentage': seller_percentage,
                                'seller_url':seller_url,
                                'asin': asin,
                                'url': url
                }
                offer_list.append(offer_details)
            return offer_list

        except ParserError:
            print("empty page found")
            break
        except:
            print(traceback.format_exc())
            print("retying :", url)
        
if __name__ == '__main__':
    # defining arguments   
    parser = argparse.ArgumentParser()
    parser.add_argument('asin', help='unique product id, eg "B01DQ2B8UY"')
    parser.add_argument('condition', help='product condition eg "new", "used", "all", "like_new", "verygood", "acceptable", "good"', default="all")
    parser.add_argument('shipping', help='product shipping eg "prime", "all"', default="all")
    args = parser.parse_args()
    asin = args.asin
    condition = args.condition
    shipping = args.shipping

    # for creating url according to the filter applied
    condition_dict = {'new': '&f_new=true',
                    'used': '&f_used=true',
                    'all': '&condition=all',
                    'like_new': '&f_usedLikeNew=true',
                    'good': '&f_usedGood=true',
                    'verygood': '&f_usedVeryGood=true',
                    'acceptable': 'f_usedAcceptable=true'
    }
    shipping_dict = {'prime': '&f_primeEligible=true',
                    'all': '&shipping=all'
    }

    url = 'https://www.amazon.com/gp/offer-listing/'+asin+'/ref='+condition_dict.get(condition)+shipping_dict.get(shipping)
    data = parse_offer_details(url)
    
    if data:
        print ('Writing results to  the file: ', asin, '-sellers.csv')
        with open(asin+'-sellers.csv', 'wb')as csvfile:
            fieldnames = ['seller', 'seller_rating', 'seller_percentage', 'price', 'prime', 'condition', 'shipping_detais', 'delivery', 'seller_url','url', 'asin']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
            writer.writeheader()
            for row in  data:
                writer.writerow(row)
