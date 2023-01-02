"""This module contains nested inputs for the vpc component"""
import os
from typing import Mapping, Optional

import pulumi
from .exceptions import VpcPeeringException


@pulumi.input_type
class VpcSubnetArgs:
    """A class defining a subnet resource in the vpc component"""

    cidr: pulumi.Input[str] = pulumi.property("cidr")
    az: pulumi.Input[str] = pulumi.property("az")
    tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = pulumi.property(
        "tags", default=None
    )


@pulumi.input_type
class VpcPeeringArgs:
    """A class defining a vpc-peering resource in the vpc component"""

    def __init__(
        self,
        *,
        name: pulumi.Input[str],
        vpc_id: pulumi.Input[str],
        accepter: bool = False,
        cidr: Optional[str] = None,
        account_id: Optional[str] = None,
        aws_profile: Optional[str] = os.getenv("AWS_PROFILE"),
    ):
        if accepter and (account_id or cidr):
            raise VpcPeeringException(
                "Account ID or CIDR can't be defined when accepter is set to True"
            )
        pulumi.set(self, "name", name)
        pulumi.set(self, "vpc_id", vpc_id)
        pulumi.set(self, "accepter", accepter)
        pulumi.set(self, "cidr", cidr)
        pulumi.set(self, "account_id", account_id)
        pulumi.set(self, "aws_profile", aws_profile)

    @property
    @pulumi.getter(name="name")
    def name(self) -> pulumi.Input[str]:
        """vpc name"""
        ...

    @property
    @pulumi.getter(name="vpc_id")
    def vpc_id(self) -> pulumi.Input[str]:
        """vpc id"""
        ...

    @property
    @pulumi.getter(name="accepter")
    def accepter(self) -> bool:
        """Identifies the side of the peering connection"""
        ...

    @property
    @pulumi.getter(name="cidr")
    def cidr(self) -> Optional[str]:
        """cidr in peering connection"""
        ...

    @property
    @pulumi.getter(name="account_id")
    def account_id(self) -> Optional[str]:
        """account_id associated with the peering connection"""
        ...

    @property
    @pulumi.getter(name="aws_profile")
    def aws_profile(self) -> Optional[str]:
        """aws profile required for peering connection"""
        ...
