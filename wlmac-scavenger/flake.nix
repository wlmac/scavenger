{
  description = "Ephemeral SAC Scavenger Hunt website by Project Metropolis";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-23.11";

  outputs = { self, nixpkgs }:
    let
      supportedSystems = [ "x86_64-linux" "x86_64-darwin" "aarch64-linux" "aarch64-darwin" ];
      forAllSystems = nixpkgs.lib.genAttrs supportedSystems;
      pkgs = forAllSystems (system: nixpkgs.legacyPackages.${system});
    in
    {
      devShells = forAllSystems (system: {
        default = pkgs.${system}.mkShellNoCC {
          packages = with pkgs.${system}; [
            poetry
            (python311.withPackages (pp: with pp; [
              black
              isort
              mypy
              types-requests
              django-stubs
            ]))
            gettext
          ];
        };
      });
    };
}
