{
  description = "Ephemeral SAC Scavenger Hunt website by Project Metropolis";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-22.11";
  #inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";

  outputs = { self, nixpkgs }:
    let
      supportedSystems = [ "x86_64-linux" "x86_64-darwin" "aarch64-linux" "aarch64-darwin" ];
      forAllSystems = nixpkgs.lib.genAttrs supportedSystems;
      pkgs = forAllSystems (system: nixpkgs.legacyPackages.${system});
      projectDir = self + /scavenger2022;
    in
    {
      packages = forAllSystems (system: {
        default = pkgs.${system}.poetry2nix.mkPoetryApplication { inherit projectDir; };
      });

      devShells = forAllSystems (system: {
        default = pkgs.${system}.mkShellNoCC {
          packages = with pkgs.${system}; [
            (poetry2nix.mkPoetryEnv {
              inherit projectDir;
            })
            (python310.withPackages (pp: with pp; [
              poetry
              black
              isort
              mypy
              types-requests
              django-stubs
            ]))
          ];
        };
      });
    };
}
