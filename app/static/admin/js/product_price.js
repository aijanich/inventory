document.addEventListener("DOMContentLoaded", function () {

    const productField = document.querySelector("#id_product");
    const priceField = document.querySelector("#id_price");

    if (!productField) return;

    productField.addEventListener("change", function () {

        const productId = this.value;

        fetch(`/api/product-price/${productId}/`)
            .then(response => response.json())
            .then(data => {
                priceField.value = data.price;
            });

    });

});