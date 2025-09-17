/** @odoo-module **/

// KULTURHAUS WORKING CHECKOUT SOLUTION
console.log("🛒 Kulturhaus Checkout: Loading...");

document.addEventListener("DOMContentLoaded", function() {
    function applyKulturhausFixes() {
        console.log("🛒 Kulturhaus Fix: Applying German instructions...");
        
        // Check if already added
        if (document.querySelector(".kulturhaus-checkout-help")) return;
        
        // Create German instructions with exact working code
        const helpDiv = document.createElement("div");
        helpDiv.className = "kulturhaus-checkout-help";
        helpDiv.style.cssText = `
            background: #e8f5e9 \!important;
            border: 2px solid #4caf50 \!important;
            border-radius: 8px \!important;
            padding: 20px \!important;
            margin: 20px 0 \!important;
            font-family: Arial, sans-serif \!important;
            color: #2e7d32 \!important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1) \!important;
            position: relative \!important;
            z-index: 1000 \!important;
        `;
        
        helpDiv.innerHTML = `
            <h3 style="margin: 0 0 15px 0 \!important; color: #1b5e20 \!important; font-size: 18px \!important;">
                🛒 Ihre Bestellung in 2 einfachen Schritten
            </h3>
            <div style="display: flex \!important; align-items: center \!important; margin: 10px 0 \!important;">
                <div style="background: #4caf50 \!important; color: white \!important; border-radius: 50% \!important; width: 24px \!important; height: 24px \!important; display: flex \!important; align-items: center \!important; justify-content: center \!important; font-weight: bold \!important; margin-right: 12px \!important; font-size: 12px \!important;">1</div>
                <div><strong>Adresse bestätigen</strong> (Sie sind hier ✓)</div>
            </div>
            <div style="display: flex \!important; align-items: center \!important; margin: 10px 0 \!important;">
                <div style="background: #81c784 \!important; color: white \!important; border-radius: 50% \!important; width: 24px \!important; height: 24px \!important; display: flex \!important; align-items: center \!important; justify-content: center \!important; font-weight: bold \!important; margin-right: 12px \!important; font-size: 12px \!important;">2</div>
                <div><strong>Zur Kasse gehen</strong></div>
            </div>
            <p style="margin: 12px 0 0 0 \!important; font-size: 14px \!important; font-weight: bold \!important; color: #1b5e20 \!important;">
                → Klicken Sie <em>"Confirm"</em> wenn Ihre Adresse korrect ist.
            </p>
        `;
        
        // Insert at the very beginning of main content
        const mainContent = document.querySelector(".oe_website_sale") || document.body;
        const firstChild = mainContent.firstElementChild;
        mainContent.insertBefore(helpDiv, firstChild);
        
        console.log("✅ German instructions added successfully\!");
    }
    
    // Run with multiple timing strategies
    applyKulturhausFixes();
    setTimeout(applyKulturhausFixes, 500);
    setTimeout(applyKulturhausFixes, 1500);
    
    console.log("🎉 Kulturhaus Checkout: Module loaded\!");
});
