function install_dependencies
{
    sudo apt-get update -y
    sudo apt-get install -y python3-pip
    pip3 install python-can flask
}

function configure_virtual_can_channel
{
    # load kernel modules
    modprobe can
    modprobe can_raw
    modprobe can_bcm

    # create virtual interface
    sudo ip link add dev vcan0 type vcan
    sudo ip link set up vcan0
}

function main
{
    install_dependencies
    configure_virtual_can_channel
    python3 main.py
}

main "$@"