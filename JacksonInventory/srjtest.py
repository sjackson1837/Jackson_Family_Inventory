import requests

def get_product_details(barcode):
    url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
    response = requests.get(url)
    
    if response.status_code == 200:
        product_data = response.json()
        if product_data['status'] == 1:
            return product_data['product']
        else:
            return f"Product not found for barcode: {barcode}"
    else:
        return f"Failed to fetch data from Open Food Facts API. Status code: {response.status_code}"

def main():
    barcode = input("Enter the product barcode: ")
    product_details = get_product_details(barcode)
    
    if isinstance(product_details, dict):
        print("Product details:")
        print(f"Product Name: {product_details.get('product_name', 'N/A')}")
        print(f"Brands: {product_details.get('brands', 'N/A')}")
        print(f"Ingredients: {product_details.get('ingredients_text', 'N/A')}")
        print(f"Nutrition Grade: {product_details.get('nutrition_grades_tags', 'N/A')}")
    else:
        print(product_details)

if __name__ == "__main__":
    main()