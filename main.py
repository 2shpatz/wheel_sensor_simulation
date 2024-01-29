from flask import Flask, jsonify

import time
import sensors.wheel_sensor as wheel_sensor
from data_server.data_server import DataServer
import asyncio

app = Flask(__name__)

async def main():
    wheel_sensor.simulate_sensors()
    data_server = DataServer()

    @app.route('/wheel/status', methods=['GET'])
    async def get_data():
        # Asynchronously fetch data from the data server
        data = await data_server.get_all_sensors()
        return jsonify(data)
    loop = asyncio.get_event_loop()
    
    app.run(debug=True, port=5001)
        
if __name__ == '__main__':
    asyncio.run(main())


   
# TBD protobuf, configuration file, 