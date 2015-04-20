Introduction
============

The Python client for BaseCRM reflects a somewhat odd heritage:

 - There is no official Python client (they're a Ruby shop so no surprise).
 - The [original BaseCRM API Client (for Python)](http://github.com/npinger/base-crm-api-client) focused on replicating the [Base API Documentation](http://dev.futuresimple.com/api/overview).
     - An enhanced version of this branch (formerly OfficialSupport) can be found under the "official-1.x" branch.
 - By early 2014, it became clear that FutureSimple was not regularly updating their API documents.  To bring the API up to parity with the web application, @claytondaley reviewed the messages exchanged by the BaseCRM web interface and expanded the API client to take advantage of many of these capabilities.
     - In related communications, FutureSimple made it clear that much of this functionality was not set in stone.
     - Users who wish to continue to use this client will find it in the master-1.x branch, but the API is deprecated
     - @claytondaley also experimented with (stateful) access to the feed in a "stateful" branch
 - In early 2015, FutureSimple announced an updated (v2) API that integrated many of these features into the official API documentation.
     - Due to substantial improvements in the master-1.x branch, v2 support will be built off this branch.
     - We've also heard that FutureSimple is releasing a [Sync](https://developers.getbase.com/docs/rest/articles/sync) and WebHooks option that may be added to this client.

I'm taking advantage of the v2 rewrite to convert the BaseCRM API to a more object-oriented pattern.  If you prefer to stick with the procedural approach, feel free to use (and update) the 1.x branch.

Some final notes:

 - Several forks include a pip-friendly setup and I would welcome a PR.
 - A new "official-2.x" is available if anyone wants to contribute PRs trimming the experimental v2 client down to official v2 API calls.
 - If you require (prefer?) an asynchronous client, [TxBaseCRM](https://github.com/claytondaley/TxBaseCRM) has been created to support an effort for Twisted. 

BaseCRM ORM
===========

The pattern of the low-level client (below) was selected to be as transparent as possible to the underlying API calls and timing.

Eventually, it'd be nice to provide a more ORM-like experience on top of this foundation.  Database ORMs are already a complex affair.  Unfortunately, building an ORM on top of a REST API introduces even more issues.
    
Only after some details about the v2 API are settled (especially concurrency and sync features) will it make sense to attempt this feature.

Low-Level API Client
====================

The BaseCRM Client includes a library of authentication objects.  To create a client, initialize one of these objects and provide it to BaseAPI's constructor:

    # Create an auth object 
    from basecrm.authentication import Password
    auth = Password(MY_USERNAME, MY_PASSWORD)
    
    # Build the client
    from basecrm.client import BaseAPI
    base = BaseAPI(auth)
    
The client also comes with a set of resources.  Resources are Python objects that contain internal descriptions of the constraints and business rules for a set of API endpoints:

    # An entity with a specific id
    from basecrm.v2.entities import Contact
    contact_1 = Contact(1)
    
    # A list of all Deals
    from basecrm.v2.entities import DealSet
    all_deals = DealSet()
    
    # A list of entities based on a certain filter
    # Valid kwargs can be found at Class.FILTERS
    all_organizations = basecrm.OrganizationSet()

These objects contain no magic so you must explicitly ask the API client to act on them when you want to exchange data with the servers:

    # Resources are updated based on the response the API
    base.get(contact_1)
    
    # Collections describe a set of Resources   
    page = base.get_page(all_organizations, page, per_page, order_by)

This makes the low-level API Client a very thin wrapper around the actual API calls.  The syntax is friendlier, but every API call is explicit.

Updates and deletes are similar:
    
    contact_1 = basecrm.Contact(1)
    base.get(contact_1)
    # Valid properties (keys) and types (values) are found at Class.PROPERTIES
    contact_1.name = 'Fred'
    base.save(contact_1)
    # and when you're done
    base.delete(contact_1)

Ongoing Development:
====================

 - [ ] Upgrade "master" to fully support the v2 API
 - [ ] A v2 branch trimmed down to official support
 - [ ] Tests
 - [ ] Error handling - There is presently no effort to catch and handle errors during the API call and only transient efforts to check types and values.

We welcome issue reports and PRs.