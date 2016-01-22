import requests
from logger import get_logger


LOG = get_logger()


SNAT_FLOW = u'''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<flow xmlns="urn:opendaylight:flow:inventory">
  <priority>10</priority>
  <flow-name>snat1</flow-name>
  <match>
    <ethernet-match>
      <ethernet-type>
        <type>2048</type>
      </ethernet-type>
    </ethernet-match>
    <ipv4-source>%(srcip)s/32</ipv4-source>
    <ipv4-destination>%(dstip)s/32</ipv4-destination>
    <ip-match>
      <ip-protocol>6</ip-protocol>
      <ip-proto>ipv4</ip-proto>
    </ip-match>
    <tcp-source-port>%(srcport)d</tcp-source-port>
    <tcp-destination-port>%(dstport)d</tcp-destination-port>
  </match>
  <id>%(flowid)d</id>
  <table_id>0</table_id>
  <idle-timeout>1800</idle-timeout>
  <instructions>
    <instruction>
      <order>0</order>
      <apply-actions>
        <action>
          <order>0</order>
          <set-nw-src-action>
            <ipv4-address>%(newip)s/32</ipv4-address>
          </set-nw-src-action>
        </action>
        <action>
          <order>1</order>
          <set-tp-src-action>
            <port>%(newport)d</port>
          </set-tp-src-action>
        </action>
        <action>
          <order>2</order>
          <output-action>
            <output-node-connector>3</output-node-connector>
            <max-length>65535</max-length>
          </output-action>
        </action>
      </apply-actions>
    </instruction>
  </instructions>
</flow>
'''

DNAT_FLOW = u'''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<flow xmlns="urn:opendaylight:flow:inventory">
  <priority>10</priority>
  <flow-name>dnat1</flow-name>
  <match>
    <ethernet-match>
      <ethernet-type>
        <type>2048</type>
      </ethernet-type>
    </ethernet-match>
    <ipv4-source>%(srcip)s/32</ipv4-destination>
    <ipv4-destination>%(dstip)s/32</ipv4-destination>
    <ip-match>
      <ip-protocol>6</ip-protocol>
      <ip-proto>ipv4</ip-proto>
    </ip-match>
    <tcp-source-port>%(srcport)d</tcp-source-port>
    <tcp-destination-port>%(dstport)d</tcp-destination-port>
  </match>
  <id>%(flowid)d</id>
  <table_id>0</table_id>
  <idle-timeout>1800</idle-timeout>
  <instructions>
    <instruction>
      <order>0</order>
      <apply-actions>
        <action>
          <order>0</order>
          <set-nw-dst-action>
            <ipv4-address>%(newip)s/32</ipv4-address>
          </set-nw-dst-action>
        </action>
        <action>
          <order>1</order>
          <set-tp-dst-action>
            <port>%(newport)d</port>
          </set-tp-dst-action>
        </action>
        <action>
          <order>2</order>
          <output-action>
            <output-node-connector>1</output-node-connector>
            <max-length>65535</max-length>
          </output-action>
        </action>
      </apply-actions>
    </instruction>
  </instructions>
</flow>
'''

ROUTE_FLOW = u'''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<flow xmlns="urn:opendaylight:flow:inventory">
  <priority>10</priority>
  <flow-name>forw1</flow-name>
  <match>
    <ethernet-match>
      <ethernet-type>
        <type>2048</type>
      </ethernet-type>
    </ethernet-match>
    <ipv4-source>%(srcip)s/32</ipv4-destination>
    <ipv4-destination>%(dstip)s/32</ipv4-destination>
    <tcp-source-port>%(srcport)d</tcp-source-port>
    <tcp-destination-port>%(dstport)d</tcp-destination-port>
  </match>
  <id>%(flowid)d</id>
  <table_id>0</table_id>
  <idle-timeout>1800</idle-timeout>
  <instructions>
    <instruction>
      <order>0</order>
      <apply-actions>
        <action>
          <order>0</order>
          <output-action>
            <output-node-connector>%(outport)d</output-node-connector>
            <max-length>65535</max-length>
          </output-action>
        </action>
      </apply-actions>
    </instruction>
  </instructions>
</flow>
'''


OF_URL = u'http://localhost:8181/restconf/config/opendaylight-inventory:nodes/node/openflow:%d/table/0/flow/%d'

REQUESTS_FUNC = {'PUT': requests.put,
                 'POST': requests.post,
                 'GET': requests.get,
                 'DELETE': requests.delete}

def set_snat(flow, newip, newport, flowid, switchid, method='PUT'):
    args = {
        'srcip': flow[0],
        'srcport': flow[1],
        'dstip': flow[2],
        'dstport': flow[3],
        'newip': newip,
        'newport': newport,
        'flowid': flowid
    }
    url = OF_URL % (switchid, flowid)
    data = SNAT_FLOW % args
    LOG.info('REQUEST SNAT - METHOD: %s, URL: %s, DATA: %s' % (method, url, data))
    #resp = REQUESTS_FUNC.get(method)(url, data=data)
    #LOG.info('RESPONSE SNAT - STATUS: %d, TEXT: %s' % (resp.status_code, resp.text))


def set_dnat(flow, newip, newport, flowid, switchid, method='PUT'):
    args = {
        'srcip': flow[0],
        'srcport': flow[1],
        'dstip': flow[2],
        'dstport': flow[3],
        'newip': newip,
        'newport': newport,
        'flowid': flowid
    }
    url = OF_URL % (switchid, flowid)
    data = DNAT_FLOW % args
    LOG.info('REQUEST DNAT - METHOD: %s, URL: %s, DATA: %s' % (method, url, data))
    #resp = REQUESTS_FUNC.get(method)(url, data=data)
    #LOG.info('RESPONSE SNAT - STATUS: %d, TEXT: %s' % (resp.status_code, resp.text))


def set_route(flow, outport, flowid, switchid, method='PUT'):
    args = {
        'srcip': flow[0],
        'srcport': flow[1],
        'dstip': flow[2],
        'dstport': flow[3],
        'outport': outport,
        'flowid': flowid
    }
    url = OF_URL % (switchid, flowid)
    data = ROUTE_FLOW % args
    LOG.info('REQUEST ROUTE - METHOD: %s, URL: %s, DATA: %s' % (method, url, data))
    #resp = REQUESTS_FUNC.get(method)(url, data=data)
    #LOG.info('RESPONSE SNAT - STATUS: %d, TEXT: %s' % (resp.status_code, resp.text))