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
        vpc_peering: Optional[Sequence[VpcPeeringArgs]] = None,
        ha_nat: bool = True,
        enable_dns_hostname: bool = True,
        enable_dns_support: bool = True,
        instance_tenancy: str = "default",
        protected_eip: bool = False,
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
        # Create VPC peering
        self.vpc_peering_routes = []
        if vpc_peering:
            for peering in vpc_peering:
                peering_details = self._create_peering(
                    peering.accepter,
                    peering.name,
                    peering.vpc_id,
                    peering.aws_profile,
                    peering.account_id,
                    peering.cidr,
                )
                self.vpc_peering_routes.append(peering_details.get("vpc_routes"))

        # Create public subnets
        self.public_subnets = []
        self.public_subnet_ids = []
        self.pubic_route_table = (
            self._create_rout_tables(
                "public-rt",
                [
                    aws.ec2.RouteTableRouteArgs(
                        cidr_block="0.0.0.0/0", gateway_id=self.igw.id
                    )
                ]
                * self.vpc_peering_routes,
            ),
        )
        opts = pulumi.ResourceOptions(parent=self.vpc)
        for subnet in public_subnets:
            pass

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
        same_account_peering = False
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
                skip_metadata_api_check=False,
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
                opts=remote_resource_option,
            )
            remote_cidr_block = remote_vpc.cidr_block
        else:
            raise ValueError("You must either provide an aws account_id or aws profile")
        # Resource option for these resources
        this_resource_option = pulumi.ResourceOptions(parent=self)
        this_account_id = aws.get_caller_identity(opts=this_resource_option).account_id

        if remote_account_id == this_account_id and region == conf.get("region"):
            same_account_peering = True

        # If we are requesting the peering connection
        if not peering_accepter:
            peering_connection = aws.ec2.VpcPeeringConnection(
                f"{peering_vpc_name}-peering-connection",
                auto_accept=same_account_peering,
                peer_vpc_id=peering_vpc_id,
                vpc_id=self.vpc.id,
                peer_owner_id=remote_account_id,
                peer_region=None if same_account_peering else region,
                tags=self.vpc.tags_all.apply(
                    lambda x: {
                        "Name": f"[{x['Name']}] <-> [{peering_vpc_name}]",
                        "Side": "Local" if same_account_peering else "Requester",
                    }
                ),
                opts=this_resource_option,
            )
        else:
            # If we are not the requester, but accepter and the peering is not
            # in the same aws account
            if not same_account_peering:
                # We need to first get the peering connection
                remote_peering_connection = aws.ec2.get_vpc_peering_connection_output(
                    peer_vpc_id=peering_vpc_id,
                    vpc_id=self.vpc.id,
                    opts=remote_invoke_option,
                )
                # Create vpc peering accepter connection
                peering_connection = aws.ec2.VpcPeeringConnectionAccepter(
                    f"{peering_vpc_name}-peering-accepter-connection",
                    vpc_peering_connection_id=remote_peering_connection.id,
                    auto_accept=True,
                    tags=self.vpc.tags_all.apply(
                        lambda x: {
                            "Name": f"[{x['Name']}] <-> [{peering_vpc_name}]",
                            "Side": "Accepter",
                        }
                    ),
                    opts=this_resource_option,
                )
            else:
                # If we are accepter and the peering
                # is in the same aws account.
                # we simply retrieve the peering connection
                peering_connection = aws.ec2.get_vpc_peering_connection_output(
                    peer_vpc_id=self.vpc.id, vpc_id=peering_vpc_id
                )

                # Create vpc routes
                routes = aws.ec2.RouteTableRouteArgs(
                    cidr_block=peering_cidr,
                    vpc_peering_connection_id=peering_connection.id,
                )
                return {
                    "peering_vpc": remote_vpc,
                    "connection": peering_connection,
                    "vpc_routes": routes,
                    "peering_cidr": remote_cidr_block,
                }

    def _create_rout_tables(
        self,
        name: str,
        routes: Sequence[aws.ec2.RouteTableRouteArgs],
        opts: pulumi.ResourceOptions = None,
    ) -> aws.ec2.RouteTable:
        """Creates and returns a route table resource with given parameters"""
        return aws.ec2.RouteTable(name, vpc_id=self.vpc.id, routes=routes, opts=opts)

    def _create_subnet(
        self,
        subnet_cidr: str,
        zone: str,
        route_table: aws.ec2.RouteTable,
        private: bool,
        label: str,
        tags: Mapping[str, str] = None,
    ) -> aws.ec2.Subnet:
        """Creates subnet and associate it with the provided route table.
        Returns the subnet resource with given parameters"""
        subnet = aws.ec2.Subnet(
            f"{zone}-{label}-subnet",
            vpc_id=self.vpc.id,
            availability_zone=zone,
            cidr_block=subnet_cidr,
            assign_ipv6_address_on_creation=False,
            map_public_ip_on_launch=not private,
            tags=tags,
            opts=pulumi.ResourceOptions(parent=self.vpc),
        )
        aws.ec2.RouteTableAssociation(
            f"{zone}-{label}-subnet-associate",
            route_table_id=route_table.id,
            subnet_id=subnet.id,
            opts=pulumi.ResourceOptions(parent=route_table),
        )
        return subnet
