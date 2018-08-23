# Amazon Seller List

Amazon Seller List Scraper written in Python 3 to extract seller information of product based on its ASIN. If you would like to know more about this scraper
you can check it out at the blog post 'How to scrape seller prices of products from Amazon'

## Getting Started
These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Fields to Extract
1. Seller Name
2. Price
3. Rating of Seller
4. Product Condition
5. Delivery Options
6. Product Shipping
7. Positive Percentage

### Prerequisites
For this web scraping tutorial usng Python 3, we will need some some packages:

* Python Requests
* LXML
* UnicodeCSV

### Installation

PIP to install the following packages in Python (https://pip.pypa.io/en/stable/installing/)

Python Requests, to make requests and download the HTML content of the pages (http://docs.python-requests.org/en/master/user/install/)

Python LXML, for parsing the HTML Tree Structure using Xpaths (Learn how to install that here – http://lxml.de/installation.html)

## Running the Scraper

We will execute the script to get the offer listing of the ASIN B01DQ2B8UY:

```
python3 amazon-seller-list ASIN condition shipping

python3 amazon-seller-list B01DQ2B8UY "new" "prime"
```

## Sample Output
This will create a CSV file:

[Sample Output](https://github.com/scrapehero/amazon-seller-list/blob/master/B01DQ2B8UY-sellers.csv)
