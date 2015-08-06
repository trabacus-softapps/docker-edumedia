FROM softapps/docker-odoobase-upstream
MAINTAINER Arun T K <arun.kalikeri@xxxxxxxx.com>
ADD additional_addons/pentaho_reports /opt/odoo/additional_addons/pentaho_reports
ADD additional_addons/attachment_large_object /opt/odoo/additional_addons/attachment_large_object
ADD additional_addons/Edumedia_India /opt/odoo/additional_addons/Edumedia_India
ADD additional_addons/Edumedia /opt/odoo/additional_addons/Edumedia

RUN chown -R odoo:odoo /opt/odoo/additional_addons/
