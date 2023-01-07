from typing import Optional, Sequence

import pulumi
import pulumi_aws as aws
from pulumi import CustomResource

# from ._inputs import ClusterNodeGroupOptionArgs, KubeConfigOptionArgs


class EksCluster(CustomResource):
    """A class defining an EKS cluster custom resource"""

    def __init(
        self,
        name: str,
        admin_role_arn: pulumi.Input[str],
        subnet_ids: Sequence[pulumi.Input[str]],
        vpc_id: pulumi.Input[str],
        k8s_version: pulumi.Input[str],
        # vpc_cni_addon_version: str,
        # core_dns_addon_version: str,
        # kubeproxy_addon_version: str,
        # node_groups: Sequence[ClusterNodeGroupOptionArgs],
        # bottlerocket_operator_version: str,
        # provider_credentials_opts: KubeConfigOptionArgs,
        public_access_cidr: Optional[Sequence[pulumi.Input[str]]] = [
            "0.0.0.0/0"
        ],  # noqa E501
        endpoint_private_access: Optional[bool] = False,
        endpoint_public_access: Optional[bool] = True,
        opts: Optional[pulumi.ResourceOptions] = None,
    ) -> None:
        super.__init__(
            "pulumi-components:aws:components:eks-cluster", name, {}, opts
        )  # noqa E501

        # Create ClusterVpcConfig
        self.cluster_vpc_config = aws.eks.ClusterVpcConfigArgs(
            f"{name}-cluster-vpc-config",
            subnet_ids=subnet_ids,
            vpc_id=vpc_id,
            endpoint_private_access=endpoint_private_access,
            endpoint_public_access=endpoint_public_access,
            public_access_cidrs=public_access_cidr,
        )

        # Create EKS Cluster
        self.cluster = aws.eks.Cluster(
            role_arn=admin_role_arn,
            vpc_config=self.cluster_vpc_config,
            name=name,
            version=k8s_version,
        )
