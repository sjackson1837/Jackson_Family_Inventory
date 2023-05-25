function addProduct() {
  const barcode = document.getElementById("barcode").value;
  const url = `https://world.openfoodfacts.org/api/v0/product/${barcode}.json`;

  fetch(url)
    .then(response => response.json())
    .then(data => {
      if (data.status === 0) {
        // Barcode not found, allow typing product information
        document.getElementById("productname").readOnly = false;
        document.getElementById("qty").readOnly = false;
        document.getElementById("productimage").readOnly = false;
        document.getElementById("productimage").value = "https://cdn.dribbble.com/users/1247449/screenshots/3984840/no_img.png";

        document.getElementById("productimage_show").src = "https://cdn.dribbble.com/users/1247449/screenshots/3984840/no_img.png";
        var audio = new Audio('scripts/sounds/negative.mp3');
        audio.play();
      } else {
        // Barcode found, populate product information
        const ProductName = data.product.product_name;
        const ProductDescription = data.product.generic_name;
        // const ProductQty = "new";
        var ProductQty = 1;
        const imageUrl = data.product.image_url;

        console.log("image:  " + imageUrl)

        document.getElementById("barcode").readOnly = true;
        document.getElementById("productname").readOnly = true;
        document.getElementById("productimage").readOnly = true;
        document.getElementById("barcode").value = barcode;
        document.getElementById("productname").value = ProductName;
        document.getElementById("qty").value = ProductQty;
        document.getElementById("productimage").value = imageUrl;
        document.getElementById("productimage_show").src = imageUrl;
        // document.getElementById("barcode").value = "";
        var audio = new Audio('static/sounds/positive.mp3');
        audio.play();
      }
    })
    .catch(error => console.error(error));
}
