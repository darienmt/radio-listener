def select_device_index(pyAudio, input_device=True):
    device_indexes = []
    device_info_by_index = {}
    
    audio_devices_count = pyAudio.get_device_count()
    print()
    print("Select input device:")
    for i in range(audio_devices_count):
        device_info = pyAudio.get_device_info_by_index(i)
        if input_device: 
            max_input_channels = device_info.get("maxInputChannels")
            if max_input_channels == 0:
                continue
        else:
            max_output_channels = device_info.get("maxOutputChannels")
            if max_output_channels == 0:
                continue
        device_index = device_info.get("index")
        name = device_info.get("name")
        
        print(f"{device_index} - {name}")
        device_indexes.append(device_index)
        device_info_by_index[device_index] = device_info
    
    selected_device_index = None
    while selected_device_index is None:
        device = input("Enter device index or x to exit: ")
        if device.lower() == "x":
            break
        try:
            selected_device_index = int(device)
        except ValueError:
            print("Invalid input. Please enter an integer")
            continue
        
        if selected_device_index not in device_indexes:
            print(f"The selected device index {selected_device_index} is not in {device_indexes}")
            selected_device_index = None
    
    return device_info_by_index.get(selected_device_index)