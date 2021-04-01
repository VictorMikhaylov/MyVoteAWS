import setuptools

__version__ = "0.0.1"

with open("README.md", "r") as fp:
    long_description = fp.read()


setuptools.setup(
    name="my_vote_app",
    version=__version__,
    description="Slurm student AWS stack deployment with CDK Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Victor Mikhaylov <victor.v.mikhayloc@gmail.com>",
    install_requires=[
        "aws-cdk.core==1.96.0",
        "aws-cdk.aws-dynamodb==1.96.0",
        "aws-cdk.aws-sns==1.96.0",
        "aws-cdk.aws-sqs==1.96.0",
        "aws-cdk.aws-lambda==1.96.0",
        "aws-cdk.aws-lambda-event-sources==1.96.0",
        "aws-cdk.aws-lambda-destinations==1.96.0",
        "aws-cdk.aws-apigatewayv2==1.96.0",
        "aws-cdk.aws-apigatewayv2_integrations==1.96.0",
        "boto3",
        "requests",
    ],
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Utilities",
        "Typing :: Typed",
    ],
)
