from typing import Optional, Sequence

import pulumi
import pulumi_aws as aws
from pulumi import ComponentResource

from ._inputs import RdsSecurityGroupIngressArgs


class RdsSecurityGroup(ComponentResource):
    """A class creating an RDS security resource"""

    def __init__(
        self,
        name: str,
        db_engine: str,
        vpc_id: str,
        ingress_security_group_cidrs: Optional[
            pulumi.Input[Sequence[str]]
        ] = [],  # noqa E501
        ingress_security_group_ids: Optional[
            pulumi.Input[Sequence[str]]
        ] = None,  # noqa E501
        opts: Optional[pulumi.ResourceOptions] = None,
    ):
        super().__init__(
            f"pulumi-components:aws:components:{name}-security-group",
            name,
            {},
            opts,  # noqa E501
        )
        self.security_group = aws.ec2.SecurityGroup(
            f"{name}-security-group",
            description=f"{name} security-group",
            vpc_id=vpc_id,
            ingress=RdsSecurityGroupIngressArgs(
                db_engine,
                f"{name}-security-group-ingress-rule",
                ingress_security_group_cidrs,
                ingress_security_group_ids,
            ).security_group_ingress_args,
            egress=[
                aws.ec2.SecurityGroupEgressArgs(
                    from_port=0,
                    to_port=0,
                    protocol="-1",
                    cidr_blocks=["0.0.0.0/0"],  # noqa E501
                )
            ],
            opts=pulumi.ResourceOptions(parent=self),
        )
        self.register_outputs({"id": self.security_group.id})


class RdsSubnetGroup(ComponentResource):
    """A class defining Subnet group custom resource"""

    def __init__(
        self,
        name,
        subnet_ids: pulumi.Input[Sequence[str]],
        opts: Optional[pulumi.ResourceOptions] = None,
    ):
        super().__init__(
            f"pulumi-components:aws:components:{name}-subnet-group",
            name,
            {},
            opts,  # noqa E501
        )
        if not subnet_ids:
            raise ValueError["subnet ids are required"]
        self.subnet_group = aws.rds.SubnetGroup(
            f"{name}-subnet-group",
            subnet_ids=subnet_ids,
            opts=pulumi.ResourceOptions(parent=self),
        )
        self.register_outputs({"subnet_group": self.subnet_group})
