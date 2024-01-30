from flask import Flask, jsonify

import time
import sensors.wheel_sensor as wheel_sensor
from data_server.data_server import DataServer
import asyncio

app = Flask(__name__)

async def main():
    wheel_sensor.simulate_sensors()
    data_server = DataServer()
    task = asyncio.create_task(data_server.start_listen_to_data())
    data_server.start_api_server()
    await task
        
if __name__ == '__main__':
    asyncio.run(main())


   
# TBD protobuf, configuration file, 