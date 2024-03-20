import openpyxl
import httpx
from selectolax.parser import HTMLParser
import time


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


# Export data to Excel
def export_to_xlsx(products_list):
    wb = openpyxl.Workbook()
    ws = wb.active

    # Write headers
    headers = products_list[0].keys() if products_list else []
    ws.append(list(headers))

    # Write data
    for product in products_list:
        ws.append(list(product.values()))

    # Save to Excel file
    wb.save('products.xlsx')
    print('Data saved to products.xlsx')


# Main function
def main():
    baseurl = "https://www.rei.com/c/watersports?page="
    products_list = []
    for i in range(1, 5):
        print(f"Page {i}")
        html = get_html(baseurl, i)
        # If we exceeded the page:
        if html is False:
            break
        # Retrieve the yielded items
        data = parse_page(html)
        # Iterate over the items generated
        for item in data:
            products_list.append(item)
        # Wait a second before scraping next page
        time.sleep(1)

    # Export to Excel
    export_to_xlsx(products_list)

    print(f'Total products: {len(products_list)}')
    print(products_list)


if __name__ == "__main__":
    main()
