/* Simple Kulturhaus Checkout Fixes */
document.addEventListener("DOMContentLoaded", function() {
    console.log("Kulturhaus Simple Checkout: Loading...");
    
    function addGermanInstructions() {
        const checkoutForms = document.querySelectorAll("form[action*=\"shop\"], .oe_website_sale form");
        
        checkoutForms.forEach(function(form) {
            if (form.querySelector(".checkout-help")) return;
            
            const helpDiv = document.createElement("div");
            helpDiv.className = "checkout-help";
            helpDiv.innerHTML = "<h4>🛒 Ihre Bestellung in 2 einfachen Schritten</h4><div class=\"step\"><div class=\"step-number\">1</div><div><strong>Adresse bestätigen</strong> (Sie sind hier)</div></div><div class=\"step\"><div class=\"step-number\">2</div><div><strong>Zur Kasse gehen</strong></div></div><p><em>Klicken Sie \"Weiter zur Zahlung\" wenn Ihre Adresse korrekt ist.</em></p>";
            
            form.insertBefore(helpDiv, form.firstChild);
        });
    }
    
    function replaceEnglishText() {
        const replacements = {
            "Your Address": "Ihre Adresse",
            "Save address": "Adresse speichern", 
            "Confirm": "Bestätigen",
            "Continue": "Weiter",
            "Proceed to Checkout": "Weiter zur Zahlung"
        };
        
        Object.keys(replacements).forEach(function(english) {
            const elements = document.querySelectorAll("*");
            elements.forEach(function(el) {
                if (el.children.length === 0 && el.textContent.trim() === english) {
                    el.textContent = replacements[english];
                }
            });
        });
    }
    
    addGermanInstructions();
    replaceEnglishText();
    
    setTimeout(function() {
        addGermanInstructions();
        replaceEnglishText();
    }, 1000);
    
    console.log("Kulturhaus Simple Checkout: Loaded successfully");
});
