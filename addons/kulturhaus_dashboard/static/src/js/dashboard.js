/** @odoo-module **/

import { Component, useState, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { rpc } from "@web/core/network/rpc";

class KulturhausDashboard extends Component {
    static template = "kulturhaus_dashboard.Dashboard";
    
    setup() {
        this.action = useService("action");
        this.notification = useService("notification");
        
        this.state = useState({
            loading: true,
            kpis: {},
            sections: [],
            theme: 'blue',
            layout: 'grid',
            show_kpis: true
        });
        
        onWillStart(async () => {
            await this.loadDashboard();
        });
    }
    
    async loadDashboard() {
        try {
            this.state.loading = true;
            
            const response = await rpc('/dashboard/data', {});
            
            this.state.kpis = response.kpis || {};
            this.state.sections = response.cards || [];
            this.state.theme = response.theme || 'blue';
            this.state.layout = response.layout || 'grid';
            this.state.show_kpis = response.show_kpis !== false;
            this.state.loading = false;
        } catch (error) {
            console.error('Dashboard load error:', error);
            this.notification.add('Failed to load dashboard', {
                type: 'danger'
            });
            this.state.loading = false;
        }
    }
    
    get orderedSections() {
        return this.state.sections || [];
    }
    
    handleCardClick(card) {
        try {
            if (card.action && typeof card.action === 'object') {
                this.action.doAction(card.action);
            } else if (typeof card.action === 'number') {
                this.action.doAction(card.action);
            }
        } catch (error) {
            console.error('Card navigation error:', error);
            this.notification.add('Navigation failed', {
                type: 'danger'
            });
        }
    }
    
    openWebsite() {
        window.open('https://kulturhaus-bortfeld.de', '_blank');
    }
}

registry.category("actions").add("kulturhaus_dashboard", KulturhausDashboard);