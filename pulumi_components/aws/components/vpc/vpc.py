"""Module defining the vpc custom resource"""
import ipaddress

import pulumi
import pulumi_aws as aws
from typing import Sequence, Optional
from _inputs import VpcSubnetArgs, VpcPeeringArgs


class Vpc(pulumi.CustomResource):
    """A class defining a VPC custom resource"""
    def __init__(self,
                 name: str,
                 cidr: pulumi.Input[str],
                 public_subnets: Sequence[VpcSubnetArgs],
                 private_subnets: Optional[VpcSubnetArgs],
                 vpn_peering: Optional[VpcPeeringArgs] = None,
                 other_peering: Optional[Sequence[VpcPeeringArgs]] = None,
                 ha_nat: bool = True,
                 enable_dns_hostname: bool = True,
                 enable_dns_support: bool = True,
                 instance_tenancy: str = "default",
                 opts: Optional[pulumi.ResourceOptions] = None,
                 ):
        super().__init__("pulumi-components:aws:components:vpc", name, {}, opts)

        if instance_tenancy.lower() not in ["default", "dedicated"]:
            raise ValueError("instance tenancy can only have default or dedicated as values")

        # Check if correct cidr has been passed
        vpc_cidr = ipaddress.IPv4Network(cidr)

        # Create a VPC resource
        self.vpc = aws.ec2.Vpc(
            "vpc",
            args=aws.ec2.VpcArgs(
                cidr_block=str(vpc_cidr),
                enable_dns_hostname=enable_dns_hostname,
                enable_dns_support=enable_dns_support,
                instance_tenancy=instance_tenancy,
                opts=pulumi.ResourceOptions(parent=self)
            )
        )