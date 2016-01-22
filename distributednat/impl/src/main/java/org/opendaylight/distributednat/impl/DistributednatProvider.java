/*
 * Copyright © 2015 Xiao Lin, Gang Zhao, Zhilan Huang and others.  All rights reserved.
 *
 * This program and the accompanying materials are made available under the
 * terms of the Eclipse Public License v1.0 which accompanies this distribution,
 * and is available at http://www.eclipse.org/legal/epl-v10.html
 */
package org.opendaylight.distributednat.impl;

import org.opendaylight.controller.md.sal.binding.api.ReadOnlyTransaction;
import org.opendaylight.controller.sal.binding.api.BindingAwareBroker.ProviderContext;
import org.opendaylight.controller.sal.binding.api.BindingAwareProvider;
import org.opendaylight.controller.sal.binding.api.NotificationProviderService;
import org.opendaylight.yang.gen.v1.urn.ietf.params.xml.ns.yang.ietf.inet.types.rev100924.IpAddress;
import org.opendaylight.yang.gen.v1.urn.opendaylight.packet.basepacket.rev140528.packet.chain.grp.PacketChain;
import org.opendaylight.yang.gen.v1.urn.opendaylight.packet.basepacket.rev140528.packet.chain.grp.packet.chain.packet.RawPacket;
import org.opendaylight.yang.gen.v1.urn.opendaylight.packet.ethernet.rev140528.ethernet.packet.received.packet.chain.packet.EthernetPacket;
import org.opendaylight.yang.gen.v1.urn.opendaylight.packet.ipv4.rev140528.Ipv4PacketListener;
import org.opendaylight.yang.gen.v1.urn.opendaylight.packet.ipv4.rev140528.Ipv4PacketReceived;
import org.opendaylight.yang.gen.v1.urn.opendaylight.packet.ipv4.rev140528.ipv4.packet.received.packet.chain.packet.Ipv4Packet;
import org.opendaylight.yang.gen.v1.urn.opendaylight.packet.service.rev130709.PacketProcessingListener;
import org.opendaylight.yang.gen.v1.urn.opendaylight.packet.service.rev130709.PacketReceived;
import org.opendaylight.yangtools.yang.binding.InstanceIdentifier;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DistributednatProvider implements BindingAwareProvider, AutoCloseable, Ipv4PacketListener/*, PacketProcessingListener*/ {

    private static final Logger LOG = LoggerFactory.getLogger(DistributednatProvider.class);
    private static NotificationProviderService nps = null;

    public void getNotification(NotificationProviderService nps) {
        this.nps = nps;
    }

/*    @Override
    public void onPacketReceived(PacketReceived packetReceived) {
        LOG.info("I received a packet");
    }*/

    public static final String bytesToHexString(byte[] bArray) {
        StringBuffer sb = new StringBuffer(bArray.length);
        String sTemp;
        for (int i = 0; i < bArray.length; i++) {
            sTemp = Integer.toHexString(0xFF & bArray[i]);
            if (sTemp.length() < 2)
                sb.append(0);
            sb.append(sTemp.toUpperCase());
        }
        return sb.toString();
    }

    @Override
    public void onIpv4PacketReceived(Ipv4PacketReceived packetReceived) {
        LOG.info("on Ipv4PacketReceived");
        if(packetReceived == null || packetReceived.getPacketChain() == null) {
            return;
        }

        RawPacket rawPacket = null;
        EthernetPacket ethernetPacket = null;
        Ipv4Packet ipv4Packet = null;
        for(PacketChain packetChain : packetReceived.getPacketChain()) {
            if(packetChain.getPacket() instanceof RawPacket) {
                rawPacket = (RawPacket) packetChain.getPacket();
            } else if(packetChain.getPacket() instanceof EthernetPacket) {
                ethernetPacket = (EthernetPacket) packetChain.getPacket();
            } else if(packetChain.getPacket() instanceof Ipv4Packet) {
                ipv4Packet = (Ipv4Packet) packetChain.getPacket();
            }
        }
        if(rawPacket == null || ethernetPacket == null || ipv4Packet == null) {
            return;
        }
        //LOG.info(rawPacket.getIngress().toString());
        //LOG.info(rawPacket.toString());
        byte[] raw_data = packetReceived.getPayload();
        String raw_data_string = bytesToHexString(raw_data);
        LOG.info("PacketRawData:"+raw_data_string);
        InstanceIdentifier iid = rawPacket.getIngress().getValue();
        LOG.info("SourceIP:"+ipv4Packet.getSourceIpv4().getValue());
        LOG.info("DstIP:"+ipv4Packet.getDestinationIpv4().getValue());
        //LOG.info(iid.toString());

        //if(!IPV4_IP_TO_IGNORE.equals(ipv4Packet.getSourceIpv4().getValue())) {
        //    addressObservationWriter.addAddress(ethernetPacket.getSourceMac(),
        //            new IpAddress(ipv4Packet.getSourceIpv4().getValue().toCharArray()),
        //            rawPacket.getIngress());
        //}
    }
    @Override
    public void onSessionInitiated(ProviderContext session) {
        LOG.info("DistributednatProvider Session Initiated");
    }

    @Override
    public void close() throws Exception {
        LOG.info("DistributednatProvider Closed");
    }

}
