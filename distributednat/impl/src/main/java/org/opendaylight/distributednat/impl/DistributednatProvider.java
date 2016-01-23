/*
 * Copyright © 2015 Xiao Lin, Gang Zhao, Zhilan Huang and others.  All rights reserved.
 *
 * This program and the accompanying materials are made available under the
 * terms of the Eclipse Public License v1.0 which accompanies this distribution,
 * and is available at http://www.eclipse.org/legal/epl-v10.html
 */
package org.opendaylight.distributednat.impl;

import org.opendaylight.controller.sal.binding.api.BindingAwareBroker.ProviderContext;
import org.opendaylight.controller.sal.binding.api.BindingAwareProvider;
import org.opendaylight.controller.sal.binding.api.NotificationProviderService;
import org.opendaylight.yang.gen.v1.urn.opendaylight.packet.basepacket.rev140528.packet.chain.grp.PacketChain;
import org.opendaylight.yang.gen.v1.urn.opendaylight.packet.basepacket.rev140528.packet.chain.grp.packet.chain.packet.RawPacket;
import org.opendaylight.yang.gen.v1.urn.opendaylight.packet.ethernet.rev140528.ethernet.packet.received.packet.chain.packet.EthernetPacket;
import org.opendaylight.yang.gen.v1.urn.opendaylight.packet.ipv4.rev140528.Ipv4PacketListener;
import org.opendaylight.yang.gen.v1.urn.opendaylight.packet.ipv4.rev140528.Ipv4PacketReceived;
import org.opendaylight.yang.gen.v1.urn.opendaylight.packet.ipv4.rev140528.ipv4.packet.received.packet.chain.packet.Ipv4Packet;
import org.opendaylight.yangtools.yang.binding.InstanceIdentifier;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.BufferedReader;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.net.URLConnection;

public class DistributednatProvider implements BindingAwareProvider, AutoCloseable, Ipv4PacketListener/*, PacketProcessingListener*/ {

    private static final Logger LOG = LoggerFactory.getLogger(DistributednatProvider.class);
    private static NotificationProviderService nps = null;

    public void getNotification(NotificationProviderService nps) {
        this.nps = nps;
    }

    public static final String bytesToHexStringFromBeginToEnd(byte[] bArray, int begin, int end) {
        StringBuffer sb = new StringBuffer(bArray.length);
        String sTemp;
        for (int i = begin; i <= end; i++) {
            sTemp = Integer.toHexString(0xFF & bArray[i]);
            if (sTemp.length() < 2)
                sb.append(0);
            sb.append(sTemp.toUpperCase());
        }
        return sb.toString();
    }

    public static final String byteToHexString(byte b) {
        return Integer.toHexString(0xFF & b);
    }

    public static String doGet(String srcIp, String dstIp, String srcTcpPort, String dstTcpPort, String switchId, String switchPort) throws Exception {
        StringBuffer sb = new StringBuffer("http://localhost:6666/temporary_eip_port?");
        sb.append("srcIp=" + srcIp + "&");
        sb.append("dstIp=" + dstIp + "&");
        sb.append("srcPort=" + srcTcpPort + "&");
        sb.append("dstPort=" + dstTcpPort + "&");
        sb.append("switchId=" + switchId + "&");
        sb.append("switchPort=" + switchPort);

        String finalUrl = sb.toString();
        LOG.info("final url is " + finalUrl);
        URL localURL = new URL(finalUrl);
        URLConnection connection = localURL.openConnection();
        HttpURLConnection httpURLConnection = (HttpURLConnection)connection;

        httpURLConnection.setRequestMethod("GET");
        httpURLConnection.setRequestProperty("Content-Type", "application/json");

        InputStream inputStream = null;
        InputStreamReader inputStreamReader = null;
        BufferedReader reader = null;
        StringBuffer resultBuffer = new StringBuffer();
        String tempLine = null;

        if (httpURLConnection.getResponseCode() >= 300) {
            throw new Exception("HTTP Request is not success, Response code is " + httpURLConnection.getResponseCode());
        }

        try {
            inputStream = httpURLConnection.getInputStream();
            inputStreamReader = new InputStreamReader(inputStream);
            reader = new BufferedReader(inputStreamReader);

            while ((tempLine = reader.readLine()) != null) {
                resultBuffer.append(tempLine);
            }

        } finally {

            if (reader != null) {
                reader.close();
            }

            if (inputStreamReader != null) {
                inputStreamReader.close();
            }

            if (inputStream != null) {
                inputStream.close();
            }

        }

        return resultBuffer.toString();
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

        byte[] raw_data = packetReceived.getPayload();
        String raw_data_string = bytesToHexStringFromBeginToEnd(raw_data, 0, raw_data.length-1);
        InstanceIdentifier iid = rawPacket.getIngress().getValue();

        String iid_string = iid.toString();
        String verifyIp = bytesToHexStringFromBeginToEnd(raw_data, 12, 13);
        String verifyTCP = bytesToHexStringFromBeginToEnd(raw_data, 23, 23);
        String srcIp = ipv4Packet.getSourceIpv4().getValue();//bytesToHexStringFromBeginToEnd(raw_data, 26, 29);
        String dstIp = ipv4Packet.getDestinationIpv4().getValue();//bytesToHexStringFromBeginToEnd(raw_data, 30, 33);
        String srcPort = bytesToHexStringFromBeginToEnd(raw_data, 34, 35);
        String dstPort = bytesToHexStringFromBeginToEnd(raw_data, 36, 37);
        String switchId = null;
        String switchPort = null;
        LOG.info("----------");
        LOG.info("SourceIP: "+ipv4Packet.getSourceIpv4().getValue());
        LOG.info("DstIP: "+ipv4Packet.getDestinationIpv4().getValue());
        LOG.info("verifyIp:" + verifyIp);
        LOG.info("verifyTCP: " + verifyTCP);
        LOG.info("srcIp: " + srcIp);
        LOG.info("dstIp: " + dstIp);
        LOG.info("srcPort: " + srcPort);
        LOG.info("dstPort: " + dstPort);

        if (verifyIp.equals("0800") && verifyTCP.equals("06")) {
            LOG.info("Receive a TCP packet");
            LOG.info(iid.toString());
            char[] charIId = iid_string.toCharArray();
            int switchIdIndex = iid_string.indexOf("openflow");
            int switchPortIndex = iid_string.lastIndexOf("openflow");
            switchId = String.valueOf(charIId[switchIdIndex + 9]);
            switchPort = String.valueOf(charIId[switchPortIndex + 11]);
            LOG.info("switchId: " + switchId);
            LOG.info("siwtchPort: " + switchPort);
            try {
                //doGet(String srcIp, String dstIp, String srcTcpPort, String dstTcpPort, String switchId, String switchPort)
                LOG.info(doGet(srcIp, dstIp, srcPort, dstPort, switchId, switchPort));
            } catch (Exception e) {
                LOG.info(e.toString());
            }
        }
        LOG.info("----------");
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
