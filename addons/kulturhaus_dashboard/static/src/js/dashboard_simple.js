/** @odoo-module **/

import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

class KulturhausDashboardSimple extends Component {
    static template = xml`
        <div class="kulturhaus-dashboard-simple p-4">
            <h1 class="mb-4">
                <i class="fa fa-home me-2"/>Kulturhaus Dashboard
            </h1>
            
            <div class="row">
                <!-- Active Members -->
                <div class="col-md-4 mb-3">
                    <div class="card h-100" t-on-click="openMemberList">
                        <div class="card-header bg-primary text-white">
                            <i class="fa fa-users"/> Aktive Mitglieder
                        </div>
                        <div class="card-body text-center">
                            <h2 class="display-4">127</h2>
                            <span class="text-success">
                                <i class="fa fa-arrow-up"/> +3
                            </span>
                        </div>
                    </div>
                </div>
                
                <!-- SEPA Status -->
                <div class="col-md-4 mb-3">
                    <div class="card h-100" t-on-click="openSepaModule">
                        <div class="card-header bg-success text-white">
                            <i class="fa fa-euro"/> SEPA Status
                        </div>
                        <div class="card-body text-center">
                            <p class="mb-1">15.02.2025</p>
                            <h3>€3,175.00</h3>
                            <span class="badge bg-success">
                                <i class="fa fa-check"/> Bereit
                            </span>
                        </div>
                    </div>
                </div>
                
                <!-- Next Event -->
                <div class="col-md-4 mb-3">
                    <div class="card h-100" t-on-click="openEventList">
                        <div class="card-header bg-info text-white">
                            <i class="fa fa-calendar"/> Nächstes Event
                        </div>
                        <div class="card-body text-center">
                            <h5>Fasching Party</h5>
                            <p class="mb-1">Sa, 08.02 20:00</p>
                            <div class="progress">
                                <div class="progress-bar" style="width: 40%">
                                    45/120
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Quick Actions -->
            <div class="mt-4 text-center">
                <button class="btn btn-primary me-2" t-on-click="() => this.showMessage('Instagram')">
                    <i class="fa fa-camera"/> Post Instagram
                </button>
                <button class="btn btn-primary" t-on-click="() => this.showMessage('Telegram')">
                    <i class="fa fa-paper-plane"/> Send Telegram
                </button>
            </div>
        </div>
    `;
    
    setup() {
        this.action = useService("action");
        this.notification = useService("notification");
    }
    
    openMemberList() {
        this.action.doAction({
            type: 'ir.actions.act_window',
            name: 'Mitglieder',
            res_model: 'res.partner',
            view_mode: 'list,form',
            domain: [['is_company', '=', false]],
            target: 'current'
        });
    }
    
    openSepaModule() {
        // Navigate to SEPA module or show notification
        this.notification.add("SEPA Modul öffnen", {
            type: "info"
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
    
    showMessage(platform) {
        this.notification.add(`${platform} Aktion wird ausgeführt...`, {
            type: "success"
        });
    }
}

registry.category("actions").add("kulturhaus_dashboard_simple", KulturhausDashboardSimple);