/** @odoo-module **/

import { registry } from "@web/core/registry";
import { CharField } from "@web/views/fields/char/char_field";
import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";

export class CopyClipboardChar extends CharField {
    setup() {
        super.setup();
        this.notification = useService("notification");
    }

    onClickCopy() {
        const value = this.props.value || "";
        if (navigator.clipboard) {
            navigator.clipboard.writeText(value).then(() => {
                this.notification.add(_t("Copied to clipboard!"), {
                    type: "success",
                });
            }).catch(() => {
                this.notification.add(_t("Failed to copy to clipboard"), {
                    type: "danger",
                });
            });
        } else {
            // Fallback for older browsers
            const textArea = document.createElement("textarea");
            textArea.value = value;
            textArea.style.position = "fixed";
            textArea.style.opacity = "0";
            document.body.appendChild(textArea);
            textArea.focus();
            textArea.select();
            try {
                document.execCommand("copy");
                this.notification.add(_t("Copied to clipboard!"), {
                    type: "success",
                });
            } catch (err) {
                this.notification.add(_t("Failed to copy to clipboard"), {
                    type: "danger",
                });
            }
            document.body.removeChild(textArea);
        }
    }
}

CopyClipboardChar.template = "kulturhaus_calendar_subscription.CopyClipboardChar";

registry.category("fields").add("CopyClipboardChar", CopyClipboardChar);