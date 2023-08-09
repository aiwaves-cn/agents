# Start your trial

## pip

1. install package

    ```shell
    pip install -i http://47.96.122.196:9999/simple agent --trusted-host 47.96.122.196
    ```

2. import it in your file

    ```python
    import agents
    ```

## your own server

1. package sourcecode

    ```shell
    python setup.py sdist
    ```

2. install twine

    ```shell
    pip install twine
    ```

3. upload

    ```shell
    twine upload --repository-url http://host:port --username <username> --password <password> dist/*
    ```

4. install
