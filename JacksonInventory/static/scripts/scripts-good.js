function addProduct() {
  const barcode = document.getElementById("barcode").value;
  const url = `https://world.openfoodfacts.org/api/v0/product/${barcode}.json`;

  fetch(url)
    .then(response => response.json())
    .then(data => {
      const ProductName = data.product.product_name;
      const ProductDescription = data.product.generic_name;
      //const ProductQty = "new";
      var ProductQty = 1;
      const imageUrl = data.product.image_url;

      console.log("image:  " + imageUrl)

      document.getElementById("barcode").value = barcode;
      document.getElementById("productname").value = ProductName;
      document.getElementById("qty").value = ProductQty;
      document.getElementById("productimage").value = imageUrl;
      document.getElementById("productimage_show").src = imageUrl;
      // document.getElementById("barcode").value = "";
      var audio = new Audio('static/sounds/positive.mp3');
      audio.play();
    })
    .catch(error => console.error(error));
    var audio = new Audio('scripts/sounds/negative.mp3');
    audio.play();
  
}