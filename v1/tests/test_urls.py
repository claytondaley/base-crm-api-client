__author__ = 'Clayton Daley'


"""
#######################
# Call Functions
#
# NOT YET IMPLEMENTED

https://app.futuresimple.com/apis/voice/api/v1/voice_preferences.json
https://app.futuresimple.com/apis/voice/api/v1/call_lists.json
https://app.futuresimple.com/apis/voice/api/v1/call_outcomes.json
https://app.futuresimple.com/apis/voice/api/v1/call_scripts.json
"""

"""
##########################
# Contact Functions and Constants

https://app.futuresimple.com/apis/crm/api/v1/contacts/40905764.json
# Multiple ID
https://app.futuresimple.com/apis/crm/api/v1/contacts.json?contact_ids=40905835%2C40905820&per_page=100
# contact_id is parent
https://app.futuresimple.com/apis/crm/api/v1/contacts.json?contact_id=40905629&page=1&tags_exclusivity=and&crm_list=true&sort_by=calls_to_action%2Cfirst&using_search=false

# NOT YET IMPLEMENTED

Count
https://app.futuresimple.com/apis/crm/api/v1/contacts/count.json?page=1&tags_exclusivity=and&crm_list=true&sort_by=calls_to_action%2Cfirst&using_search=false

Related Parameters
https://app.futuresimple.com/apis/crm/api/v1/custom_fields/cities
https://app.futuresimple.com/apis/crm/api/v1/custom_fields/regions
https://app.futuresimple.com/apis/crm/api/v1/custom_fields/countries
https://app.futuresimple.com/apis/crm/api/v1/custom_fields/zip_codes
https://app.futuresimple.com/apis/crm/api/v1/custom_fields.json?filterable=true
https://app.futuresimple.com/apis/crm/api/v1/custom_fields.json?sortable=true
https://app.futuresimple.com/apis/crm/api/v1/custom_field_values/grouped.json

https://app.futuresimple.com/apis/common/api/v1/feed/account_contacts_privacy.json
"""

"""
################
# DealContacts

# For contacts attached to a deal
https://app.futuresimple.com/apis/sales/api/v1/deals/1276628/contacts.json

"""


"""
##########################
# Deals Functions and Constants

https://app.futuresimple.com/apis/sales/api/v1/deals/by_ids.json?deal_ids=2049413%2C1283854%2C1283853%2C1283851&per_page=4
https://app.futuresimple.com/apis/sales/api/v1/deals.json?dont_scope_by_stage=true&deal_ids=1276628
https://app.futuresimple.com/apis/sales/api/v1/deals/top_deals.json
https://app.futuresimple.com/apis/sales/api/v2/deals/total_pipeline_worth

https://app.futuresimple.com/apis/sales/api/v2/contacts/deals.json?contact_ids=40905809

NOT YET IMPLEMENTED

Related Parameters
https://app.futuresimple.com/apis/sales/api/v1/stages.json?detailed=true

https://app.futuresimple.com/apis/sales/api/v1/loss_reasons.json

https://app.futuresimple.com/apis/sales/api/v1/deal_custom_fields.json
https://app.futuresimple.com/apis/sales/api/v1/deal_custom_fields.json?sortable=true
https://app.futuresimple.com/apis/sales/api/v1/custom_field_values/grouped.json

https://app.futuresimple.com/apis/sales/api/v2/deals/currencies.json

https://app.futuresimple.com/apis/uploader/api/v2/attachments.json?attachable_type=DocumentRepository&attachable_id=null
"""

"""
##########################
# Email Functions
#
# NOT YET IMPLEMENTED

V1
https://app.futuresimple.com/apis/mailman/api/v1/email_profile.json
https://app.futuresimple.com/apis/mailman/api/v1/email_profiles/check.json

V2
https://app.futuresimple.com/apis/mailman/api/v2/email_profile.json
https://app.futuresimple.com/apis/mailman/api/v2/email_profile.json?postpone=true

Inbox
https://app.futuresimple.com/apis/mailman/api/v2/synced_emails.json?mailbox=inbox&page=1&fields=items%2Ctotal_count&content=none

Sent
https://app.futuresimple.com/apis/mailman/api/v2/synced_emails.json?mailbox=outbox&page=1&fields=items%2Ctotal_count&content=none

Archived
https://app.futuresimple.com/apis/mailman/api/v2/synced_emails.json?mailbox=archived&page=1&fields=items%2Ctotal_count&content=none

Untracked
https://app.futuresimple.com/apis/mailman/api/v1/synced_emails/other.json?page=1
"""

