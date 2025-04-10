#
# ~/.bashrc
#

# If not running interactively, don't do anything
[[ $- != *i* ]] && return

alias ls='ls --color=auto'
alias grep='grep --color=auto'
PS1='[\u@\h \W]\$ '

export TERMINAL="wezterm"
export EDITOR="nvim"


# Bash settings
shopt -s autocd cdspell cmdhist dotglob histappend expand_aliases checkwinsize

# Starship prompt
eval "$(starship init bash)"

# Define your functions
function cheat() {
    curl -s "https://cheat.sh/$1"
}

# FZF integration
if [ -f ~/.fzf.bash ]; then
    source ~/.fzf.bash
fi


# Setup fzf
# ---------
# Add fzf to the PATH if it's not already there
if [[ ! "$PATH" == *"/home/m/.fzf/bin"* ]]; then
  export PATH="${PATH:+$PATH:}/home/m/.fzf/bin"
fi

if command -v fzf &> /dev/null; then
  eval "$(fzf --bash)"
fi

export FZF_DEFAULT_OPTS='--height 60% --reverse --border'
bind -x '"\C-p": _fzf_man_search'

_fzf_man_search() {
    local command
    command=$(compgen -c | fzf --height 60% --reverse --no-sort --prompt 'Man Pages > ' \
        --preview 'man {} | col -b | less -R' \
        --preview-window=left:80%:wrap)

    if [ -n "$command" ]; then
        # Display the selected man page using less
        man "$command" | less
    fi
}


eval "$(zoxide init bash)"
zox() {
    local dir
    dir=$(zoxide query -l | fzf --height 40% --reverse --inline-info) || return
    cd "$dir" || return
}


alias reload='source ~/.bashrc'
alias cat='bat --paging=never --style=numbers,changes,grid'
alias man='man -P "bat --style=numbers --color=always --wrap=never"'
alias fastfetch='fastfetch --config ~/.config/fastfetch/config.json'
alias sayonara='firejail --appimage /home/m/Applications/Sayonara.AppImage'
alias cider='firejail --profile=/etc/firejail/cider.profile --appimage /home/m/Applications/Cider.AppImage'
alias libreoffice='/home/m/Applications/LibreOffice.AppImage'
alias xterm='wezterm'


