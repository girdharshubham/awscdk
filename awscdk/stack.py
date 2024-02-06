import os

import aws_cdk
from aws_cdk import Stack
from constructs import Construct
from awscdk.resources import ssm, eks, custom_resource as cr


class App(Stack):

    def __init__(
            self,
            scope: Construct,
            construct_id: str,
            environment: str,
            system_master,
            helm_charts=None,
            **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)
        ssm_parameter_base = "/platform/account"
        # register_outout holds the helm release values for nginx ingress. I think a minor todo would be to register it with eks's helm chart - need to figure out how they'd work together
        cr.HelmValue(self, f"{construct_id}HelmValue", ssm_parameter_base, environment).register_output()

        ssm.DeploymentEnvironmentParameter(self, f"{construct_id}DeploymentEnvironmentParameter", environment,
                                           ssm_parameter_base)

        eks.EksCluster(self, f"{construct_id}EKSCluster", version=1.28, system_master=system_master)
