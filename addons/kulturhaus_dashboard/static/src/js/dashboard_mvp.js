/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onWillStart, useRef, onMounted } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class KulturhausDashboardMVP extends Component {
    static template = "kulturhaus_dashboard.DashboardMVP";
    
    setup() {
        this.rpc = useService("rpc");
        this.notification = useService("notification");
        this.action = useService("action");
        
        this.state = useState({
            loading: true,
            data: {
                members: { active: 0, delta: 0, quarterly_churn: [] },
                sepa: { next_date: null, amount: 0, status: 'pending' },
                events: { next_event: '', event_date: null, tickets_sold: 0, capacity: 0, monthly_revenue: 0 },
                website: { quarterly_visitors: 0, change_percent: 0 },
                social: { instagram_followers: 0, engagement_rate: 0, last_post: null }
            },
            quickActionModal: false,
            quickActionType: null,
            quickActionMessage: ''
        });
        
        onWillStart(async () => {
            await this.loadDashboardData();
        });
        
        onMounted(() => {
            // Set up auto-refresh every 30 seconds
            this.refreshInterval = setInterval(() => {
                this.loadDashboardData();
            }, 30000);
            
            // Set up WebSocket for real-time updates (if available)
            this.setupWebSocket();
        });
    }
    
    async loadDashboardData() {
        try {
            const result = await this.rpc("/dashboard/data", {});
            if (result.success) {
                this.state.data = result.data;
                this.state.loading = false;
            }
        } catch (error) {
            console.error("Dashboard load error:", error);
            this.notification.add("Error loading dashboard data", {
                type: "danger"
            });
        }
    }
    
    async refreshWidget(widgetName) {
        try {
            const result = await this.rpc(`/dashboard/refresh/${widgetName}`, {});
            if (result.success) {
                this.state.data[widgetName] = result.data;
                this.notification.add(`${widgetName} refreshed`, {
                    type: "success"
                });
            }
        } catch (error) {
            console.error("Widget refresh error:", error);
        }
    }
    
    setupWebSocket() {
        // WebSocket setup for real-time updates
        // This would connect to Odoo's bus system
        try {
            // Placeholder for WebSocket implementation
            console.log("WebSocket setup for real-time updates");
        } catch (error) {
            console.error("WebSocket setup error:", error);
        }
    }
    
    formatCurrency(amount) {
        return new Intl.NumberFormat('de-DE', {
            style: 'currency',
            currency: 'EUR'
        }).format(amount);
    }
    
    formatDate(dateString) {
        if (!dateString) return '-';
        const date = new Date(dateString);
        return date.toLocaleDateString('de-DE', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric'
        });
    }
    
    formatDateTime(dateString) {
        if (!dateString) return '-';
        const date = new Date(dateString);
        return date.toLocaleDateString('de-DE', {
            weekday: 'short',
            day: '2-digit',
            month: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        });
    }
    
    getSepaStatusClass(status) {
        const classes = {
            'ready': 'text-success',
            'pending': 'text-warning',
            'issues': 'text-danger'
        };
        return classes[status] || 'text-muted';
    }
    
    getSepaStatusIcon(status) {
        const icons = {
            'ready': 'fa-check-circle',
            'pending': 'fa-clock',
            'issues': 'fa-exclamation-triangle'
        };
        return icons[status] || 'fa-question-circle';
    }
    
    getDeltaIcon(delta) {
        return delta > 0 ? 'fa-arrow-up text-success' : 
               delta < 0 ? 'fa-arrow-down text-danger' : 
               'fa-minus text-muted';
    }
    
    getTicketProgress() {
        const { tickets_sold, capacity } = this.state.data.events;
        if (!capacity) return 0;
        return Math.round((tickets_sold / capacity) * 100);
    }
    
    getTimeUntilEvent() {
        const eventDate = this.state.data.events.event_date;
        if (!eventDate) return '';
        
        const now = new Date();
        const event = new Date(eventDate);
        const days = Math.ceil((event - now) / (1000 * 60 * 60 * 24));
        
        if (days < 0) return 'Vergangen';
        if (days === 0) return 'Heute';
        if (days === 1) return 'Morgen';
        return `In ${days} Tagen`;
    }
    
    getTimeSincePost() {
        const lastPost = this.state.data.social.last_post;
        if (!lastPost) return 'Nie';
        
        const now = new Date();
        const post = new Date(lastPost);
        const hours = Math.floor((now - post) / (1000 * 60 * 60));
        
        if (hours < 1) return 'Gerade eben';
        if (hours < 24) return `Vor ${hours} Stunden`;
        const days = Math.floor(hours / 24);
        if (days === 1) return 'Gestern';
        return `Vor ${days} Tagen`;
    }
    
    showQuickAction(actionType) {
        this.state.quickActionModal = true;
        this.state.quickActionType = actionType;
        this.state.quickActionMessage = '';
    }
    
    closeQuickAction() {
        this.state.quickActionModal = false;
        this.state.quickActionType = null;
        this.state.quickActionMessage = '';
    }
    
    async sendQuickAction() {
        const { quickActionType, quickActionMessage } = this.state;
        
        if (!quickActionMessage) {
            this.notification.add("Bitte Nachricht eingeben", {
                type: "warning"
            });
            return;
        }
        
        try {
            const endpoint = quickActionType === 'instagram' ? 
                '/dashboard/quick-action/instagram' : 
                '/dashboard/quick-action/telegram';
                
            const result = await this.rpc(endpoint, {
                message: quickActionMessage
            });
            
            if (result.success) {
                this.notification.add(`Nachricht ${quickActionType === 'instagram' ? 'auf Instagram gepostet' : 'an Telegram gesendet'}`, {
                    type: "success"
                });
                this.closeQuickAction();
            } else {
                this.notification.add(result.error || "Fehler beim Senden", {
                    type: "danger"
                });
            }
        } catch (error) {
            console.error("Quick action error:", error);
            this.notification.add("Fehler beim Senden der Nachricht", {
                type: "danger"
            });
        }
    }
    
    openMemberList() {
        this.action.doAction({
            type: 'ir.actions.act_window',
            name: 'Mitglieder',
            res_model: 'res.partner',
            view_mode: 'list,form',
            domain: [['is_company', '=', false], ['sepa_mandate_active', '=', true]],
            target: 'current'
        });
    }
    
    openSepaModule() {
        this.action.doAction({
            type: 'ir.actions.act_window',
            name: 'SEPA Batches',
            res_model: 'kulturhaus.sepa.batch',
            view_mode: 'list,form',
            target: 'current'
        });
    }
    
    openEventList() {
        this.action.doAction({
            type: 'ir.actions.act_window',
            name: 'Veranstaltungen',
            res_model: 'event.event',
            view_mode: 'list,kanban,form,calendar',
            target: 'current'
        });
    }
    
    willUnmount() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }
    }
}

registry.category("actions").add("kulturhaus_dashboard_mvp", KulturhausDashboardMVP);