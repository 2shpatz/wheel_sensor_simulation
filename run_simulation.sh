function install_dependencies
{
    sudo apt-get update -y
    sudo apt-get install -y python3-pip
    pip install python-can flask
}

function configure_virtual_can_channel
{
    
}

function main
{
    install_dependencies
}

main "$@"