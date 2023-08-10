import json
import scrapy
import os

class TargetSpider(scrapy.Spider):
    name = 'target'
    
    def __init__(self, url, **kwargs):
        super().__init__(**kwargs)
        self.start_urls = [url]
        self.headers = {
            'accept': 'application/json',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
        }
    def start_requests(self):
        for url in self.start_urls:
            if  '/A-' in url:
                tcin_id = url.split('/A-')[1]
                yield scrapy.Request(
                    url,
                    callback=self.parse,
                    dont_filter=True,
                    headers=self.headers,
                    meta={"tcin_id": tcin_id}
                )

    def parse(self, response):
        get_json_for = response.text.split("'__CONFIG__':")[1].split(")), writable: false ")[0].split('{ configurable: false, enumerable: true, value: deepFreeze(JSON.parse("')[1].split('")), writeable: false }')[0]
        clear_json = get_json_for.replace("\\", "")
        formatted_json = json.loads(clear_json)

        api_key = formatted_json['defaultServicesApiKey']
        tcin_id = response.meta['tcin_id']

        url = f"https://redsky.target.com/redsky_aggregations/v1/web/pdp_client_v1?key={api_key}&tcin={tcin_id}&pricing_store_id=1771"
        yield scrapy.Request(
            url,
            callback=self.get_all_data,
            dont_filter=True,
            headers=self.headers,
            meta={"tcin_id": response.meta['tcin_id']}
        )

    def get_all_data(self, response):
        folder_name = response.meta['tcin_id']
        if not os.path.exists(folder_name):
            os.mkdir(folder_name)

        final_data = json.loads(response.text)['data']['product'] 
        if 'children' in final_data:
            for multi_data in final_data['children']:
                try:
                    url = multi_data['item']['enrichment']['buy_url']
                except:
                    url = None
                try:
                    tcin = multi_data['tcin']
                except:
                    tcin = None
                try:
                    upc = multi_data['item']['primary_barcode']
                except:
                    upc = None
                try:
                    price_amount = multi_data['price']['current_retail']
                except:
                    price_amount = None
                try:
                    price_for_curanccy = multi_data['price']['formatted_current_price']
                    if "$" in price_for_curanccy:
                        currency =  "USD"
                except:
                    currency = None
                try:
                    description = multi_data['item']['product_description']['downstream_description']
                    description = description.replace("</br>","").replace("<br>","").replace("<br />","")
                except:
                    description = None
                try:
                    if multi_data['item']['enrichment']['nutrition_facts']:
                        ingredients =  [multi_data['item']['enrichment']['nutrition_facts']['ingredients']]
                except:
                    ingredients = []
                try:
                    bullets = multi_data['item']['product_description']['soft_bullet_description']
                    bullets = bullets.replace("&bull;","").replace("<br>","\n")
                except:
                    bullets = None
                try:
                    features = [item.replace('<B>', '').replace('</B>', '') for item in multi_data['item']['product_description']['bullet_descriptions']]
                except:
                    features = []

                items = {
                    "url": url,
                    "tcin": tcin,
                    "upc": upc,
                    "price_amount": price_amount,
                    "currency": currency,
                    "description": description,
                    "specs": None,
                    "ingredients":ingredients,
                    "bullets": bullets,
                    "features": features
                }
# www.target.com\87663380
                with open(f'.//{folder_name}//{tcin}.json', 'w',encoding='utf-8') as json_file:
                    json.dump(items, json_file, indent=4)
                    self.logger.info("JSON file saved.")
        else:
            try:
                url = final_data['item']['enrichment']['buy_url']
            except:
                url = None
            try:
                tcin = response.meta['tcin_id']
            except:
                tcin = None
            try:
                upc = final_data['item']['primary_barcode']
            except:
                upc = None
            try:
                price_amount = final_data['price']['current_retail']
            except:
                price_amount = None
            try:
                price_for_curanccy = final_data['price']['formatted_current_price']
                if "$" in price_for_curanccy:
                    currency =  "USD"
            except:
                currency = None
            try:
                description = final_data['item']['product_description']['downstream_description']
                description = description.replace("</br>","").replace("<br>","").replace("<br />","")
            except:
                description = None
            try:
                if final_data['item']['enrichment']['nutrition_facts']:
                    ingredients =  [final_data['item']['enrichment']['nutrition_facts']['ingredients']]
            except:
                ingredients = []
            try:
                bullets = final_data['item']['product_description']['soft_bullet_description']
                bullets = bullets.replace("&bull;","").replace("<br>","\n")
            except:
                bullets = None
            try:
                features = [item.replace('<B>', '').replace('</B>', '') for item in final_data['item']['product_description']['bullet_descriptions']]
            except:
                features = []

            items = {
                "url": url,
                "tcin": tcin,
                "upc": upc,
                "price_amount": price_amount,
                "currency": currency,
                "description": description,
                "specs": None,
                "ingredients": ingredients,
                "bullets": bullets,
                "features": features
            }
            with open(f'.//{folder_name}//{tcin}.json', 'w',encoding='utf-8') as json_file:
                    json.dump(items, json_file, indent=4)
                    self.logger.info("JSON file saved.")
