{ pkgs ? import <nixpkgs> { } }:
let
  pythonPkgs = pythonPkgs: with pythonPkgs; [
    setuptools
    pip
    black
  ];
  pythonWithPkgs = pkgs.python3.withPackages pythonPkgs;
in
  pkgs.mkShell {
    packages = [ pythonWithPkgs ];
  }
