/** @odoo-module **/
import { Thread } from "@mail/core/common/thread_model";
import { patch } from "@web/core/utils/patch";

const threadServicePatch = {
   get importantCounter() {
        if (this.model === "mailbox") {
            return this.selfMember?.message_unread_counter;
        }
        if (this.isChatChannel) {
            return this.selfMember?.message_unread_counter ;
        }

        return this.selfMember?.message_unread_counter;
    }
}


patch(Thread.prototype, threadServicePatch);
