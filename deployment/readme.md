# STOS server deployment configuration

The deployment process is largely automated via [deploy script](./deploy.sh). To run fresh deploy or update the server, run:
```sh
./deployment/deploy.sh
```
## Prerequisites
_System:_
- linux
- systemd
- user called `stos`
- directory `/home/stos`, owned by the `stos` user
_Packages:_
- [docker](https://www.docker.com/)
- [nix-shell](https://nixos.org/), part of `nix` package manager

## Deployment breakdown
1. Firstly, the necessary healthchecks are performed, checking for existence of 3 things:
    - network connectivity (with the Internet)
    - nix-shell
    - docker
If any of those are missing on your system, make sure to install the necessary packages (`nix` and `docker`, respectively)
2. Pytest is run checking for any errors in testing. If tests fail, the entire deployment does too.
3. A bootstrap script is generated, automatically resolving all necessary paths to the components of the service
4. Systemd service entry is copied to `/etc/systemd/system/stos.service`
5. `stos.service` is run and its status displayed in the end
