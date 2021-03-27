import setuptools


with open("README.md") as fp:
    long_description = fp.read()


setuptools.setup(
    name="my_vote_app",
    version="0.0.1",
    description="Slurm student AWS stack deployment with CDK Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Victor Mikhaylov <victor.v.mikhayloc@gmail.com>",
    # package_dir={"": "voting_deploy"},
    # packages=setuptools.find_packages(where="voting_deploy"),
    install_requires=[
        "aws-cdk.core==1.95.1",
        "aws-cdk.aws-dynamodb==1.95.1",
        "aws-cdk.aws-lambda==1.95.1",
        "aws-cdk.aws-apigateway==1.95.1",
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
