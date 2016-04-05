[![](https://cloud.githubusercontent.com/assets/1317406/12406044/32cd9916-be0f-11e5-9b18-1547f284f878.png)](http://www.synapse-wireless.com/)

# SNAPconnect Example - Echo Test Simple Throughput Benchmark

This example application asks a node to echo back a number of strings in order to test the total packet throughput.

## Running This Example

In order to run this example, you will need to make sure that SNAPconnect is installed on your system:

```bash
pip install --extra-index-url https://update.synapse-wireless.com/pypi snapconnect
```
    
You will also need to make a few modifications to EchoTest.py to configure your bridge address,
serial type, and serial port. Some of the values that you can change include:

```python
BRIDGE_NODE = "\x4B\x42\x34"
SERIAL_TYPE = snap.SERIAL_TYPE_RS232
SERIAL_PORT = 0 # COM1
```

You can even set the number of queries to perform by changing the `NUMBER_OF_QUERIES` value:

```python
NUMBER_OF_QUERIES = 100 # More polls == longer test
```

Once you have configured the example, simply run:

```bash
python EchoTest.py
```

If SNAPconnect was installed and everything was configured correctly, the specified number of queries will be made,
incoming responses will be counted, and the final results will be displayed:

```
$ python EchoTest.py
Initiating test sequence
100 queries, 100 responses in 7946 milliseconds
```

For more details, refer to source file [EchoTest.py](EchoTest.py).

## License

Copyright © 2016 [Synapse Wireless](http://www.synapse-wireless.com/), licensed under the [Apache License v2.0](LICENSE.md).

<!-- meta-tags: vvv-snapconnect, vvv-python, vvv-example -->