"""
##########################
# Feed (i.e. Activity) Functions
#
# NOTE: feeds overlap to some degree with tasks (completed only) and notes

REAL CALLS THIS FUNCTION SHOULD SIMULATE

https://app.futuresimple.com/apis/feeder/api/v1/feed/contact/40905809.json?timestamp=null&api_mailman=v2
https://app.futuresimple.com/apis/feeder/api/v1/feed/contact/40905809.json?timestamp=null&api_mailman=v2&only=Email
https://app.futuresimple.com/apis/feeder/api/v1/feed/contact/40905809.json?timestamp=null&api_mailman=v2&only=Note
https://app.futuresimple.com/apis/feeder/api/v1/feed/contact/40905809.json?timestamp=null&api_mailman=v2&only=Call
https://app.futuresimple.com/apis/feeder/api/v1/feed/contact/40905809.json?timestamp=null&api_mailman=v2&only=Task

https://app.futuresimple.com/apis/feeder/api/v1/feed/lead/7787301.json?page=1&api_mailman=v2
https://app.futuresimple.com/apis/feeder/api/v1/feed/lead/7787301.json?only=Note&page=1&api_mailman=v2
https://app.futuresimple.com/apis/feeder/api/v1/feed/lead/7787301.json?only=Email&page=1&api_mailman=v2
https://app.futuresimple.com/apis/feeder/api/v1/feed/lead/7787301.json?only=Call&page=1&api_mailman=v2
https://app.futuresimple.com/apis/feeder/api/v1/feed/lead/7787301.json?only=Task&page=1&api_mailman=v2

https://app.futuresimple.com/apis/feeder/api/v1/feed/deal/1290465.json?timestamp=null&api_mailman=v2
https://app.futuresimple.com/apis/feeder/api/v1/feed/deal/1290465.json?timestamp=null&api_mailman=v2&only=Email
https://app.futuresimple.com/apis/feeder/api/v1/feed/deal/1290465.json?timestamp=null&api_mailman=v2&only=Note
https://app.futuresimple.com/apis/feeder/api/v1/feed/deal/1290465.json?timestamp=null&api_mailman=v2&only=Call
https://app.futuresimple.com/apis/feeder/api/v1/feed/deal/1290465.json?timestamp=null&api_mailman=v2&only=Task

PAGING (spaces introduced to emphasize minor differences between URLs)
https://app.futuresimple.com/apis/feeder/api/v1/feed.json?&timestamp=eyJsYXN0X2NvbnRhY3RfaWQiOjQx NTE 3MjAx LCJsYXN0X25vdGVfaWQiOj EwNjE 0MzE zLCJsYXN0X2xlYWRfaWQiOjc3ODczMDEsImxhc3RfZGVhbF9zdGFnZV9jaGFuZ2VfaWQiOjc3MTY2NSwibGFzdF9kZWFsX2lkIjoxMjc2NjQ3fQ
https://app.futuresimple.com/apis/feeder/api/v1/feed.json?&timestamp=eyJsYXN0X2NvbnRhY3RfaWQiOjQw OTA 3NTg1 LCJsYXN0X25vdGVfaWQiOj YzNDM yNDE sImxhc3RfbGVhZF9pZCI6Nzc4NzMwMSwibGFzdF9kZWFsX3N0YWdlX2NoYW5nZV9pZCI6NzcxNjY1LCJsYXN0X2RlYWxfaWQiOjEyNzY2Mjh9
https://app.futuresimple.com/apis/feeder/api/v1/feed.json?&timestamp=eyJsYXN0X2NvbnRhY3RfaWQiOjQw OTA 1NzY1 LCJsYXN0X25vdGVfaWQiOj YzNDM wOTk sImxhc3RfbGVhZF9pZCI6Nzc4NzMwMSwibGFzdF9kZWFsX3N0YWdlX2NoYW5nZV9pZCI6NzcxNjY1LCJsYXN0X2RlYWxfaWQiOjEyNzY2Mjh9
https://app.futuresimple.com/apis/feeder/api/v1/feed.json?&timestamp=eyJsYXN0X2NvbnRhY3RfaWQiOjQw OTA 1NzY0 LCJsYXN0X25vdGVfaWQiOj YzNDM wOTk sImxhc3RfbGVhZF9pZCI6Nzc4NzMwMSwibGFzdF9kZWFsX3N0YWdlX2NoYW5nZV9pZCI6NzcxNjY1LCJsYXN0X2RlYWxfaWQiOjEyNzY2Mjh9
https://app.futuresimple.com/apis/feeder/api/v1/feed.json?&timestamp=eyJsYXN0X2NvbnRhY3RfaWQiOjQw OTA 1NjI5 LCJsYXN0X25vdGVfaWQiOj YzNDM wOTk sImxhc3RfbGVhZF9pZCI6Nzc4NzMwMSwibGFzdF9kZWFsX3N0YWdlX2NoYW5nZV9pZCI6NzcxNjY1LCJsYXN0X2RlYWxfaWQiOjEyNzY2Mjh9
"""

