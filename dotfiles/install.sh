#!/bin/bash
############################
# This script creates symlinks from the home directory to any desired dotfiles in ~/dotfiles
############################
cd dotfiles/ || exit

echo "Creating symlink to bash folder in home directory."
cp -R ./bash/. "$HOME"/

# shellcheck source=/dev/null
source "$HOME/.bashrc"

echo "update"
sudo apt-get -qq update

echo "install -y python3 python3-venv python3-pip"
sudo apt-get -qq install -y python3 python3-venv python3-pip

echo "upgrade pip"
pip install -q --upgrade pip

# Visual Studio Code :: Package list
pkglist=(
    aaron-bond.better-comments
    alexcvzz.vscode-sqlite
    batisteo.vscode-django
    DavidAnson.vscode-markdownlint
    dbaeumer.vscode-eslint
    DotJoshJohnson.xml
    ecmel.vscode-html-css
    esbenp.prettier-vscode
    felipecaputo.git-project-manager
    foxundermoon.shell-format
    GrapeCity.gc-excelviewer
    rogalmic.bash-debug
    mads-hartmann.bash-ide-vscode
    mechatroner.rainbow-csv
    KevinRose.vsc-python-indent
    donjayamanne.python-environment-manager
    donjayamanne.python-extension-pack
    ms-python.black-formatter
    ms-python.isort
    ms-python.mypy-type-checker
    ms-python.pylint
    ms-python.python
    ms-vscode.live-server
    hbenl.vscode-test-explorer
    redhat.vscode-yaml
    timonwong.shellcheck
    vscode-icons-team.vscode-icons
    wholroyd.jinja
    yzhang.markdown-all-in-one
    Zignd.html-css-class-completion
    donjayamanne.githistory
    eamodio.gitlens
    github.github-vscode-theme
    oderwat.indent-rainbow
    christian-kohler.path-intellisense
    marp-team.marp-vscode
    shuworks.vscode-table-formatter
    njpwerner.autodocstring
    Name: Git Graph
    mhutchie.git-graph
    donjayamanne.githistory
    eamodio.gitlens
)

if test /tmp/code-server/bin/code-server; then
    for i in "${pkglist[@]}"; do
        echo "Install extension $i "
        /tmp/code-server/bin/code-server --install-extension "$i" > /dev/null
    done
fi

echo "Add Settings code-server"
cp ./settings.json "$HOME/.local/share/code-server/User"
