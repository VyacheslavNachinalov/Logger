import asyncio
import serial
import time
from csv import writer
from threading import Thread


async def task(ser):
    while True:
        if ser.in_waiting:
            output = ser.readline().decode('ASCII').strip()
            if ser.port == '/dev/ttyUSB2':
                ser_name = 'Stepper:'
            elif ser.port == '/dev/ttyUSB1':
                ser_name = 'Laser:'
            elif ser.port == '/dev/ttyUSB0':
                ser_name = 'RS-485:'
            await csv_write(ser_name, output)
            print(ser_name, output)
        await asyncio.sleep(0)


async def csv_write(ser_port, output):
    named_tuple = time.localtime()
    time_string = time.strftime("%m/%d/%Y, %H:%M:%S", named_tuple)
    list_data = [time_string, ser_port, output]
    with open('file.csv', 'a', newline='') as f_object:
        writer_object = writer(f_object)
        writer_object.writerow(list_data)
        f_object.close()


ser1 = serial.Serial('/dev/ttyUSB0', 115200, timeout=0, write_timeout=0)
ser2 = serial.Serial('/dev/ttyUSB1', 9600, timeout=0)
ser3 = serial.Serial('/dev/ttyUSB2', 9600, timeout=0)


async def rs_485_write(ser):
    while True:
        data = input()+'\r\n'
        ser.write(data.encode('ASCII'))


def reading_from_PORTS(ser1, ser2, ser3):
    ioloop = asyncio.new_event_loop()
    asyncio.set_event_loop(ioloop)
    tasks = [
        ioloop.create_task(task(ser1)),
        ioloop.create_task(task(ser2)),
        ioloop.create_task(task(ser3))
    ]
    wait_tasks = asyncio.wait(tasks)
    ioloop.run_until_complete(wait_tasks)
    ioloop.close()


def writing_in_PORTS(ser1):
    ioloop = asyncio.new_event_loop()
    asyncio.set_event_loop(ioloop)
    task = [ioloop.create_task(rs_485_write(ser1))
    ]
    wait_tasks = asyncio.wait(task)
    ioloop.run_until_complete(wait_tasks)
    ioloop.close()

ioloop = asyncio.get_event_loop()

t1 = Thread(target=reading_from_PORTS, args=[ser1, ser2, ser3])
t2 = Thread(target=writing_in_PORTS, args=[ser1])

t1.start()
t2.start()

t1.join()
t2.join()

