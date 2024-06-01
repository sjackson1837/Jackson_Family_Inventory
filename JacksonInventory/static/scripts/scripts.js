function debounce(func, delay) {
    let debounceTimer;
    return function(...args) {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(() => func.apply(this, args), delay);
    };
  }
  
  function checkBarcodeDelayed(event) {
    debounce(() => {
      checkBarcode(event);
    }, 500)();
  }
  
  function checkBarcodeDelayedUseItem(event) {
    debounce(() => {
      checkBarcodeUseItem(event);
    }, 500)();
  }
  
  function checkBarcode(event) {
    const barcode = event.target.value;
  
    setTimeout(function() {
      const xhr = new XMLHttpRequest();
      xhr.open("POST", "/check_item", true);
      xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
      xhr.onreadystatechange = function() {
        if (xhr.readyState === 4) {
          if (xhr.status === 200) {
            const response = JSON.parse(xhr.responseText);
            handleBarcodeResponse(response, barcode);
          }
        }
      };
      xhr.send("barcode=" + barcode);
    }, 750);
  }
  
  function checkBarcodeUseItem(event) {
    const barcode = event.target.value;
  
    setTimeout(function() {
      const xhr = new XMLHttpRequest();
      xhr.open("POST", "/use_item", true);
      xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
      xhr.onreadystatechange = function() {
        if (xhr.readyState === 4) {
          if (xhr.status === 200) {
            const response = JSON.parse(xhr.responseText);
            handleBarcodeResponse(response, barcode);
          }
        }
      };
      xhr.send("barcode=" + barcode);
    }, 750);
  }
  
  
  function handleBarcodeResponse(response, barcode) {
    if (response.redirect_url) {
      document.getElementById("barcode").value = "";
      playSoundAndRedirect('static/sounds/positive.mp3', response.redirect_url);
    } else if (response.barcode_not_found) {
      checkItem(barcode);
    } else {
      flash("testing flash message");
    }
  }
  
  
  function useItem(event) {
    const barcode = event.target.value;
    const xhr = new XMLHttpRequest();
    xhr.open("POST", "/use_item", true);
    xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhr.onreadystatechange = function() {
      if (xhr.readyState === 4 && xhr.status === 200) {
        const response = JSON.parse(xhr.responseText);
        handleUseItemResponse(response, event, barcode);
      }
    };
    xhr.send("barcode=" + barcode);
  }
  
  function handleUseItemResponse(response, event, barcode) {
    if (response.redirect_url) {
      playSoundAndRedirect('static/sounds/positive.mp3', response.redirect_url);
    } else if (response.barcode_not_found) {
      playSound('static/sounds/negative.mp3');
      alert("Item not found in inventory");
      event.target.value = "";
    }
  }
  
  function playSoundAndRedirect(soundSrc, redirectUrl) {
    const audio = new Audio(soundSrc);
    audio.onended = function() {
      window.location.href = redirectUrl;
    };
    audio.play();
  }
  
  function playSound(soundSrc) {
    const audio = new Audio(soundSrc);
    audio.play();
  }
  
  function checkItem(barcode) {
    const url = `https://world.openfoodfacts.org/api/v0/product/${barcode}.json`;
  
    fetch(url)
      .then(response => response.json())
      .then(data => {
        if (data.status === 0) {
          populateProductFormForNewProduct(barcode);
        } else {
          populateProductForm(data.product, barcode);
        }
      })
      .catch(error => console.error(error));
  }
  
  function populateProductFormForNewProduct(barcode) {
    const defaultImageUrl = "https://st4.depositphotos.com/14953852/22772/v/450/depositphotos_227725020-stock-illustration-image-available-icon-flat-vector.jpg";
    document.getElementById("barcode").readOnly = true;
    document.getElementById("barcode").value = barcode;
    document.getElementById("productname").readOnly = false;
    document.getElementById("qty").readOnly = false;
    document.getElementById("qty").value = 1;
    document.getElementById("minqty").value = 1;
    document.getElementById("productimage_input").readOnly = false;
    document.getElementById("productimage_input").value = defaultImageUrl;
    document.getElementById("productimage_show").src = defaultImageUrl;
  
    showProductData();
    playSound('static/sounds/negative.mp3');
  }
  
  function populateProductForm(product, barcode) {
    const imageUrl = product.image_url || "https://st4.depositphotos.com/14953852/22772/v/450/depositphotos_227725020-stock-illustration-image-available-icon-flat-vector.jpg";
    document.getElementById("barcode").readOnly = true;
    document.getElementById("productname").readOnly = true;
    document.getElementById("productimage_input").readOnly = true;
    document.getElementById("barcode").value = barcode;
    document.getElementById("productname").value = product.product_name;
    document.getElementById("qty").value = 1;
    document.getElementById("minqty").value = 1;
    document.getElementById("productimage_input").value = imageUrl;
    document.getElementById("productimage_show").src = imageUrl;
  
    showProductData();
    playSound('static/sounds/positive.mp3');
  }
  
  function showProductData() {
    document.getElementById('barcodeContainer').style.display = 'block';
    document.getElementById('productDataContainer').style.display = 'block';
    document.getElementById('productimage_show').style.display = 'block';
  }
  
  function incrementQty() {
    const qtyInput = document.getElementById('qty');
    let qtyValue = parseInt(qtyInput.value) || 0;
    qtyInput.value = qtyValue + 1;
  }
  
  function decrementQty() {
    const qtyInput = document.getElementById('qty');
    let qtyValue = parseInt(qtyInput.value) || 0;
    qtyInput.value = Math.max(0, qtyValue - 1);
  }
  
  function incrementMinQty() {
    const qtyInput = document.getElementById('minqty');
    let qtyValue = parseInt(qtyInput.value) || 0;
    qtyInput.value = qtyValue + 1;
  }
  
  function decrementMinQty() {
    const qtyInput = document.getElementById('minqty');
    let qtyValue = parseInt(qtyInput.value) || 0;
    qtyInput.value = Math.max(0, qtyValue - 1);
  }
  
  function enableProductNameEditing() {
    document.getElementById("productname").removeAttribute("readonly");
  }
  
  function reloadPage() {
    location.reload();
  }
  
  function setFocusToBarcodeInput() {
    const barcodeInput = document.getElementById("barcode");
    barcodeInput.focus();
    barcodeInput.click();
    barcodeInput.focus();
  }
  
  window.onload = setFocusToBarcodeInput;
  
  function updateSubcategories() {
    const category_id = document.getElementById('category').value;
    const subcategoryDropdown = document.getElementById('subcategory');
  
    subcategoryDropdown.innerHTML = '';
    const defaultOption = document.createElement('option');
    defaultOption.value = '';
    defaultOption.textContent = '-- Select Subcategory --';
    subcategoryDropdown.appendChild(defaultOption);
  
    if (category_id !== '') {
      $.ajax({
        url: '/subcategories',
        method: 'POST',
        data: { category_id },
        success: function(response) {
          response.subcategories.forEach(subcategory => {
            const option = document.createElement('option');
            option.value = subcategory.id;
            option.textContent = subcategory.name;
            subcategoryDropdown.appendChild(option);
          });
        },
        error: function(xhr, status, error) {
          console.error(error);
        }
      });
    }
  }
  
  function changeImageSrc() {
    const productImage = document.getElementById("productimage_show");
    const productImageInput = document.getElementById("productimage_input");
  
    const defaultImageUrl = "https://st4.depositphotos.com/14953852/22772/v/450/depositphotos_227725020-stock-illustration-image-available-icon-flat-vector.jpg";
    productImage.src = defaultImageUrl;
    productImageInput.value = defaultImageUrl;
  
    return false;
  }