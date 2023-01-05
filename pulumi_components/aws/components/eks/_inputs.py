from typing import Optional, Sequence

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
    volume_size: pulumi.Input[int] = pulumi.property("volume_size")
    delete_on_termination: pulumi.Input[str] = pulumi.property(
        "delete_on_termination"
    )  # noqa E501
    iops: pulumi.Input[int] = pulumi.property("iops")
    volume_type: pulumi.Input[str] = pulumi.property("volume_type")
