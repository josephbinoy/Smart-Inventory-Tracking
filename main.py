import asyncio
import json
import os
import subprocess
from azure.iot.device.aio import ProvisioningDeviceClient, IoTHubDeviceClient
from picamera_module import capture_image

# Azure IoT Central device credentials
DEVICE_ID = "1ms21is047"
ID_SCOPE = "0ne0t34tggs0C606C3"
PRIMARY_KEY = "cUgx+H7vz4Yan2x9RnGRfgegeJiK9+ehBl0XswtX96eWWoO8="

def run_yolo_model(image_path):
    # Save the current directory
    current_dir = os.getcwd()

    try:
        # Change directory to darknet
        os.chdir('./darknet')

        # Construct the command
        command = (
            './darknet detector test data/obj.data yolov4-tiny-custom.cfg '
            'yolov4-tiny-custom_best.weights ../image.jpg 2>/dev/null | '
            'grep -E "../image.jpg|%" > result.txt'
        )

        # Run the command
        subprocess.run(command, shell=True, check=True)
    finally:
        # Change back to the parent directory
        os.chdir(current_dir)

def parse_result(result_file='./darknet/result.txt'):
    detections = {'bournvita': 0, 'electronics': 0, 'tropicana_mango_juice': 0}

    with open(result_file, 'r') as file:
        lines = file.readlines()
        for line in lines:
            if 'bournvita:' in line:
                detections['bournvita'] += 1
            elif 'electronics:' in line:
                detections['electronics'] += 1
            elif 'tropicana mango juice:' in line:
                detections['tropicana_mango_juice'] += 1

    return detections

async def connect_to_azure():
    provisioning_host = "global.azure-devices-provisioning.net"
    provisioning_device_client = ProvisioningDeviceClient.create_from_symmetric_key(
        provisioning_host=provisioning_host,
        registration_id=DEVICE_ID,
        id_scope=ID_SCOPE,
        symmetric_key=PRIMARY_KEY
    )

    registration_result = await provisioning_device_client.register()

    if registration_result.status == "assigned":
        device_client = IoTHubDeviceClient.create_from_symmetric_key(
            symmetric_key=PRIMARY_KEY,
            hostname=registration_result.registration_state.assigned_hub,
            device_id=DEVICE_ID
        )
        await device_client.connect()
        print("Connected to Azure IoT Central.")
        return device_client
    else:
        print(f"Failed to register device: {registration_result.status}")
        return None

async def send_to_iot_central(device_client, message):
    try:
        await device_client.send_message(message)
        print("Message successfully sent to IoT Central.")
    except Exception as e:
        print(f"Failed to send message: {str(e)}")

async def main():
    try:
        # Connect to Azure IoT Central
        device_client = await connect_to_azure()

        if device_client:            
            while True:
                # Wait for user input to start
                input("Press Enter to update Azure IoT Central...")

                # Capture image
                print("Capturing image...")
                capture_image()

                # Run YOLO model and parse results
                image_path = 'image.jpg'
                print("Running YOLO model...")
                run_yolo_model(image_path)
                print("Parsing results...")
                detections = parse_result()

                # Create message payload
                payload = json.dumps(detections)
                
                # Send message to IoT Central
                print("Sending data to IoT Central...")
                await send_to_iot_central(device_client, payload)
        else:
            print("Failed to connect to Azure IoT Central.")

    except KeyboardInterrupt:
        print("Exiting...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if device_client:
            await device_client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())