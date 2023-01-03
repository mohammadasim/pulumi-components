from typing import Dict, List, Optional, Sequence

import pulumi
import pulumi_aws as aws
from _inputs import RdsSecurityGroupIngressArgs
from pulumi import ComponentResource


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
            "pulumi-components:aws:components:rds-security-group",
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
            ),
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
            "pulumi-components:aws:components:rds-subnet-group", name, {}, opts
        )
        if not subnet_ids:
            raise ValueError["subnet ids are required"]
        self.subnet_group = aws.rds.SubnetGroup(
            f"{name}-subnet-group",
            subnet_ids=subnet_ids,
            opts=pulumi.ResourceOptions(parent=self),
        )
        self.register_outputs({"subnet_group": self.subnet_group})


class RDSInstance(ComponentResource):
    """A class defining an RDS instance custom resource"""

    def __init__(
        self,
        name: str,
        allocated_storage: str,
        instance_class: str,
        engine: str,
        engine_version: str,
        family: str,
        identifier: str,
        password: str,
        vpc_id: str,
        parameters: Sequence[Dict],
        *,
        allow_major_version_upgrade: bool = False,
        apply_immediately: bool = False,
        auto_minor_version_upgrade: bool = False,
        backup_retention_period: int = 14,
        backup_window: str = "03:00-05:00",
        blue_green_update: aws.rds.InstanceBlueGreenUpdateArgs = None,
        ca_cert_identifier: str = None,
        character_set_name: str = "utf8",
        copy_tags_to_snapshot: bool = True,
        custom_iam_instance_profile: str = None,
        customer_owned_ip_enabled: bool = False,
        db_name: str = None,
        delete_automated_backups: bool = True,
        deletion_protection: bool = True,
        domain: str = None,
        domain_iam_role_name: str = None,
        enabled_cloudwatch_logs_exports: Sequence[str] = [],
        final_snapshot_identifier: str = "",
        iam_database_authentication_enabled: bool = False,
        kms_key_id: str = None,
        maintenance_window: str = "sun:01:00-sun:03:00",
        max_allocated_storage: int = 100,
        monitoring_interval: int = 0,
        monitoring_role_arn: str = None,
        multi_az: bool = False,
        performance_insights_enabled: bool = False,
        performance_insights_kms_key_id: str = None,
        performance_insights_retention_period: int = 7,
        publicly_accessible: bool = False,
        skip_final_snapshot: bool = True,
        storage_encrypted: bool = False,
        tags=None,
        subnet_ids: List[str] = [],
        additional_vpc_security_group_ids: Optional[List[str]] = [],
        ingress_security_group_cidrs: Optional[
            pulumi.Input[Sequence[str]]
        ] = None,  # noqa E501
        ingress_security_group_ids: Optional[
            pulumi.Input[Sequence[str]]
        ] = None,  # noqa E501
        opts: Optional[pulumi.ResourceOptions] = None,
        **kwargs,
    ):
        super().__init__(
            "pulumi-components:aws:components:rdsInstance", name, {}, opts
        )  # noqa E501
        if tags is None:
            tags = {}
        self.security_group = RdsSecurityGroup(
            name,
            engine,
            vpc_id,
            ingress_security_group_cidrs=ingress_security_group_cidrs,
            ingress_security_group_ids=ingress_security_group_ids,
        )
        self.security_group_ids = additional_vpc_security_group_ids.append(
            self.security_group.id
        )
        self.subnet_group = RdsSubnetGroup(name, subnet_ids)
        rds_parameter_group_args = []
        for parameter in parameters:
            rds_parameter_group_args.append(
                aws.rds.ParameterGroupParameterArgs(
                    name=parameter["name"],
                    value=parameter["value"],
                    apply_method=parameter["apply_method"]
                    if "apply_method" in parameter
                    else "pending-reboot",
                )
            )
        self.parameter_group = aws.rds.ParameterGroup(
            f"{name}-parameter-group",
            description=f"Parameter group for {name} rds instance",
            family=family,
            parameters=rds_parameter_group_args,
        )
        self.rds_instance = aws.rds.Instance(
            name,
            args=aws.rds.InstanceArgs(
                allocated_storage=allocated_storage,
                instance_class=instance_class,
                engine=engine,
                engine_version=engine_version,
                identifier=identifier,
                password=password,
                allow_major_version_upgrade=allow_major_version_upgrade,
                apply_immediately=apply_immediately,
                auto_minor_version_upgrade=auto_minor_version_upgrade,
                backup_retention_period=backup_retention_period,
                backup_window=backup_window,
                blue_green_update=blue_green_update,
                ca_cert_identifier=ca_cert_identifier,
                character_set_name=character_set_name,
                copy_tags_to_snapshot=copy_tags_to_snapshot,
                custom_iam_instance_profile=custom_iam_instance_profile,
                customer_owned_ip_enabled=customer_owned_ip_enabled,
                db_name=db_name,
                delete_automated_backups=delete_automated_backups,
                deletion_protection=deletion_protection,
                domain=domain,
                domain_iam_role_name=domain_iam_role_name,
                enabled_cloudwatch_logs_exports=enabled_cloudwatch_logs_exports,  # noqa E501
                final_snapshot_identifier=final_snapshot_identifier,
                iam_database_authentication_enabled=iam_database_authentication_enabled,  # noqa E501
                kms_key_id=kms_key_id,
                maintenance_window=maintenance_window,
                max_allocated_storage=max_allocated_storage,
                monitoring_interval=monitoring_interval,
                monitoring_role_arn=monitoring_role_arn,
                multi_az=multi_az,
                performance_insights_enabled=performance_insights_enabled,
                performance_insights_kms_key_id=performance_insights_kms_key_id,  # noqa E501
                performance_insights_retention_period=performance_insights_retention_period,  # noqa E501
                publicly_accessible=publicly_accessible,
                skip_final_snapshot=skip_final_snapshot,
                storage_encrypted=storage_encrypted,
                db_subnet_group_name=self.subnet_group.name,
                vpc_security_group_ids=self.security_group_ids,
                parameter_group_name=self.parameter_group,
                tags=tags,
                opts=pulumi.ResourceOptions(parent=self),
            ),
        )
        self.register_outputs(
            {
                "instance": self.rds_instance,
                "parameter_group": self.parameter_group,
                "subnet_group": self.subnet_group,
                "security_group": self.security_group,
            }
        )
