#!/bin/bash

echo "Creating symlink to bash folder in home directory."
cp -R ./bash/. $HOME/

. $HOME/.bashrc

if test /tmp/code-server/bin/code-server; then
    # Visual Studio Code :: Package list
    pkglist=(aaron-bond.better-comments alexcvzz.vscode-sqlite batisteo.vscode-django DavidAnson.vscode-markdownlint dbaeumer.vscode-eslint
        donjayamanne.githistory DotJoshJohnson.xml eamodio.gitlens ecmel.vscode-html-css esbenp.prettier-vscode felipecaputo.git-project-manager
        foxundermoon.shell-format GitHub.vscode-pull-request-github GrapeCity.gc-excelviewer rogalmic.bash-debug mads-hartmann.bash-ide-vscode
        mechatroner.rainbow-csv KevinRose.vsc-python-indent donjayamanne.python-environment-manager donjayamanne.python-extension-pack ms-python.black-formatter
        ms-python.isort ms-python.mypy-type-checker ms-python.pylint ms-python.python ms-toolsai.jupyter-keymap ms-vscode.cpptools-themes ms-vscode.live-server
        ms-vscode.test-adapter-converter hbenl.vscode-test-explorer redhat.vscode-yaml timonwong.shellcheck vscode-icons-team.vscode-icons wholroyd.jinja
        yzhang.markdown-all-in-one Zignd.html-css-class-completion ms-python.python donjayamanne.githistory eamodio.gitlens github.github-vscode-theme oderwat.indent-rainbow
        christian-kohler.path-intellisense mhutchie.git-graph Gruntfuggly.todo-tree github.vscode-pull-request-github marp-team.marp-vscode shuworks.vscode-table-formatter
        njpwerner.autodocstring
    )

    for i in ${pkglist[@]}; do
        /tmp/code-server/bin/code-server --install-extension $i
    done

fi

echo "Add Settings code-server"
cp ./settings.json $HOME/.local/share/code-server/User
