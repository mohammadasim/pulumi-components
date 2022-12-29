from typing import Sequence, Optional

import pulumi
from pulumi import ComponentResource


class RDSCommonAttrs:
    """A class defining common rds attributes"""

    def __init__(self,
                 family: str,
                 engine: str,
                 engine_version: str,
                 master_password: str,
                 vpc_id: str,
                 subnet_ids: pulumi.Input[Sequence[str]],
                 additional_security_group_ids: Optional[pulumi.Input[Sequence[str]]] = [],
                 ingress_security_group_cidrs: Optional[pulumi.Input[Sequence[str]]] = None,
                 ingress_security_group_ids: Optional[pulumi.Input[str]] = None,
                 backup_retention_period: int = 14,
                 maintenance_window: str = "sun:01:00-sun:03:00",
                 backup_window: str = "03:00-05:00",
                 db_name: str = ''
                 ):
        self.family = family
        self.engine = engine
        self.engine_version = engine_version
        self.master_password = master_password
        self.vpc_id = vpc_id
        self.subnet_ids = subnet_ids
        self.additional_security_group_ids = additional_security_group_ids
        self.ingress_security_group_cidrs = ingress_security_group_cidrs
        self.ingress_security_group_ids = ingress_security_group_ids
        self.backup_retention_period = backup_retention_period
        self.maintenance_window = maintenance_window
        self.backup_window = backup_window
        self.db_name = db_name


class RDSInstance(ComponentResource, RDSCommonAttrs):
    """A class defining an RDS instance custom resource"""
    def __init__(self,
                 allocated_storage: str,
                 instance_class: str,
                 allow_major_version_upgrade: bool = False,
                 apply_immediately: bool = False,
                 auto_minor_version_upgrade: bool = False,
                 ):