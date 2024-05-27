# Smart-Inventory-Tracking
IoT-based Smart Inventory Tracking using Raspberry Pi

1. Download darknet and build
```
git clone https://github.com/AlexeyAB/darknet
cd darknet
make
```

2. Save yolov4-tiny-custom.cfg and yolov4-tiny-custom_best.weights

3. Run the model using following command in terminal
```
./darknet detector test path/to/obj.data path/to/yolov4-tiny-custom.cfg path/to/yolov4-tiny-custom_best.weights path/to/image.jpg
```

3. Output

![alt text](https://raw.githubusercontent.com/josephbinoy/Smart-Inventory-Tracking/main/results/download.png)
