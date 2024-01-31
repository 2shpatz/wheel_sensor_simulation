
import logging
import sensors.wheel_sensor as wheel_sensor
from data_server.data_server import DataApi
import asyncio


async def main():
    wheel_sensor.simulate_sensors()
    data_server = DataApi(port=5000)
    try:
        await data_server.start_server()
    except (KeyboardInterrupt, asyncio.exceptions.CancelledError) as err:
        logging.warning("data_server was terminated by the user: %s", err)
        
if __name__ == '__main__':
    asyncio.run(main())
