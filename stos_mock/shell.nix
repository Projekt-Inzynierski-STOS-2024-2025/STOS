let
  nixpkgs = fetchTarball "https://github.com/NixOS/nixpkgs/tarball/nixos-24.05";
  pkgs = import nixpkgs { config = {}; overlays = []; };
in

pkgs.mkShellNoCC {
  packages = [
    (pkgs.python312.withPackages (python-pkgs: [
      python-pkgs.python-dotenv
      python-pkgs.flask
    ]))
    pkgs.sqlite
  ];
}
