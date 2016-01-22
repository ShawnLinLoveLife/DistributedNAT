"""
This is a flask webapp module which impletements route functions.
"""


import json
import flask

import of_handler

from logger import get_logger
from config import get_config
from db_handler import DBHandler


__all__ = ['create_app']
"""
used_ports records used ports and the nat ip:ports as:
{
    eip_1: {
        port_1: (int_ip_1, int_port_1),
        port_2: (int_ip_2, int_port_2),
        ...
    },
    ...
}
"""
used_ports = dict([(rule['ext_ip'], {}) for rule in DBHandler().get()])
used_flowid = []
LOG = get_logger()
GWID = get_config().getint('default', 'gw_switch_id')


def alloc_port(src_ip, src_port, dst_ip, dst_port, switch, switch_port):
    """
    Allocate a temporary EIP:port for this flow
    """
    handler = DBHandler()
    if src_port == 0:
        return
    print src_ip
    nat_rule = handler.get(int_ip=src_ip)
    print nat_rule
    if nat_rule:
        eip = nat_rule[0].get('ext_ip')
        for port in range(1, 65536):
            print used_ports
            if port not in used_ports.get(eip).keys():
                #get unused flow ID
                for flowid in range(0, 999):
                    if flowid not in used_flowid:
                        used_flowid.append(flowid)
                        break
                else:
                    return 'ERROR'
                used_ports.get(eip)[port] = (src_ip, src_port, dst_ip, dst_port, flowid)
                #set SNAT flow
                egress_flow = [src_ip, src_port, dst_ip, dst_port]
                of_handler.set_snat(egress_flow, eip, port, 1000 + flowid, switch)
                #set DNAT flow
                ingress_flow = [dst_ip, dst_port, eip, src_port]
                of_handler.set_dnat(ingress_flow, src_ip, src_port, 2000 + flowid, switch, switch_port)
                #set ROUTE flow
                of_handler.set_route(ingress_flow, int(switch) + 1, flowid, GWID)
                return json.dumps([eip, port])
    return 'ERROR'


def expire_port(src_ip, src_port, dst_ip, dst_port, switch, switch_port):
    """
    Expire a temporary EIP:port for this flow
    """
    handler = DBHandler()
    nat_rule = handler.get(int_ip=src_ip)
    if nat_rule:
        eip = nat_rule[0].get('ext_ip')
        for port in used_ports.get(eip):
            if used_ports.get(eip).get(port)[:4] == (src_ip, src_port, dst_ip, dst_port):
                flow = used_ports.get(eip).pop(port)
                flowid = flow.pop(4)
                #set flowid unused
                used_flowid.remove(flowid)
                #rm ROUTE flow
                ingress_flow = [dst_ip, dst_port, eip, src_port]
                of_handler.set_route(ingress_flow, switch + 1, flowid, GWID, method='DELETE')
    return 'OK'


def parse_packet_in_params():
    '''
    get params of request body
    '''
    src_ip = flask.request.args.get('srcIp')
    src_port = flask.request.args.get('srcPort')
    src_port = int(src_port, 16)
    dst_ip = flask.request.args.get('dstIp')
    dst_port = flask.request.args.get('dstPort')
    dst_port = int(dst_port, 16)
    switch = flask.request.args.get('switchId')
    switch_port = flask.request.args.get('switchPort')
    return src_ip, src_port, dst_ip, dst_port, switch, switch_port

def handle_temporary_eip_port_request():
    """
    Generate/Delete temporary EIP:port for specified src_ip:src_port
    """
    src_ip, src_port, dst_ip, dst_port, switch, switch_port = parse_packet_in_params()
    if flask.request.method == 'GET':
        return alloc_port(src_ip, src_port, dst_ip, dst_port, switch, switch_port)
    if flask.request.method == 'GET':
        return expire_port(src_ip, src_port, dst_ip, dst_port, switch, switch_port)


def bind_eip(bindings):
    """
    Add NAT rules for each internal IP to EIP
    """
    global used_ports
    handler = DBHandler()
    for int_ip in bindings['int_ip']:
        #FIXME judge if the int_ip or ext_ip exists first
        handler.add(int_ip, bindings['ext_ip'])
    used_ports.setdefault(bindings['ext_ip'], {})


def unbind_eip(bindings):
    """
    Delete NAT rules for each internal IP to EIP
    """
    global used_ports
    handler = DBHandler()
    for int_ip in bindings['int_ip']:
        handler.add(int_ip)
    if not len(handler.get(ext_ip=bindings['ext_ip'])):
        used_ports.pop(bindings['ext_ip'])


def get_nat():
    """
    return all NAT rules
    """
    handler = DBHandler()
    ret = handler.get()
    if ret:
        return json.dumps(ret)
    else:
        return ''

def handle_shared_eip_request():
    """
    Add/Delete a mapping of internal IPs to EIP
    """
    data = flask.request.json
    if flask.request.method in ('PUT', 'POST'):
        bind_eip(data)
        return 'OK'
    elif flask.request.method == 'DELETE':
        unbind_eip(data)
        return 'OK'
    elif flask.request.method == 'GET':
        return get_nat()


def create_app():
    """ Return a flask application """
    app = flask.Flask(__name__)
    app.add_url_rule('/temporary_eip_port',
                     'GET for packet-in, DELETE for flow-removed',
                     handle_temporary_eip_port_request,
                     methods=['GET', 'DELETE'])
    app.add_url_rule('/shared_eip',
                     'CIDR of shared EIP',
                     handle_shared_eip_request,
                     methods=['POST', 'DELETE', 'PUT', 'GET'])

    @app.before_request
    def log_request():
        """ log the request args and body, for tracing """
        LOG.info('URL: %s, BODY: %s' % (flask.request.url, flask.request.data))

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host='0.0.0.0', port=1024, debug=True)
