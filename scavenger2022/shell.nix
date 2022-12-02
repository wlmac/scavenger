{ pkgs ? import <nixpkgs> { } }:
let
  pythonPkgs = pythonPkgs: with pythonPkgs; [
    setuptools
    pip
    black
    virtualenv
    mypy
    python-lsp-server
    python-lsp-black
  ];
  pythonWithPkgs = pkgs.python3.withPackages pythonPkgs;
in
  pkgs.mkShell {
    packages = [ pkgs.docker pythonWithPkgs ];

    shellHook = ''
      export PIP_PREFIX=$(pwd)/.build/pip_packages
      export PYTHONPATH="$PIP_PREFIX/${pkgs.python3.sitePackages}:$PYTHONPATH"
      export PATH="$PIP_PREFIX/bin:$PATH"
      unset SOURCE_DATE_EPOCH
      python3 -m pip install virtualenv
      python3 -m venv .build/venv
      source .build/venv/bin/activate
      python3 -m pip install pipenv
      pipenv install --skip-lock
    '';
  }
