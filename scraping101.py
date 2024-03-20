import httpx
from selectolax.parser import HTMLParser


def get_html(baseurl, page):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }

    resp = httpx.get(baseurl+str(page), headers=headers, follow_redirects=True)
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
        return html.css_first(selector).text()
    except AttributeError:
        return None


# Select all product and iterate over them:
def parse_page(html):
    products = html.css("li.VcGDfKKy_dvNbxUqm29K")

    for product in products:
        savings_text = extract_text(
            product, "div[data-ui=savings-percent-variant2]")
        savings = savings_text.split()[1] if savings_text is not None else None
        item = {
            "name": extract_text(product, ".Xpx0MUGhB7jSm5UvK2EY"),
            "fullprice": extract_text(product, "span[data-ui=full-price]"),
            "saleprice": extract_text(product, "span[data-ui=sale-price]"),
            "savings": savings,
        }
        yield item

# Main function


def main():
    baseurl = "https://www.rei.com/c/watersports?page="
    products_list = []
    for i in range(1, 80):
        print('Page '+str(i))
        html = get_html(baseurl, i)
        # If we exceeded the page:
        if html is False:
            break
        # Retrieve the yielded items
        data = parse_page(html)
        # Iterate over the items generated
        for item in data:
            products_list.append(item)

    print('Total products: '+str(len(products_list)))
    print(products_list)


if __name__ == "__main__":
    main()
