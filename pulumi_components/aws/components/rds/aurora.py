from typing import Dict, List, Optional, Sequence

import pulumi
import pulumi_aws as aws
from pulumi import ComponentResource, ResourceOptions

from .common import RdsSecurityGroup


class AuroraCluster(ComponentResource):
    """A class defining an Aurora cluster custom resource"""

    def __init__(
        self,
        name: str,
        cluster_parameters: Sequence[Dict],
        db_parameters: Sequence[str],
        family: pulumi.Input[str],
        engine: str,
        engine_version: pulumi.Input[str],
        master_password: str,
        subnet_ids: Sequence[pulumi.Input[str]],
        vpc_id: str,
        availability_zones: Sequence[pulumi.Input[str]],
        instances: Sequence[Dict],
        database_name: Optional[str],
        *,
        master_username: Optional[str] = "admin",
        additional_security_group_ids: List[pulumi.Input[str]] = [],
        ingress_security_group_cidrs: Sequence[pulumi.Input[str]] = None,
        ingress_security_group_ids: Sequence[pulumi.Input[str]] = None,
        engine_mode: Optional[str] = "provisioned",
        backtrack_window: Optional[int] = 0,
        backup_retention_period: Optional[int] = 14,
        copy_tags_to_snapshots: bool = True,
        preferred_backup_window: str = "03:00-05:00",
        preferred_maintenance_window: str = "sun:01:00-sun:03:00",
        allow_major_version_upgrade: bool = False,
        apply_immediately: bool = False,
        tags: Optional[Dict[str, str]] = {},
        skip_final_snapshot: bool = True,
        opts: Optional[ResourceOptions] = None,
        **kwargs,
    ) -> None:
        super().__init__(
            "pulumi-components:aws:components:aurora-cluster", name, {}, opts
        )
        # Create cluster security group
        self.security_group = RdsSecurityGroup(
            name=name,
            db_engine=engine,
            vpc_id=vpc_id,
            ingress_security_group_cidrs=ingress_security_group_cidrs,
            ingress_security_group_ids=ingress_security_group_ids,
        )
        self.security_group_ids = additional_security_group_ids.append(
            self.security_group.id
        )
        # Create cluster parameter group
        cluster_parameter_group_args = [
            aws.rds.ParameterGroupParameterArgs(
                name=param["name"],
                value=param["value"],
                apply_method=param["apply_method"]
                if "apply_method" in param
                else "pending-reboot",
            )
            for param in cluster_parameters
        ]
        self.cluster_parameter_group = aws.rds.ClusterParameterGroup(
            (rsc_name := f"{name}-cluster-parameter-group"),
            name=f"{rsc_name}-{family}",
            family=family,
            parameters=cluster_parameter_group_args,
            opts=pulumi.ResourceOptions(parent=self),
        )
        # Create db paramter group
        db_parameter_group_args = [
            aws.rds.ParameterGroupParameterArgs(
                name=param["name"],
                value=param["value"],
                apply_method=param["apply_method"]
                if "apply_method" in param
                else "pending-reboot",
            )
            for param in db_parameters
        ]
        self.db_parameter_group = aws.rds.ParameterGroup(
            (rsc_name := f"{name}-db-parameter-group"),
            name=f"{rsc_name}-{family}",
            family=family,
            parameters=[db_parameter_group_args],
            opts=pulumi.ResourceOptions(parent=self),
        )
