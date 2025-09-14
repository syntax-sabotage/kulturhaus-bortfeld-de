FROM odoo:18.0

USER root

# Install additional Python packages
RUN pip3 install --break-system-packages \
    icalendar \
    python-telegram-bot \
    schwifty

USER odoo