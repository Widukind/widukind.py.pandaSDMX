DB.nomics connector for Python using pandaSDMX
==============================================


This package gives the possibility of downloading DB.nomics series in Python using pandaSDMX.

**`DB.nomics <https://db.nomics.world/>`_ is a database of international macroeconomic data collected on public web servers of statistical offices worldwide.**

*Please ask your questions to the `DB.nomics forum <https://forum.db.nomics.world/>`_.*

**For a more complete documentation, refer to the original documentation:** http://pandasdmx.readthedocs.org/

Installation
------------

::

    $ pip install https://github.com/dr-leo/pandasdmx/tarball/master

    $ pip install git+https://git.nomics.world/dbnomics/dbnomics-connector-pandasdmx.py.git


Basic Example
-------------

::

    >>> from widukind_sdmx import Request

    # DB.nomics Agencies: ECB, INSEE, EUROSTAT, BIS, IMF, OECD, ESRI, FED
    >>> sdmx = Request(agency='INSEE')

    >>> data_response = sdmx.get(resource_type='data', resource_id="IPCH-2015-FR-COICOP", key={'FREQ': 'A', 'PRODUIT': '00', 'NATURE': 'INDICE'})

    # Render to pandas.core.frame.DataFrame

    >>> cur_df = data_response.write()

    >>> cur_df.shape
    (20, 1)

    >>> cur_df.tail()
    NATURE       INDICE
    FREQ              A
    PRODUIT          00
    TIME_PERIOD
    2011          96.20
    2012          98.33
    2013          99.31
    2014          99.91
    2015         100.00

    # Render to Python

    >>> from pprint import pprint

    >>> data = list(data_response.msg.data.series)
    >>> obs = list(data[0].obs())
    >>> for o in obs: print(o.dim, o.value)
    ...
    1996 74.9
    1997 75.9
    1998 76.4
    1999 76.8
    2000 78.2
    2001 79.6
    2002 81.2
    2003 82.9
    2004 84.9
    2005 86.5
    2006 88.1
    2007 89.51
    2008 92.34
    2009 92.44
    2010 94.04
    2011 96.2
    2012 98.33
    2013 99.31
    2014 99.91
    2015 100

    >>> pprint(dict(data[0].key._asdict()))
    {'FREQ': 'A', 'NATURE': 'INDICE', 'PRODUIT': '00'}

    >>> pprint(dict(data[0].attrib._asdict()))
    {'BASE-PER': '2015',
     'DECIMALS': '2',
     'IDBANK': '001762489',
     'LAST-UPDATE': '2016-02-18',
     'REF-AREA': 'FE',
     'TIME-PER-COLLECT': 'PERIODE',
     'TITLE': 'IPCH-ANNUEL-ENSEMBLE-DES-MENAGES-FRANCE-BASE-2015-NOMENCLATURE-COICOP-ENSEMBLE-HARMONISE',
     'UNIT-MEASURE': 'SO',
     'UNIT-MULT': '0',
     'WIDUKIND_ID': '001762489',
     'WIDUKIND_NAME': 'Annual - 00 - All items - Index'}

Structure
---------

::

    >>> from collections import OrderedDict
    >>> from widukind_sdmx import Request

    >>> sdmx = Request(agency='INSEE')

    >>> dataflows_response = sdmx.get(resource_type='dataflow')
    >>> dataflows = dataflows_response.msg.dataflows

    >>> datastructure_response = sdmx.get(resource_type='datastructure', resource_id="IPCH-2015-FR-COICOP")
    >>> dsd = datastructure_response.msg.datastructures["IPCH-2015-FR-COICOP"]
    >>> dimensions = OrderedDict([(dim.id, dim) for dim in dsd.dimensions.aslist() if dim.id not in ['TIME_PERIOD']])

Debug
-----

::

    >>> from widukind_sdmx import Request
    >>> sdmx = Request(agency='INSEE')

    >>> dataflows_response = sdmx.get(resource_type='dataflow')

    >>> print(dataflows_response.url)
    https://db.nomics.world/api/v1/sdmx/dataflow/INSEE

    >>> print(dataflows_response.status_code)
    200

Config (optional)
-----------------

::

    # DB.nomics Production (default)
    $ export WIDUKIND_API_URL=https://api.db.nomics.world/api/v1/sdmx

    # DB.nomics local
    $ export WIDUKIND_API_URL=http://127.0.0.1:8081/api/v1/sdmx

