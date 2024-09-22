#!/bin/bash
current_dir=$(dirname "$(realpath "$0")")
cd $current_dir
root_dir=$(dirname "$current_dir")
echo --- Running testing.sh ---
nix-shell shell.testing.nix --run "./test.sh"
if [ $? -ne 0 ]; then
    echo --- ERROR - testing.sh exited with a non-zero exit code, aborting
    exit 1
fi
echo --- Entering root environment ---
echo --- Generating stos startup script for systemd ---
sudo tee /etc/bin/stos-bootstrap > /dev/null << EOF
#!/bin/bash
cd $root_dir
/nix/var/nix/profiles/default/bin/nix-shell $current_dir --run 'python3 main.py'
EOF
sudo chmod +x /etc/bin/stos-bootstrap
echo --- Updating service configuration ---
sudo cp ./stos.service /etc/systemd/system/stos.service
echo --- Starting stos.service ---
sudo systemctl daemon-reload
sudo systemctl restart stos
sleep 1
echo --- Done, showing service status ---
sudo systemctl status stos
