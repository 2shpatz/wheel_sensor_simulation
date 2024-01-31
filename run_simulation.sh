function install_dependencies
{
    sudo apt-get update -y
    sudo apt-get install -y python3-pip
    pip3 install python-can flask
}

function configure_virtual_can_channel
{
    virtual_can_interface="vcan0"
    if ip link show dev "$virtual_can_interface" &> /dev/null; then
        echo "Interface $virtual_can_interface exists."
    else
        echo "creating Interface $virtual_can_interface..."
    
        # load kernel modules
        modprobe can
        modprobe can_raw
        modprobe can_bcm

        # create virtual interface
        sudo ip link add dev vcan0 type vcan
        sudo ip link set up vcan0
    fi
}

function main
{
    install_dependencies
    configure_virtual_can_channel
    python3 main.py
}

main "$@"