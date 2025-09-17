/** @odoo-module **/

import { Store } from "@mail/core/common/store_service";
import { rpc } from "@web/core/network/rpc";
import { patch } from "@web/core/utils/patch";
import { prettifyMessageContent } from "@mail/utils/common/format";

const threadServicePatch = {
  async getMessagePostParams(params){
     const { attachments, cannedResponseIds, isNote, mentionedChannels, mentionedPartners } =
            params['postData'];
        const subtype = isNote ? "mail.mt_note" : "mail.mt_comment";
        const validMentions = this.getMentionsFromText(params['body'], {
            mentionedChannels,
            mentionedPartners,
        });
      const body_content = await prettifyMessageContent(params['body'], validMentions)
     if (body_content.includes('data-oe-model="discuss.channel"')) {
        let splitText = body_content.split(' ')
        let channels = []
        for (let i = 0; i < splitText.length; i++) {
            if (splitText[i].includes('discuss.channel/')) {
                let channelIdIndex = splitText[i].indexOf('discuss.channel/');

                if (channelIdIndex !== -1) {
                    // Extract the id value by slicing the string starting after 'id=' and until the next '&' or end of string
                    let channelId = splitText[i].substring(channelIdIndex + 16).split(' ')[0];
                    channelId = channelId.replace('"', '')
                    channels.push(parseInt(channelId));
                }
            }

        }    
        let parameters = {
            'channels': channels,
            'body': body_content,  
            'model': params['thread'].model,
            'record': params['thread'].id   
        }
          const channelData = rpc("/mail/get_channels", parameters);
    }
      return super.getMessagePostParams(params);
  }
}

patch(Store.prototype, threadServicePatch);
