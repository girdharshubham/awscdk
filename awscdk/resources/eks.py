from aws_cdk import (
    aws_eks as eks,
    lambda_layer_kubectl,
    aws_ec2 as ec2,
    aws_lambda as function
)
from aws_cdk.aws_eks import Cluster
from constructs import Construct


class EksCluster(Construct):
    cluster: Cluster

    def __init__(self,
                 scope: Construct,
                 id: str,
                 version: float,
                 ) -> None:
        super().__init__(scope, id)

        self.cluster = eks.Cluster(self,
                                   id,
                                   version=self.__parse_version(version),
                                   kubectl_layer=self.__lambda_layer("Default")
                                   )

    def __lambda_layer(self, type: str) -> function.LayerVersion:

        match type:
            case "Default":
                return lambda_layer_kubectl.KubectlLayer(self, "KubectlHelm")

    def __parse_version(self, version: float) -> eks.KubernetesVersion.version:

        match version:
            case 1.28:
                return eks.KubernetesVersion.V1_28
            case 1.27:
                return eks.KubernetesVersion.V1_27
            case 1.26:
                return eks.KubernetesVersion.V1_26
            case _:
                raise Exception("Unsupported Kubernetes Version")

    def __parse_instance_types(self, instance: str):
        return ec2.InstanceType(instance)

    def add_node_pool(self,
                      min: int = 1,
                      max: int = 1,
                      desired: int = 1,
                      instance_types=["t3.micro"],
                      capacity_type=eks.CapacityType.SPOT
                      ):

        """
        Creates a node pool. Defaults to a spot pool with (min,desired,max,[type])values(1,1,1,spot,[t3.micro]) configuration
        :param min:
        :param max:
        :param desired:
        :param instance_types:
        :param capacity_type:
        :return:
        """

        (self
         .cluster
         .add_nodegroup_capacity(f"{id}SpotPool",
                                 capacity_type=capacity_type,
                                 min_size=min,
                                 desired_size=desired,
                                 max_size=max,
                                 instance_types=list(map(self.__parse_instance_types, instance_types))
                                 )
         )
        return self

    def add_helm_chart(self, charts):
        """
        Sample:
        {
            "IngressNginx": {
                "chart": "ingress-nginx",
                "repository": "https://kubernetes.github.io/ingress-nginx",
                "namespace": "ingress-nginx",
                "createNamespace": True,
            }
        }

        :param charts:
        :return: None
        """
        for key, value in charts.items():
            self.cluster.add_helm_chart(key,
                                        chart=value["chart"],
                                        repository=value["repository"],
                                        namespace=value["namespace"],
                                        create_namespace=value["createNamespace"],
                                        values=value["values"]
                                        )

        return self
