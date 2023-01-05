from typing import Dict, List, Optional, Sequence

import pulumi
import pulumi_aws as aws
from pulumi import ComponentResource, ResourceOptions

from .common import RdsSecurityGroup, RdsSubnetGroup


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
        skip_final_snapshot: bool = False,
        storage_encrypted: bool = True,
        deletion_protection: bool = True,
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
            parameters=db_parameter_group_args,
            opts=pulumi.ResourceOptions(parent=self),
        )

        # Create subnet group
        self.subnet_group = RdsSubnetGroup(name, subnet_ids)

        # Create the cluster
        self.cluster = aws.rds.Cluster(
            (cluster_name := f"{name}-cluster"),
            cluster_identifier=cluster_name,
            availability_zones=availability_zones,
            db_cluster_parameter_group_name=self.cluster_parameter_group.name,
            db_subnet_group_name=self.subnet_group.subnet_group.name,
            engine=engine,
            engine_mode=engine_mode,
            engine_version=engine_version,
            master_password=master_password,
            master_username=master_username,
            storage_encrypted=storage_encrypted,
            vpc_security_group_ids=self.security_group_ids,
            skip_final_snapshot=skip_final_snapshot,
            final_snapshot_identifier=f"{rsc_name}-final-snapshot",
            preferred_backup_window=preferred_backup_window,
            preferred_maintenance_window=preferred_maintenance_window,
            backtrack_window=backtrack_window,
            backup_retention_period=backup_retention_period,
            copy_tags_to_snapshot=copy_tags_to_snapshots,
            deletion_protection=deletion_protection,
            allow_major_version_upgrade=allow_major_version_upgrade,
            apply_immediately=apply_immediately,
            tags=tags,
            opts=pulumi.ResourceOptions(parent=self),
        )

        self.instances = [
            aws.rds.ClusterInstance(
                (rsc_name := f"{name}-instance-{i}"),
                apply_immediately=apply_immediately,
                cluster_identifier=self.cluster.id,
                copy_tags_to_snapshot=copy_tags_to_snapshots,
                db_parameter_group_name=self.db_parameter_group.name,
                db_subnet_group_name=self.subnet_group.subnet_group.name,
                engine=engine,
                engine_version=engine_version,
                identifier=f"{rsc_name}",
                instance_class=instances[i].get("instance_class"),
                preferred_backup_window=preferred_backup_window,
                preferred_maintenance_window=preferred_maintenance_window,
                tags=tags,
                opts=pulumi.ResourceOptions(parent=self.cluster),
            )
            for i in range(len(instances))
        ]
        self.register_outputs(
            {
                "cluster": self.cluster,
                "instances": self.instances,
                "cluster_parameter_group": self.cluster_parameter_group,
                "db_parameter_group": self.db_parameter_group,
                "security_group": self.security_group,
                "subnet_group": self.subnet_group,
            }
        )
