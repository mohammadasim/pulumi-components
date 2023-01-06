from typing import Mapping, Optional, Sequence

import pulumi


@pulumi.input_type
class RoleMappingArgs:
    """A class mapping IAM roles to users and groups in kubernetes"""

    groups: pulumi.Input[Sequence[pulumi.Input[str]]] = pulumi.property(
        "groups"
    )  # noqa E501
    role_arn: pulumi.Input[str] = pulumi.property("role_arn")
    user_name: pulumi.Input[str] = pulumi.property("user_name")


@pulumi.input_type
class UserMappingArgs:
    """A class mapping AWS users to users and groups in Kubernetes"""

    groups: pulumi.Input[Sequence[pulumi.Input[str]]] = pulumi.property(
        "groups"
    )  # noqa E501
    user_arn: pulumi.Input[str] = pulumi.property("user_arn")
    user_name: pulumi.Input[str] = pulumi.property("user_name")


@pulumi.input_type
class KubeConfigOptionArgs:
    """A class defining options for kubeconfig. It maps an IAM profile
    with an IAM role"""

    def __init__(
        self,
        *,
        profile_name: Optional[pulumi.Input[str]],
        role_arn: Optional[pulumi.Input[str]]
    ) -> None:
        if profile_name:
            pulumi.set(self, "profile_name", profile_name)
        if role_arn:
            pulumi.set(self, "role_arn", role_arn)

    @property
    @pulumi.getter(name="profile_name")
    def profile_name(self) -> Optional[pulumi.Input[str]]:
        """AWS profile name to use instead of default.
        Profile is passed to kubeconfig as enviornment variable"""
        ...

    @property
    @pulumi.getter(name="role_arn")
    def role_arn(self) -> Optional[pulumi.Input[str]]:
        """The ARN of the rule to be assumed"""
        ...


@property
@pulumi.input_type
class ClusterNodeGroupVolumeOptionArgs:
    """A class defining options for a kubernetes volume in a node group"""

    volume_size: pulumi.Input[int] = pulumi.property("volume_size")
    delete_on_termination: pulumi.Input[str] = pulumi.property(
        "delete_on_termination"
    )  # noqa E501
    iops: pulumi.Input[int] = pulumi.property("iops")
    volume_type: pulumi.Input[str] = pulumi.property("volume_type")


@property
@pulumi.input_type
class ClusterNodeGroupOptionArgs:
    """A class defining options for a node group"""

    def __init__(
        self,
        name: str,
        instance_types: Sequence[pulumi.Input[str]],
        capacity_type: pulumi.Input[str],
        max_pods: pulumi.Input[int],
        max_size: pulumi.Input[int],
        desired_size: pulumi.Input[int],
        volume_size: pulumi.Input[int],
        volume: Optional[ClusterNodeGroupVolumeOptionArgs],
        availability_zones: Sequence[pulumi.Input[str]],
        max_unavailable_percentage: Optional[pulumi.Input[int]],
        security_group_ids: Optional[pulumi.Input[str]],
        labels: Optional[pulumi.Input[Mapping[str, str]]] = None,
        taints: Optional[pulumi.Input[Sequence[Mapping[str, str]]]] = None,
    ) -> None:
        pulumi.set(self, "name", name)
        pulumi.set(self, "instance_types", instance_types)
        pulumi.set(self, "capacity_type", capacity_type)
        pulumi.set(self, "max_pods", max_pods)
        pulumi.set(self, "max_size", max_size)
        pulumi.set(self, "desired_size", desired_size)
        pulumi.set(self, "volume_size", volume_size)
        pulumi.set(self, "volume", volume)
        pulumi.set(self, "availability_zones", availability_zones)
        pulumi.set(
            self, "max_unavailable_percentage", max_unavailable_percentage
        )  # noqa E501
        pulumi.set(self, "security_group_ids", security_group_ids)
        if labels:
            pulumi.set(self, "labels", labels)
        if taints:
            pulumi.set(self, "taints", taints)

    @property
    @pulumi.getter(name="name")
    def name(self) -> pulumi.Input[str]:
        """The name of the Node Group"""
        ...

    @property
    @pulumi.getter(name="instance_types")
    def instance_types(self) -> Sequence[pulumi.Input[str]]:
        """Instance types in the Node Group"""
        ...

    @property
    @pulumi.getter(name="capacity_type")
    def capacity_type(self) -> pulumi.Input[str]:
        """The capacity type of the Node Group"""
        ...

    @property
    @pulumi.getter(name="max_pods")
    def max_pods(self) -> pulumi.Input[int]:
        """The maximum number of pods running on a node"""
        ...

    @property
    @pulumi.getter(name="max_size")
    def max_size(self) -> pulumi.Input[int]:
        """The maximum number of worker nodes in a Node Group"""
        ...

    @property
    @pulumi.getter(name="desired_size")
    def desired_size(self) -> pulumi.Input[int]:
        """The desired number of worker nodes running in a Node group"""
        ...

    @property
    @pulumi.getter(name="volume_size")
    def volume_size(self) -> pulumi.Input[int]:
        """The size of volume attached to nodes in the Node Group"""
        ...

    @property
    @pulumi.getter(name="volume")
    def volume(self) -> Optional[ClusterNodeGroupVolumeOptionArgs]:
        """An instance of volume attached to nodes in the Node group"""
        ...

    @property
    @pulumi.getter(name="availability_zones")
    def availability_zones(self) -> Sequence[pulumi.Input[str]]:
        """The list of availability zones the
        node group creates workers nodes in"""
        ...

    @property
    @pulumi.getter(name="max_unavailable_percentage")
    def max_unavailable_percentage(self) -> Optional[pulumi.Input[int]]:
        """The max percentage of worker nodes in a Node Group"""
        ...

    @property
    @pulumi.getter(name="security_group_ids")
    def security_group_ids(self) -> Optional[pulumi.Input[str]]:
        """The list of security group ids associated with the Node Group"""
        ...

    @property
    @pulumi.getter(name="labels")
    def labels(self) -> Optional[pulumi.Input[Mapping[str, str]]]:
        """Custom labels that needs to be added to the Node Group"""
        ...

    @property
    @pulumi.getter(name="taints")
    def taints(self) -> Optional[pulumi.Input[Sequence[Mapping[str, str]]]]:
        """Custom taints that need to be added to the Node Group"""
        ...


@pulumi.input_type
class CNIAddonArgs:
    """A Class containg options for Kubernetes CNI plugin option"""

    kubeconfig: pulumi.Input[str] = pulumi.property("kubeconfig")
    version: pulumi.Input[str] = pulumi.property("version")
    role_arn: pulumi.Input[str] = pulumi.property("role_arn")
    env_vars: pulumi.Input[Mapping[str, str]] = pulumi.property("env_vars")


@pulumi.input_type
class KubeProxyAddonArgs:
    """A Class containing options for Kubernetes proxy addon"""

    kubeconfig: pulumi.Input[str] = pulumi.property("kubeconfig")
    version: pulumi.Input[str] = pulumi.property("version")


@pulumi.input_type
class CoreDNSAddonArgs:
    kubeconfig: pulumi.Input[str] = pulumi.property("kubeconfig")
    version: pulumi.Input[str] = pulumi.property("version")
