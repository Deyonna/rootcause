document.addEventListener('DOMContentLoaded', () => {
    const premiumCheckbox = document.getElementById('id_is_premium');
    const coinCostWrapper = document.getElementById('coin-cost-wrapper');
    const coinCostInput = document.getElementById('id_coin_cost');
    if (!premiumCheckbox || !coinCostWrapper || !coinCostInput) return;

    function sync() {
        const isPremium = premiumCheckbox.checked;
        coinCostWrapper.style.display = isPremium ? '' : 'none';
        if (!isPremium) {
            coinCostInput.value = 0;
        }
    }

    premiumCheckbox.addEventListener('change', sync);
    sync();
});
