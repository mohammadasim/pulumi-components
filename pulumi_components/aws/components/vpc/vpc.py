"""Module defining the vpc custom resource"""
import ipaddress
from typing import Mapping, Optional, Sequence

import pulumi
import pulumi_aws as aws
from _inputs import VpcPeeringArgs, VpcSubnetArgs


class Vpc(pulumi.CustomResource):
    """A class defining a VPC custom resource"""

    def __init__(
        self,
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
            raise ValueError(
                "instance tenancy can only have default or dedicated as values"
            )

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
                opts=pulumi.ResourceOptions(parent=self),
            ),
        )

        # Create internet gateway resource
        self.igw = aws.ec2.InternetGateway(
            "internet-gateway",
            vpc_id=self.vpc.id,
            opts=pulumi.ResourceOptions(parent=self.vpc),
        )
        # Create VPC and VPN peering
        self.vpc_peering_routes = []

    def _create_peering(
        self,
        peering_accepter: bool,
        peering_vpc_name: str,
        peering_vpc_id: str,
        peering_profile: str = None,
        peering_account_id: str = None,
        peering_cidr: str = None,
        region: str = "eu-west-1",
    ) -> Mapping:
        """Creates peering connection. To create a peering connection,
        we must have the peering_vpc_id. If the account_id of the remote
        account is provided, we must also have the CIDR range. If account_id
        and cidr range not provided. The function must have a profile id, as
        that will be used to obtain this information."""
        remote_vpc = None
        remote_cidr_block = None
        remote_account_id = None
        same_account_peering = None
        conf = pulumi.Config("aws")
        # If we have the remote aws account id,
        # We must also have the cidr as well.
        if peering_account_id:
            remote_account_id = peering_account_id
            if peering_cidr:
                remote_cidr_block = peering_cidr
            else:
                raise ValueError("CIDR block not provided for peering")
        elif peering_profile:
            # Create a remote provider
            remote_provider = aws.Provider(
                f"{peering_profile}-{peering_vpc_name}-remote-provider",
                profile=peering_profile,
                region=region,
                skip_metadata_api_check=False
            )
            # Create remote resource option
            remote_resource_option = pulumi.ResourceOptions(
                parent=self, provider=remote_provider
            )
            # Create remote invoke option
            remote_invoke_option = pulumi.InvokeOptions(
                parent=self, provider=remote_provider
            )
            # Since we don't have the remote account id and cidr
            # We need to get that information, as it is required
            # for creating a peering connection
            remote_account_id = aws.get_caller_identity(
                opts=remote_invoke_option
            ).account_id
            # Get the remote vpc resource using the vpc_id provided
            remote_vpc = aws.ec2.Vpc.get(
                f"{peering_vpc_name}-vpc",
                id=peering_vpc_id,
                opts=remote_resource_option
            )
            remote_cidr_block = remote_vpc.cidr_block
        else:
            raise ValueError("You must either provide an aws account_id or aws profile")
        # Resource option for these resources
        this_resource_option = pulumi.ResourceOptions(parent=self)
        this_account_id = aws.get_caller_identity(opts=this_resource_option).account_id

        if remote_account_id == this_account_id and region == conf.get("region"):
            same_account_peering = True

        if not peering_accepter:
            peering_connection = aws.ec2.VpcPeeringConnection(
                f"{peering_vpc_name}-peering-connection",

                )
            )


