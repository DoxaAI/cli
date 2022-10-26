from setuptools import setup

setup(
    name="doxa-cli",
    version="1.0",
    py_modules=["login","upload"],
    include_package_data=True,
    install_requires=["click", "termcolor"],
    entry_points="""
        [console_scripts]
        login=login:login
        user=login:user
        logout=login:out
        upload=upload:upload
    """,
)