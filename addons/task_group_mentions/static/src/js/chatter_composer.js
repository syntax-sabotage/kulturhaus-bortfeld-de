/** @odoo-module **/

import { Composer } from "@mail/core/common/composer";
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";

/**
 * Patch the Composer to add support for @all and @Vorstand mentions
 */
patch(Composer.prototype, {
    /**
     * Override onInputKeydown to detect @ followed by "all" or "vorstand"
     */
    onInputKeydown(ev) {
        const result = super.onInputKeydown(ev);
        
        // Check if user is typing after @
        const input = ev.target;
        const text = input.value || input.textContent;
        const cursorPos = input.selectionStart || 0;
        
        // Look for @ symbol before cursor
        const beforeCursor = text.substring(0, cursorPos);
        const lastAtIndex = beforeCursor.lastIndexOf('@');
        
        if (lastAtIndex !== -1) {
            const afterAt = beforeCursor.substring(lastAtIndex + 1).toLowerCase();
            
            // Check for our special keywords
            if (afterAt === 'all' || afterAt === 'vorstand') {
                // Add visual feedback
                this._highlightGroupMention(afterAt);
            }
        }
        
        return result;
    },
    
    /**
     * Add visual feedback for group mentions
     */
    _highlightGroupMention(mentionType) {
        // This is a placeholder for visual feedback
        // In a real implementation, you might want to show a tooltip or badge
        console.log(`Group mention detected: @${mentionType}`);
    },
    
    /**
     * Override the suggestion provider to include @all and @Vorstand
     */
    async computeSuggestions() {
        const suggestions = await super.computeSuggestions(...arguments);
        
        // Check if we're in a project.task context
        if (this.thread && this.thread.model === 'project.task') {
            // Get the current search term
            const searchTerm = this.currentSearchTerm || '';
            
            // Add our special mentions if they match the search
            const specialMentions = [];
            
            if ('all'.startsWith(searchTerm.toLowerCase())) {
                specialMentions.push({
                    id: 'mention_all',
                    name: 'all',
                    display_name: _t('All Followers'),
                    type: 'special_mention',
                    icon: 'fa-users',
                    description: _t('Notify all task followers'),
                });
            }
            
            if ('vorstand'.startsWith(searchTerm.toLowerCase())) {
                specialMentions.push({
                    id: 'mention_vorstand',
                    name: 'Vorstand',
                    display_name: _t('Board Members'),
                    type: 'special_mention',
                    icon: 'fa-user-tie',
                    description: _t('Notify all board members'),
                });
            }
            
            // Prepend special mentions to the suggestions
            if (specialMentions.length > 0) {
                return [...specialMentions, ...suggestions];
            }
        }
        
        return suggestions;
    },
    
    /**
     * Handle selection of special mentions
     */
    onSuggestionSelect(suggestion) {
        if (suggestion.type === 'special_mention') {
            // Insert the special mention
            const mentionText = `@${suggestion.name}`;
            
            // Get the current composer input
            const input = this.root.el.querySelector('.o_mail_composer_text_field');
            if (input) {
                const currentText = input.value || input.textContent || '';
                const lastAtIndex = currentText.lastIndexOf('@');
                
                if (lastAtIndex !== -1) {
                    // Replace from @ to current position with our mention
                    const beforeAt = currentText.substring(0, lastAtIndex);
                    const afterCursor = currentText.substring(input.selectionStart || currentText.length);
                    
                    // Set the new text
                    const newText = beforeAt + mentionText + ' ' + afterCursor;
                    if (input.value !== undefined) {
                        input.value = newText;
                    } else {
                        input.textContent = newText;
                    }
                    
                    // Move cursor after the mention
                    const newCursorPos = beforeAt.length + mentionText.length + 1;
                    input.setSelectionRange(newCursorPos, newCursorPos);
                }
            }
            
            // Show notification
            this.notification.add(
                _t(`"${mentionText}" will notify ${suggestion.display_name}`),
                { type: 'info' }
            );
            
            return;
        }
        
        // Default behavior for regular mentions
        return super.onSuggestionSelect(suggestion);
    }
});