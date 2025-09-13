/** @odoo-module **/

// German Checkout Autofill and Improvements
document.addEventListener("DOMContentLoaded", function() {
    console.log("Kulturhaus: German autofill loading...");
    
    // Set Germany as default country
    function setGermanyDefault() {
        const countrySelect = document.querySelector("select[name=\"country_id\"]");
        if (countrySelect) {
            const germanOption = Array.from(countrySelect.options).find(option => 
                option.text.includes("Deutschland") || option.text.includes("Germany")
            );
            if (germanOption) {
                germanOption.selected = true;
                countrySelect.dispatchEvent(new Event("change"));
                console.log("Germany set as default country");
            }
        }
    }
    
    // Auto-populate email and name from previous entries
    function autoPopulateFields() {
        const emailField = document.querySelector("input[name=\"email\"]");
        const nameField = document.querySelector("input[name=\"name\"]");
        
        if (emailField && \!emailField.value) {
            const savedEmail = localStorage.getItem("kulturhaus_email");
            if (savedEmail) {
                emailField.value = savedEmail;
                console.log("Email auto-populated");
            }
        }
        
        if (nameField && \!nameField.value) {
            const savedName = localStorage.getItem("kulturhaus_name");
            if (savedName) {
                nameField.value = savedName;
                console.log("Name auto-populated");
            }
        }
        
        // Save values for future use
        if (emailField) {
            emailField.addEventListener("blur", function() {
                if (this.value) localStorage.setItem("kulturhaus_email", this.value);
            });
        }
        
        if (nameField) {
            nameField.addEventListener("blur", function() {
                if (this.value) localStorage.setItem("kulturhaus_name", this.value);
            });
        }
    }
    
    // Translate remaining text
    function translateRemainingText() {
        // "Already have an account?"
        const accountText = document.querySelector("*");
        if (accountText) {
            document.querySelectorAll("*").forEach(function(el) {
                if (el.textContent && el.textContent.includes("Already have an account?")) {
                    el.textContent = el.textContent.replace("Already have an account?", "Sie haben bereits einen Account?");
                }
                if (el.textContent && el.textContent.includes("Back to cart")) {
                    el.textContent = el.textContent.replace("Back to cart", "zurueck");
                }
            });
        }
    }
    
    // Run all functions
    setGermanyDefault();
    autoPopulateFields();
    translateRemainingText();
    
    // Re-run after small delay for dynamic content
    setTimeout(function() {
        setGermanyDefault();
        autoPopulateFields();
        translateRemainingText();
    }, 1000);
    
    console.log("Kulturhaus: German autofill complete");
});
