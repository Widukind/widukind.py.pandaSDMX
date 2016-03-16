# -*- coding: utf-8 -*-

import logging
import os
from zipfile import ZipFile, is_zipfile
from time import sleep

from pandasdmx import remote
from pandasdmx.api import Request as BaseRequest
from pandasdmx.api import Response
from pandasdmx.utils import str_type

logger = logging.getLogger('pandasdmx.api')

WIDUKIND_API_URL = os.environ.get('WIDUKIND_API_URL', "http://widukind-api.cepremap.org/api/v1/sdmx")

WIDUKIND_RESOURCES = {
    'data': {
        'headers': {'Accept': 'application/vnd.sdmx.genericdata+xml;version=2.1'},
    },
}

class Request(BaseRequest):

    _agencies = {
        '': None,  # empty agency for convenience when fromfile is given.
        'ESTAT': {
            'name': 'Eurostat',
            'url': 'http://ec.europa.eu/eurostat/SDMX/diss-web/rest',
            'resources': {},
        },
        'ECB': {
            'name': 'European Central Bank',
            'url': WIDUKIND_API_URL,
            'resources': WIDUKIND_RESOURCES,
        },
        'SGR': {
            'name': 'SDMX Global Registry',
            'url': 'https://registry.sdmx.org/ws/rest',
            'resources': {},
        },
        'INSEE': {
            'name': 'National Institute of Statistics and Economic Studies',
            'url': WIDUKIND_API_URL,
            'resources': WIDUKIND_RESOURCES
        },
        'EUROSTAT': {
            'name': 'Eurostat',
            'url': WIDUKIND_API_URL,
            'resources': WIDUKIND_RESOURCES
        },
        'ESRI': {
            'name': 'Economic and Social Research Institute, Cabinet Office',
            'url': WIDUKIND_API_URL,
            'resources': WIDUKIND_RESOURCES
        },
        'FED': {
            'name': 'Federal Reserve',
            'url': WIDUKIND_API_URL,
            'resources': WIDUKIND_RESOURCES
        },
        'OECD': {
            'name': 'Organisation for Economic Co-operation and Development',
            'url': WIDUKIND_API_URL,
            'resources': WIDUKIND_RESOURCES
        },
        'IMF': {
            'name': 'International Monetary Fund',
            'url': WIDUKIND_API_URL,
            'resources': WIDUKIND_RESOURCES
        },
        'BIS': {
            'name': 'Bank for International Settlements',
            'url': WIDUKIND_API_URL,
            'resources': WIDUKIND_RESOURCES
        },
    }
    
    def get(self, resource_type='', resource_id='', agency='', key='',
            params=None, headers={},
            fromfile=None, tofile=None, url=None, get_footer_url=(30, 3),
            memcache=None, writer=None):
        '''get SDMX data or metadata and return it as a :class:`pandasdmx.api.Response` instance.

        While 'get' can load any SDMX file (also as zip-file) specified by 'fromfile',
        it can only construct URLs for the SDMX service set for this instance.
        Hence, you have to instantiate a :class:`pandasdmx.api.Request` instance for each data provider you want to access, or
        pass a pre-fabricated URL through the ``url`` parameter.

        Args:
            resource_type(str): the type of resource to be requested. Values must be
                one of the items in Request._resources such as 'data', 'dataflow', 'categoryscheme' etc.
                It is used for URL construction, not to read the received SDMX file.
                Hence, if `fromfile` is given, `resource_type` may be ''.
                Defaults to ''.
            resource_id(str): the id of the resource to be requested.
                It is used for URL construction. Defaults to ''.
            agency(str): ID of the agency providing the data or metadata.
                Used for URL construction only. It tells the SDMX web service
                which agency the requested information originates from. Note that
                an SDMX service may provide information from multiple data providers.
                may be '' if `fromfile` is given. Not to be confused
                with the agency ID passed to :meth:`__init__` which specifies
                the SDMX web service to be accessed.
            key(str, dict): select columns from a dataset by specifying dimension values.
                If type is str, it must conform to the SDMX REST API, i.e. dot-separated dimension values.
                If 'key' is of type 'dict', it must map dimension names to allowed dimension values. Two or more
                values can be separated by '+' as in the str form. The DSD will be downloaded 
                and the items are validated against it before downloading the dataset.  
            params(dict): defines the query part of the URL.
                The SDMX web service guidelines (www.sdmx.org) explain the meaning of
                permissible parameters. It can be used to restrict the
                time range of the data to be delivered (startperiod, endperiod), whether parents, siblings or descendants of the specified
                resource should be returned as well (e.g. references='parentsandsiblings'). Sensible defaults
                are set automatically
                depending on the values of other args such as `resource_type`.
                Defaults to {}.
            headers(dict): http headers. Given headers will overwrite instance-wide headers passed to the
                constructor. Defaults to None, i.e. use defaults 
                from agency configuration
            fromfile(str): path to the file to be loaded instead of
                accessing an SDMX web service. Defaults to None. If `fromfile` is
                given, args relating to URL construction will be ignored.
            tofile(str): file path to write the received SDMX file on the fly. This
                is useful if you want to load data offline using
                `fromfile` or if you want to open an SDMX file in
                an XML editor.
            url(str): URL of the resource to download.
                If given, any other arguments such as
                ``resource_type`` or ``resource_id`` are ignored. Default is None.
            get_footer_url((int, int)): 
                tuple of the form (seconds, number_of_attempts). Determines the
                behavior in case the received SDMX message has a footer where
                one of its lines is a valid URL. ``get_footer_url`` defines how many attempts should be made to
                request the resource at that URL after waiting so many seconds before each attempt.
                This behavior is useful when requesting large datasets from Eurostat. Other agencies do not seem to
                send such footers. Once an attempt to get the resource has been 
                successful, the original message containing the footer is dismissed and the dataset
                is returned. The ``tofile`` argument is propagated. Note that the written file may be
                a zip archive. pandaSDMX handles zip archives since version 0.2.1. Defaults to (30, 3).
            memcache(str): If given, return Response instance if already in self.cache(dict), 
            otherwise download resource and cache Response instance.             
        writer(str): optional custom writer class. 
            Should inherit from pandasdmx.writer.BaseWriter. Defaults to None, 
            i.e. one of the included writers is selected as appropriate. 

        Returns:
            pandasdmx.api.Response: instance containing the requested
                SDMX Message.

        '''
        # Try to get resource from memory cache if specified
        if memcache in self.cache:
            return self.cache[memcache]

        if url:
            base_url = url
        else:
            # Construct URL from args unless ``tofile`` is given
            # Validate args
            if params is None:
                params = {}
            if not agency:
                agency = self.agency
            # Validate resource if no filename is specified
            if not fromfile and resource_type not in self._resources:
                raise ValueError(
                    'resource must be one of {0}'.format(self._resources))
            # resource_id: if it is not a str or unicode type,
            # but, e.g., a invalid DataflowDefinition,
            # extract its ID
            if resource_id and not isinstance(resource_id, (str_type, str)):
                resource_id = resource_id.id

            # If key is a dict, validate items against the DSD
            # and construct the key string which becomes part of the URL
            # Otherwise, do nothing as key must be a str confirming to the REST
            # API spec.
            if resource_type == 'data' and isinstance(key, dict):
                key = self._make_key(resource_id, key)

            # Get http headers from agency config if not given by the caller
            if not (fromfile or headers):
                # Check for default headers
                resource_cfg = self._agencies[agency][
                    'resources'].get(resource_type)
                if resource_cfg:
                    headers = resource_cfg.get('headers') or {}
            # Construct URL from the given non-empty substrings.
            # if data is requested, omit the agency part. See the query
            # examples
            #if resource_type in ['data', 'categoryscheme']:
            #    agency = ''
            # Remove None's and '' first. Then join them to form the base URL.
            # Any parameters are appended by remote module.
            if self.agency:
                parts = [self._agencies[self.agency]['url'],
                         resource_type, agency, resource_id, key]
                base_url = '/'.join(filter(None, parts))

                # Set references to sensible defaults
                if 'references' not in params:
                    if resource_type in [
                            'dataflow', 'datastructure'] and resource_id:
                        params['references'] = 'all'
                    elif resource_type == 'categoryscheme':
                        params['references'] = 'parentsandsiblings'

            elif fromfile:
                base_url = ''
            else:
                raise ValueError(
                    'If `` url`` is not specified, either agency or fromfile must be given.')

        # Now get the SDMX message either via http or as local file
        logger.info(
            'Requesting resource from URL/file %s', (base_url or fromfile))
        source, url, resp_headers, status_code = self.client.get(
            base_url, params=params, headers=headers, fromfile=fromfile)
        logger.info(
            'Loaded file into memory from URL/file: %s', (url or fromfile))
        # write msg to file and unzip it as required, then parse it
        with source:
            if tofile:
                logger.info('Writing to file %s', tofile)
                with open(tofile, 'wb') as dest:
                    source.seek(0)
                    dest.write(source.read())
                    source.seek(0)
            # handle zip files
            if is_zipfile(source):
                temp = source
                with ZipFile(temp, mode='r') as zf:
                    info = zf.infolist()[0]
                    source = zf.open(info)
            else:
                # undo side effect of is_zipfile
                source.seek(0)
            msg = self._get_reader().initialize(source)
        # Check for URL in a footer and get the real data if so configured
        if get_footer_url and hasattr(msg, 'footer'):
            logger.info('Footer found in SDMX message.')
            # Retrieve the first URL in the footer, if any
            url_l = [
                i for i in msg.footer.text if remote.is_url(i)]
            if url_l:
                # found an URL. Wait and try to request it
                footer_url = url_l[0]
                seconds, attempts = get_footer_url
                logger.info(
                    'Found URL in footer. Making %i requests, waiting %i seconds in between.', attempts, seconds)
                for a in range(attempts):
                    sleep(seconds)
                    try:
                        return self.get(tofile=tofile, url=footer_url, headers=headers)
                    except Exception as e:
                        logger.info(
                            'Attempt #%i raised the following exeption: %s', a, str(e))
        # Select default writer
        if not writer:
            if hasattr(msg, 'data'):
                writer = 'pandasdmx.writer.data2pandas'
            else:
                writer = 'pandasdmx.writer.structure2pd'
        r = Response(msg, url, resp_headers, status_code, writer=writer)
        # store in memory cache if needed
        if memcache and r.status_code == 200:
            self.cache[memcache] = r
        return r

__all__ = ["Request"]
    