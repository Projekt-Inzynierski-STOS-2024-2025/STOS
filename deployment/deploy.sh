#!/bin/bash
current_dir=$(dirname "$(realpath "$0")")
cd $current_dir
root_dir=$(dirname "$current_dir")
ns=$(which nix-shell)
echo --- Running testing.sh ---
nix-shell shell.testing.nix --run "./test.sh"
if [ $? -ne 0 ]; then
    echo --- ERROR - testing.sh exited with a non-zero exit code, aborting
    exit 1
fi
echo --- Entering root environment ---
echo --- Generating stos startup script for systemd ---
sudo touch /usr/bin/stos-bootstrap
sudo tee /usr/bin/stos-bootstrap > /dev/null << EOF
#!/bin/bash
cd $root_dir
$ns $current_dir/shell.nix --run 'filebeat -c ./deployment/filebeat.yml' &
$ns $current_dir/shell.nix --run 'python3 main.py' >> /home/stos/stos.log &
wait
EOF
sudo chmod +x /usr/bin/stos-bootstrap
echo --- Updating service configuration ---
sudo cp ./stos.service /etc/systemd/system/stos.service
echo --- Starting stos.service ---
sudo systemctl daemon-reload
sudo systemctl restart stos
sleep 1
echo --- Done, showing service status ---
sudo systemctl status stos
