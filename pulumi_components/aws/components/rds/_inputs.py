"""This module contains inputs for the rds components"""
from typing import Optional, Sequence

import pulumi
import pulumi_aws as aws


@pulumi.input_type
class RdsSecurityGroupIngressArgs:
    """A class defining a security group ingress args resource in rds security group"""  # noqa E501

    def __init__(
        self,
        db_engine: str,
        description: str,
        cidr_blocks: Optional[Sequence[pulumi.Input[str]]] = None,
        security_group_ids: Optional[Sequence[pulumi.Input[str]]] = None,
    ):
        if (
            db_engine.lower() == "postgresql"
            or db_engine.lower() == "postgres"  # noqa E501
        ):
            port = 5432
        elif db_engine.lower() == "mysql":
            port = 3306
        else:
            raise ValueError(
                "This component currently only supports Postgres and Mysql"
            )
        security_group_ingress_args = []
        if cidr_blocks:
            sgi_args = aws.ec2.SecurityGroupIngressArgs(
                from_port=port,
                to_port=port,
                description=description,
                protocol="tcp",
                cidr_blocks=cidr_blocks,
            )
            security_group_ingress_args.append(sgi_args)

        if security_group_ids:
            sgi_args = aws.ec2.SecurityGroupIngressArgs(
                from_port=port,
                to_port=port,
                description=description,
                protocol="tcp",
                security_groups=security_group_ids,
            )
            security_group_ingress_args.append(sgi_args)
        # Set security_group_ingress_args as a parameter
        pulumi.set(
            self, "security_group_ingress_args", security_group_ingress_args
        )  # noqa E501

    @property
    @pulumi.getter(name="security_group_ingress_args")
    def security_group_ingress_args(
        self,
    ) -> Sequence[aws.ec2.SecurityGroupIngressArgs]:  # noqa E501
        """Getter method for security group ingress args"""
        ...
