# RecordSearch Tools

This is a Python library for getting useful, machine-readable data out of RecordSearch, the National Archives of Australia's online database.

It's basically a series of screen scrapers and as such is inherently fragile -- changes to the web interface can easily break the code.

RecordSearch is a complex system and I've added bits and pieces to this code over many years. As a result it could do with a major clean-up.

But having said all that, it should work pretty well, and until the NAA provides an API it's really the only way to get data out of RecordSearch.

## Usage and examples

The easiest way to use this library is through the [RecordSearch section of the GLAM WorkBench](https://glam-workbench.github.io/recordsearch/). There you'll find many examples of the code in action that you can run in your browser as Jupyter notebooks. That includes a notebook [to harvest the results of a search](https://glam-workbench.github.io/recordsearch/#harvest-items-from-a-search-in-recordsearch) in RecordSearch.

If you wan to DIY, there are a series of clients you can import and use:

* RSItemClient -- information on an individual item (usually a file)
* RSSeriesClient -- information on an individual series (a collection of items)
* RSAgencyClient -- information on an individual agency (such as a government department)
* RSSearchClient -- get results for an item search
* RSSeriesSearchClient -- get results for a series search
* RSAgencySearchClient -- get results for an agency search

So to get information on an individual item identified with the barcode of 3445411:

```python
from client import RSItemClient

c = RSItemClient()
c.get_summary('3445411')
```

The results look something like:

```python
{'access_decision': {'date_str': u'12 Apr 2001',
                     'end_date': None,
                     'start_date': {'date': datetime.datetime(2001, 4, 12, 0, 0),
                                    'day': True,
                                    'month': True}},
 'access_reason': [],
 'access_status': u'Open',
 'contents_dates': {'date_str': u'1914 - 1920',
                    'end_date': {'date': datetime.datetime(1920, 1, 1, 0, 0),
                                 'day': False,
                                 'month': False},
                    'start_date': {'date': datetime.datetime(1914, 1, 1, 0, 0),
                                   'day': False,
                                   'month': False}},
 'control_symbol': u'WRAGGE C L E',
 'digitised_pages': 47,
 'digitised_status': True,
 'identifier': u'3445411',
 'location': u'Canberra',
 'series': u'B2455',
 'title': u'WRAGGE Clement Lionel Egerton : SERN 647 : POB Cheadle England : POE Enoggera QLD : NOK  (Father) WRAGGE Clement Lindley'}
```

There are examples of the series and agency results in the tests.

The search clients accept most of the parameters used in the RecordSearch advanced search pages. So to search for items that include the word 'wragge' in the title, are in series B6286, and are digitised, you'd:

```python
from client import RSSearchClient
c = RSSearchClient()
c.search(digitised=True, kw='wragge', series='B6286')
```

Note that this will only return the first page of results, but it's pretty easy to build a simple harvester to loop through the complete set of search results. For example, here's a [harvester I use for downloading complete series](https://github.com/wragge/recordsearch-series-harvests).
