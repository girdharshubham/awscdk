import os
from aws_cdk import Stack
from constructs import Construct
from awscdk.resources import ssm, eks, custom_resource as cr


class App(Stack):

    def __init__(self, scope: Construct, construct_id: str, environment: str, helm_charts=None, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        (
            cr.HelmValue(self, f"{construct_id}HelmValue", environment)
        )
        (
            ssm
            .DeploymentEnvironmentParameter(self, f"{construct_id}DeploymentEnvironmentParameter", environment)
        )
        (
            eks
            .EksCluster(self, f"{construct_id}EKSCluster", version=1.28)
            .add_node_pool()
        )