"""
##########################
# Miscellaneous Functions
#
# NOT YET IMPLEMENTED

https://app.futuresimple.com/apis/core/api/v2/startup.json
https://app.futuresimple.com/apis/sales/api/v1/dashboard.json
https://app.futuresimple.com/apis/core/api/v1/public/currencies.json
https://app.futuresimple.com/apis/feeder/api/v1/feed.json?&timestamp=null
https://app.futuresimple.com/apis/voice/api/v1/voice_preferences.json
https://app.futuresimple.com/apis/sales/api/v1/integrations_status.json
https://app.futuresimple.com/apis/crm/api/v1/mailchimp/status.json
https://app.futuresimple.com/apis/uploader/api/v2/attachments.json?attachable_type=Deal&attachable_id=2255196
"""


"""
##########################
# Tags Functions

https://app.futuresimple.com/apis/tags/api/v1/taggings.json
    POST = app_id=4&taggable_type=Contact&tag_list=from+google&taggable_id=40905764 # note singular id
https://app.futuresimple.com/apis/tags/api/v1/taggings/batch_untag.json
    POST = app_id=4&taggable_type=Contact&tag_list=from+google&taggable_ids=40905764 # note plural ids
https://app.futuresimple.com/apis/tags/api/v1/taggings/batch_add.json
    POST = app_id=4&taggable_type=Contact&tag_list=from+google&taggable_ids=40905764 # note plural ids

https://app.futuresimple.com/apis/tags/api/v1/tags.json?app_id=1
https://app.futuresimple.com/apis/tags/api/v1/tags.json?app_id=4
https://app.futuresimple.com/apis/tags/api/v1/tags.json?app_id=5
https://app.futuresimple.com/apis/tags/api/v1/tags.json?app_id=7
"""

"""
##########################
# Tasks Functions
#
# NOTE: tasks overlap to some degree with feeds (completed only)

https://app.futuresimple.com/apis/common/api/v1/tasks.json?status=active&owner=309357
https://app.futuresimple.com/apis/common/api/v1/tasks.json?taskable_type=Lead&taskable_id=7787301&done=true
https://app.futuresimple.com/apis/common/api/v1/tasks.json?taskable_type=Contact&taskable_id=40905809&status=active&skip_pagination=true
https://app.futuresimple.com/apis/common/api/v1/tasks.json?taskable_type=Deal&taskable_id=1290465&status=active&skip_pagination=true

https://app.futuresimple.com/tasks/apis/common/api/v1/tasks?page=1&status=active
https://app.futuresimple.com/tasks/apis/common/api/v1/tasks?page=1&status=active&date=tomorrow
https://app.futuresimple.com/tasks/apis/common/api/v1/tasks?page=1&status=active&date=today
https://app.futuresimple.com/tasks/apis/common/api/v1/tasks?page=1&status=active&date=this_week
https://app.futuresimple.com/tasks/apis/common/api/v1/tasks?page=1&status=active&date=overdue
https://app.futuresimple.com/tasks/apis/common/api/v1/tasks?page=1&status=active&date=no_due_date

https://app.futuresimple.com/tasks/apis/common/api/v1/tasks?skip_pagination=true&owner=309360&send_time_from=2014-02-24T05%3A00%3A00.000Z&send_time_to=2014-04-07T05%3A00%3A00.000Z
https://app.futuresimple.com/tasks/apis/common/api/v1/tasks?skip_pagination=true&owner=309360&send_time_from=2014-03-31T05%3A00%3A00.000Z&send_time_to=2014-05-05T05%3A00%3A00.000Z
NOTE: send_time_from and send_time_to MUST BOTH BE PRESENT
"""

"""
##########################
# Sources Functions

https://app.futuresimple.com/apis/sales/api/v1/sources.json?all=true
https://app.futuresimple.com/apis/sales/api/v1/sources.json?other=true
https://app.futuresimple.com/apis/sales/api/v1/sources.json?auto=true
"""

"""
##########################
# Lead Functions and Constants

https://app.futuresimple.com/apis/leads/api/v1/leads.json?ids=7787301&per_page=1
https://app.futuresimple.com/apis/leads/api/v1/leads.json?sort_by=last_name&sort_order=asc&tags_exclusivity=and&without_unqualified=true&using_search=false&page=0&converting=false

https://app.futuresimple.com/apis/leads/api/v1/leads/search.json?sort_by=last_name&sort_order=asc&tags_exclusivity=and&without_unqualified=true

# NOT YET IMPLEMENTED

Related Parameters
https://app.futuresimple.com/apis/leads/api/v1/statuses.json

https://app.futuresimple.com/apis/leads/api/v1/custom_fields.json?sortable=true
https://app.futuresimple.com/apis/leads/api/v1/custom_fields/filterable.json
"""