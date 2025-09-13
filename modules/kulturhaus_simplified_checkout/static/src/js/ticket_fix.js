// Quick fix for disabled ticket registration button
document.addEventListener('DOMContentLoaded', function() {
    // Find the quantity selector and submit button
    const quantitySelect = document.querySelector('select[name^="nb_register"]');
    const submitButton = document.querySelector('button.a-submit');
    
    if (quantitySelect && submitButton) {
        function updateButtonState() {
            const quantity = parseInt(quantitySelect.value);
            if (quantity > 0) {
                submitButton.disabled = false;
                console.log('Enabled submit button - quantity:', quantity);
            } else {
                submitButton.disabled = true;
                console.log('Disabled submit button - quantity:', quantity);
            }
        }
        
        // Update button state on change
        quantitySelect.addEventListener('change', updateButtonState);
        
        // Initialize button state
        updateButtonState();
        
        console.log('Ticket button fix loaded');
    } else {
        console.log('Could not find quantity selector or submit button');
    }
});