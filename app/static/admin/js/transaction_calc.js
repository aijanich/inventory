document.addEventListener("DOMContentLoaded", function () {
    const productField = document.querySelector("#id_product");
    const quantityField = document.querySelector("#id_quantity");
    const priceField = document.querySelector("#id_price");
    const totalField = document.querySelector("#id_total_amount");

    if (!productField || !priceField || !totalField) return;

    function parseNumber(value) {
        if (!value) return 0;
        const normalized = value.toString().replace(",", ".");
        const result = parseFloat(normalized);
        return Number.isNaN(result) ? 0 : result;
    }

    function updateTotal() {
        const priceRaw = priceField.value;
        const quantityRaw = quantityField ? quantityField.value : "";
        const price = parseNumber(priceRaw);
        const quantity = parseNumber(quantityRaw);
        if (priceRaw !== "" && quantityRaw !== "") {
            totalField.value = (price * quantity).toFixed(2);
        } else if (quantityRaw === "") {
            totalField.value = "";
        }
    }

    function updatePriceFromProduct() {
        const productId = productField.value;
        if (!productId) return;
        fetch(`/api/product-price/${productId}/`, { cache: "no-store" })
            .then(response => response.json())
            .then(data => {
                if (data && data.price !== undefined) {
                    priceField.value = data.price;
                    updateTotal();
                }
            });
    }

    productField.addEventListener("change", updatePriceFromProduct);
    if (quantityField) {
        quantityField.addEventListener("input", function () {
            updatePriceFromProduct();
            updateTotal();
        });
        quantityField.addEventListener("change", function () {
            updatePriceFromProduct();
            updateTotal();
        });
    }
    priceField.addEventListener("input", updateTotal);
    if (productField.value) {
        updatePriceFromProduct();
    }
});
