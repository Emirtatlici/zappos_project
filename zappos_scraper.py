import requests
import json
from pandas import json_normalize
import pandas as pd
import signal
import logging

class ZapposScraper:
    def __init__(self):
        self.cookie_data = "your_cookie_data_here"
        self.data = pd.DataFrame()
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)
        self.exit_gracefully = False

    def signal_handler(self, signum, frame):
        self.logger.info("Signal received. Saving the scraped data before exiting...")
        self.exit_gracefully = True

    def fetch_data(self, start_page, end_page, gender=None, category=None):
        signal.signal(signal.SIGINT, self.signal_handler)  

        for i in range(start_page, end_page + 1):
            url = "https://prod.olympus.zappos.com/Search/zso/filters/agEC4gIBDQ.zso"

            querystring = {
                "limit": "100",
                "includes": "[\"productSeoUrl\",\"pageCount\",\"reviewCount\",\"productRating\",\"onSale\",\"isNew\",\"zsoUrls\",\"isCouture\",\"msaImageId\",\"facetPrediction\",\"phraseContext\",\"currentPage\",\"facets\",\"melodySearch\",\"styleColor\",\"seoBlacklist\",\"seoOptimizedData\",\"enableCrossSiteSearches\",\"badges\",\"termLanderAutoFacetOverride\",\"boostQueryOverride\",\"enableSwatches\",\"onHand\",\"enableBestForYouSort\",\"applySyntheticTwins\",\"imageMap\",\"enableUniversalShoeSizeFacets\",\"enableSingleShoes\",\"enableCrossSiteSearches\"]",
                "relativeUrls": "true",
                "siteId": "1",
                "subsiteId": "17",
                "page": i
            }

            if gender:
                querystring["t"] = gender + "+"

            if category:
                querystring["t"] += category

            payload = ""
            headers = {
                "accept": "*/*",
                "accept-language": "en-US,en;q=0.9,tr-TR;q=0.8,tr;q=0.7",
                "cookie": self.cookie_data,
                "origin": "https://www.zappos.com",
                "referer": "https://www.zappos.com/",
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": "Windows",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-site",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.0.0 Safari/537.36",
                "x-session-requested": "1"
            }

            try:
                response = requests.get(url, headers=headers, params=querystring)
                response.raise_for_status()
                x = json.loads(response.text)
                ff = json_normalize(x["results"])
                self.data = pd.concat([ff, self.data])
                self.logger.info(f"Page {i} fetched successfully. {end_page - i} pages left.")
                if self.exit_gracefully:
                    break
            except Exception as e:
                self.logger.error(f"Error: {e}")
                break

        return self.data
