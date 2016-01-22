/*
 * Copyright © 2015 Xiao Lin, Gang Zhao, Zhilan Huang and others.  All rights reserved.
 *
 * This program and the accompanying materials are made available under the
 * terms of the Eclipse Public License v1.0 which accompanies this distribution,
 * and is available at http://www.eclipse.org/legal/epl-v10.html
 */
package org.opendaylight.yang.gen.v1.urn.opendaylight.params.xml.ns.yang.distributednat.impl.rev141210;

import org.opendaylight.controller.sal.binding.api.NotificationProviderService;
import org.opendaylight.distributednat.impl.DistributednatProvider;

public class DistributednatModule extends org.opendaylight.yang.gen.v1.urn.opendaylight.params.xml.ns.yang.distributednat.impl.rev141210.AbstractDistributednatModule {
    public DistributednatModule(org.opendaylight.controller.config.api.ModuleIdentifier identifier, org.opendaylight.controller.config.api.DependencyResolver dependencyResolver) {
        super(identifier, dependencyResolver);
    }

    public DistributednatModule(org.opendaylight.controller.config.api.ModuleIdentifier identifier, org.opendaylight.controller.config.api.DependencyResolver dependencyResolver, org.opendaylight.yang.gen.v1.urn.opendaylight.params.xml.ns.yang.distributednat.impl.rev141210.DistributednatModule oldModule, java.lang.AutoCloseable oldInstance) {
        super(identifier, dependencyResolver, oldModule, oldInstance);
    }

    @Override
    public void customValidation() {
        // add custom validation form module attributes here.
    }

    @Override
    public java.lang.AutoCloseable createInstance() {
        DistributednatProvider provider = new DistributednatProvider();
        getBrokerDependency().registerProvider(provider);
        NotificationProviderService nps = getNotificationServiceDependency();
        provider.getNotification(nps);
        nps.registerNotificationListener(provider);
        return provider;
    }

}
