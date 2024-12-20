#!/bin/bash
current_dir=$(dirname "$(realpath "$0")")
cd $current_dir
root_dir=$(dirname "$current_dir")
ns=$(which nix-shell)
echo --- Updating nixpkgs
nix-channel --add https://nixos.org/channels/nixpkgs-unstable
nix-channel --update
echo --- Running healthcheck.sh 
/bin/bash healthcheck.sh
if [ $? -ne 0 ]; then
    echo --- ERROR - healthcheck failed, exiting
    exit 1
fi
echo --- System healthy 
echo --- Running testing.sh 
nix-shell shell.testing.nix --run "./test.sh"
if [ $? -ne 0 ]; then
    echo --- ERROR - testing.sh exited with a non-zero exit code, aborting
    exit 1
fi
echo --- Checks successful, preparing for deployment
echo ----- Stopping existing containers
docker ps -a -q | xargs docker stop
echo ------ Entering root environment 
echo ------ Removing some nix directories which break the system for some reason
sudo rm -rf /tmp/env-vars
echo --- Generating stos startup script for systemd 
sudo touch /usr/bin/stos-bootstrap
sudo tee /usr/bin/stos-bootstrap > /dev/null << EOF
#!/bin/bash
cd $root_dir
$ns $current_dir/shell.nix --run 'filebeat -c ./deployment/filebeat.yml' &
$ns $current_dir/shell.nix --run 'python3 main.py' >> /home/stos/stos.log &
wait
EOF
sudo chmod +x /usr/bin/stos-bootstrap
echo --- Updating service configuration 
sudo cp ./stos.service /etc/systemd/system/stos.service
echo --- Starting stos.service 
sudo systemctl daemon-reload
sudo systemctl restart stos
sleep 1
echo --- Done, showing service status 
sudo systemctl status stos
