Introduction
============

The Python client for BaseCRM reflects a somewhat odd heritage:

 - There is no official Python client (they're a Ruby shop so no surprise).
 - The [original BaseCRM API Client (for Python)](http://github.com/npinger/base-crm-api-client) focused on replicating the (soon to be deprecated) v1 [Base API Documentation](http://dev.futuresimple.com/api/overview).
     - An enhanced version of this branch (formerly OfficialSupport) can be found under the [official-1.x branch](https://github.com/claytondaley/basecrm-client/tree/official-1.x).
 - By early 2014, @claytondaley reviewed the messages exchanged by the BaseCRM web interface and expanded the client to access many of these capabilities.
     - In related communications, FutureSimple made it clear that much of this functionality was not set in stone.
     - Users who wish to continue to use this client will find it in the [master-1.x branch](https://github.com/claytondaley/basecrm-client/tree/master-1.x).
     - @claytondaley also experimented with (stateful) access to APIv1 Feeds in a [stateful-1.x branch](https://github.com/claytondaley/basecrm-client/tree/stateful-1.x)
 - In early 2015, FutureSimple announced an updated (v2) API with revised [documentation](https://developers.getbase.com/).
     - FutureSimple is also releasing a [Sync](https://developers.getbase.com/docs/rest/articles/sync) and WebHooks option that may be added to this client.

In early 2015 and as part of a complete rewrite of the API client, the master branch has been upgraded to APIv2 support:

 - The new codebase is object-oriented
 - The rewrite should be highly extensible
     - New objects inherit rich, default logic from base classes (Resource and Collection)
     - Additional business logic is added by customizing a few basic methods
 - The rewrite can support APIv1 objects
     - NOTE: there is an open [issue](https://github.com/claytondaley/basecrm-client/issues/10) related to authentication

Some final notes:

 - Several forks include a pip-friendly setup and I would welcome a PR.
 - If you require (prefer?) an asynchronous client, [TxBaseCRM](https://github.com/claytondaley/TxBaseCRM) has been created to support an effort for Twisted. 

BaseCRM ORM
===========

The pattern of the low-level client (below) was selected to be as transparent as possible to the underlying API calls and timing.

Eventually, the goal for the client is an ORM-like experience.  Unfortunately, database ORMs are already a complex affair and building an ORM on top of a REST API introduces even more issues.

No progress will be made in this direction until some details about the v2 API are settled (especially concurrency and sync features).

Low-Level API Client
====================

The BaseCRM Client includes a library of authentication objects.  To create a client, initialize one of these objects and provide it to BaseAPI's constructor:

    # Create an auth object 
    from basecrm.authentication import Password
    auth = Password(MY_USERNAME, MY_PASSWORD)
    
    # Build the client
    from basecrm.client import BaseAPI
    base = BaseAPI(auth)
    
NOTE: at present, the resulting client will only be able to connect to one API (v1 or v2) at a time.  There is an [open issue](https://github.com/claytondaley/basecrm-client/issues/10) to resolve this, but you can create two clients as a workaround.

The client also comes with pre-defined Resources.  Resources are Python objects that contain internal descriptions of the data structure and business rules for an API endpoints:

    ...
    from basecrm.v2.resource import Lead, Deal
    
    # An entity with a specific id
    lead_1 = Lead(1)
    
    # A new Deal
    new_deal = Deal()
    # Contact is a special case.  If you want to create a new Contact, create a Person or Organization instead so appropriate business rules are enforced.
    
Resources contain no magic so you must explicitly ask the API client to act on them when you want to exchange data with the servers:

    # Data inside Resources are updated after a successful API call
    base.get(contact_1)
    
    base.id
    
This makes the low-level API Client a very thin wrapper around the actual API calls.  The syntax is friendlier, but every API call is explicit.

Updates and deletes are similar:
    
    ...
    
    # Valid properties (keys) and types (values) are found at Class.PROPERTIES and enforced when you attempt to update the related attribute.
    lead_1.first_name = 'Fred'
    
    # Updates are committed to the server by calling save() and supplying the Resource
    base.save(lead_1)
    # Create() must be called instead if a Resource does not have an ID
    
    # Finally, a Resource with an ID (loaded or unloaded) can be submitted for deletion 
    base.delete(lead_1)

To list/search resources, the API Client provides Collections that store a set of filters for a particular object:

    # A list of all Deals
    from basecrm.v2.entities import DealSet
    all_deals = DealSet()
    
    # A list of entities based on a certain filter
    # Valid kwargs can be found at Class.FILTERS
    all_organizations = basecrm.OrganizationSet()

Unlike Resources, limits on the page size prevent us from loading all Collection data at once.  To make this explicit, data is not stored in the Collection, but is returned as a page: 

    # Collections describe a set of Resources   
    page = base.get_page(all_organizations, page, per_page, order_by)

Since Collections are read-only, they cannot be submitted to `create()`, `save()`, or `delete()`

Ongoing Development:
====================

 - [ ] Upgrade "master" to fully support the v2 API
 - [ ] A v2 branch trimmed down to official support
 - [ ] Tests
 - [ ] Error handling - There is presently no effort to catch and handle errors during the API call and only transient efforts to check types and values.

We welcome issue reports and PRs.