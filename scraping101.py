import httpx
from selectolax.parser import HTMLParser
import time
from urllib.parse import urljoin
from dataclasses import dataclass, asdict, fields
from typing import Optional
import json
import csv


@dataclass
class Item:
    name: Optional[str] = None
    item_number: Optional[str] = None
    price: Optional[str] = None
    rating: Optional[float] = None


def get_html(url, **kwargs):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }
    if kwargs.get("page"):
        resp = httpx.get(url+str(kwargs.get("page")),
                         headers=headers, follow_redirects=True)
    else:
        resp = httpx.get(url, headers=headers, follow_redirects=True)

    # If we are trying to access an inexistent page --> return False
    try:
        resp.raise_for_status()
    except httpx.HTTPStatusError as exc:
        print(
            f"Error response {exc.response.status_code} while requesting {exc.request.url!r}. Page limit exceeded")
        return False
    html = HTMLParser(resp.text)

    # Return page html
    return html


# This function is necessary for the cases when there is no selector found
def extract_text(html, selector):
    try:
        text = html.css_first(selector).text()
        return clean_data(text)
    except AttributeError:
        return None


def export_to_json(products):
    with open("products.json", "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=4)
    print("Saved to json")


def export_to_csv(products):
    field_names = [field.name for field in fields(Item)]
    with open("products.csv", "w") as f:
        writer = csv.DictWriter(f, field_names)
        writer.writeheader()
        writer.writerows(products)
    print("Saved to csv")


def append_to_csv(products):
    field_names = [field.name for field in fields(Item)]
    with open("products.csv", "a") as f:
        writer = csv.DictWriter(f, field_names)
        writer.writerow(products)
    print("Item appended to csv")


def clean_data(value):
    chars_to_remove = ["$", "Item", "#"]
    for char in chars_to_remove:
        if char in value:
            value = value.replace(char, "")
    return value.strip()


# Select all product and iterate over them:
def parse_page(html: HTMLParser):
    products = html.css("li.VcGDfKKy_dvNbxUqm29K")

    for product in products:
        yield urljoin("https://www.rei.com/", product.css_first("a").attributes["href"])


def parse_item_page(html: HTMLParser):
    new_item = Item(
        name=extract_text(html, "h1#product-page-title"),
        item_number=extract_text(html, "span#product-item-number"),
        price=extract_text(html, "span#buy-box-product-price"),
        rating=extract_text(html, "span.cdr-rating__number_15-0-0"),
    )
    return asdict(new_item)


# Main function
def main():
    baseurl = "https://www.rei.com/c/watersports?page="
    products_list = []
    for i in range(1, 2):
        print(f"Page {i}")
        html = get_html(baseurl, page=i)
        if html is False:
            break
        products_urls = parse_page(html)
        # Iterate over the urls generated
        for url in products_urls:
            print(url)
            html = get_html(url)
            products_list.append(parse_item_page(html))
            # append_to_csv(parse_item_page(html))
            time.sleep(0.2)

    export_to_json(products_list)
    # export_to_csv(products_list)


if __name__ == "__main__":
    main()
