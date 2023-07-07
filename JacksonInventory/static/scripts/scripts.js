function checkBarcode(event) {
  const barcode = event.target.value;
  const xhr = new XMLHttpRequest();
  xhr.open("POST", "/check_item", true);
  xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
  xhr.onreadystatechange = function () {
    if (xhr.readyState === 4) {
      if (xhr.status === 200) {
        const response = JSON.parse(xhr.responseText);
        if (response.redirect_url) {
          // Barcode found in the database, update quantity and save the record
          window.location.href = response.redirect_url;
        } else if (response.barcode_not_found) {
          // Barcode not found, run the checkItem() function
          checkItem(barcode);
        } else {
          flash("testing flash message");
        }
      }
    }
  };
  xhr.send("barcode=" + barcode);
}

function useItem(event) {
  const barcode = event.target.value;
  const xhr = new XMLHttpRequest();
  xhr.open("POST", "/use_item", true);
  xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
  xhr.onreadystatechange = function () {
    if (xhr.readyState === 4) {
      if (xhr.status === 200) {
        const response = JSON.parse(xhr.responseText);
        if (response.redirect_url) {
          // Barcode found in the database, update quantity and save the record
          window.location.href = response.redirect_url;
        } else if (response.barcode_not_found) {
          // Barcode not found, run the checkItem() function
          //checkItem(barcode);
          alert("Item not found in inventory");
          event.target.value = "";
        } else {
          //flash("testing flash message");
        }
      }
    }
  };
  xhr.send("barcode=" + barcode);
}


function checkItem() {
  const barcode = document.getElementById("barcode").value;
  const url = `https://world.openfoodfacts.org/api/v0/product/${barcode}.json`;

  fetch(url)
    .then(response => response.json())
    .then(data => {
      if (data.status === 0) {
        // Barcode not found, allow typing product information
        document.getElementById("barcode").readOnly = true;
        document.getElementById("barcode").value = barcode;
        document.getElementById("productname").readOnly = false;
        document.getElementById("qty").readOnly = false;
        var ProductQty = 1;
        var MinQty = 1;
        document.getElementById("qty").value = ProductQty;
        document.getElementById("minqty").value = MinQty;
        document.getElementById("productimage_input").readOnly = false;
        document.getElementById("productimage_input").value = "https://st4.depositphotos.com/14953852/22772/v/450/depositphotos_227725020-stock-illustration-image-available-icon-flat-vector.jpg";

        document.getElementById("productimage_show").src = "https://st4.depositphotos.com/14953852/22772/v/450/depositphotos_227725020-stock-illustration-image-available-icon-flat-vector.jpg";
        showProductData();
        var audio = new Audio('scripts/sounds/negative.mp3');
        audio.play();
      } else {
        // Barcode found, populate product information
        const ProductName = data.product.product_name;
        const ProductDescription = data.product.generic_name;
        // const ProductQty = "new";
        var ProductQty = 1;
        var MinQty = 1;
        
        let imageUrl = data.product.image_url;
        
        // Check if the image URL is undefined
        if (typeof imageUrl === 'undefined') {
            imageUrl = 'https://st4.depositphotos.com/14953852/22772/v/450/depositphotos_227725020-stock-illustration-image-available-icon-flat-vector.jpg';
        }

        document.getElementById("barcode").readOnly = true;
        document.getElementById("productname").readOnly = true;
        document.getElementById("productimage_input").readOnly = true;
        document.getElementById("barcode").value = barcode;
        document.getElementById("productname").value = ProductName;
        document.getElementById("qty").value = ProductQty;
        document.getElementById("minqty").value = MinQty;
        document.getElementById("productimage_input").value = imageUrl;
        document.getElementById("productimage_show").src = imageUrl;

        showProductData();
        var audio = new Audio('static/sounds/positive.mp3');
        audio.play();
      }
    })
    .catch(error => console.error(error));
}

function showProductData() {
  const barcodeContainer = document.getElementById('barcodeContainer');
  const productDataContainer = document.getElementById('productDataContainer');
  const productImage = document.getElementById('productimage_show');
  
  barcodeContainer.style.display = 'block';
  productDataContainer.style.display = 'block';
  productImage.style.display = 'block';
}

function incrementQty() {
  console.log("I'm ereererkjerh");
  const qtyInput = document.getElementById('qty');
  let qtyValue = parseInt(qtyInput.value);
  qtyValue = isNaN(qtyValue) ? 0 : qtyValue;
  qtyInput.value = qtyValue + 1;
}

function decrementQty() {
  const qtyInput = document.getElementById('qty');
  let qtyValue = parseInt(qtyInput.value);
  qtyValue = isNaN(qtyValue) ? 0 : qtyValue;
  qtyInput.value = qtyValue > 0 ? qtyValue - 1 : 0;
}

function incrementMinQty() {
  const qtyInput = document.getElementById('minqty');
  let qtyValue = parseInt(qtyInput.value);
  qtyValue = isNaN(qtyValue) ? 0 : qtyValue;
  qtyInput.value = qtyValue + 1;
}

function decrementMinQty() {
  const qtyInput = document.getElementById('minqty');
  let qtyValue = parseInt(qtyInput.value);
  qtyValue = isNaN(qtyValue) ? 0 : qtyValue;
  qtyInput.value = qtyValue > 0 ? qtyValue - 1 : 0;
}

function enableProductNameEditing() {
  document.getElementById("productname").removeAttribute("readonly");
}