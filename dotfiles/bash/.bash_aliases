
alias count='find . -type f | wc -l'
alias cpv='rsync -ah --info=progress2'
alias egrep='egrep --color=auto'
alias fgrep='fgrep --color=auto'
alias gh='history|grep'
alias grep='grep --color=auto'
alias l='ls -CF'
alias la='ls -A'
alias ll='ls -alF'
alias lt='ls --human-readable --size -1 -S --classify'
alias ls="ls -Glah"
alias pip-i='pip install -r requirements.txt'
alias va='source ./.venv/bin/activate'
alias ve='python3 -m venv ./.venv'
alias code-server="/tmp/code-server/bin/code-server"

function cl() {
    DIR="$*";
        # if no DIR given, go home
        if [ $# -lt 1 ]; then
                DIR=$HOME;
    fi;
    builtin cd "${DIR}" && \
    # use your preferred ls command
        ls -F --color=auto
}
