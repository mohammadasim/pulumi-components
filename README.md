# pulumi-components
This library defines pulumi custom resources for different AWS services. By using these custom resources you configure the specific AWS service along with its associated resources as an instance of a single class.

For example, using the `Vpc` class you are able to configure all the `vpc` resources i-e `NAT Gateways, Private Subnets, Public Subnets etc`. 

Examples demonstrating how this library can be used, is provided [here](https://github.com/mohammadasim/pulumi-components-examples)

This library is still work in progress, hence it is not currently hosted anywhere. You can however, use it in development mode. Simply clone the repo and run the following steps.

Install it from the local folder (editable mode):

- Enter your pulumi project folder
- Launch `poetry run pip install -e <local path to pulumi-components>`

Now all the changes made to the lib will be visible instantly when doing `pulumi up` on a project

This library will tag all your resources at run time. To use this feature simply define your tags in your stack's yaml file. Use the [example repo](https://github.com/mohammadasim/pulumi-components-examples/blob/9ca724abdac784c2313dfcf0972f9f9633b0c9a5/examples/rds-instance/Pulumi.rds-instance-example.dev.yaml#L19) as a guide. Then import `from pulumi_components.aws.utils import register_tags` invoke this function at the top of your `__main__.py` file. The tags defined in your stack's yaml file will be added to all the taggable resources.