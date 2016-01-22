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
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DistributednatProvider implements BindingAwareProvider, AutoCloseable {

    private static final Logger LOG = LoggerFactory.getLogger(DistributednatProvider.class);


    @Override
    public void onSessionInitiated(ProviderContext session) {
        LOG.info("DistributednatProvider Session Initiated");
    }

    @Override
    public void close() throws Exception {
        LOG.info("DistributednatProvider Closed");
    }

}
