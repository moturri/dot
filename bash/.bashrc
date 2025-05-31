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

shopt -s autocd cdspell cmdhist dotglob histappend expand_aliases checkwinsize

eval "$(starship init bash)"

function cht() {
	curl -s "https://cht.sh/$1"
}

eval "$(zoxide init bash)"

alias reload='source ~/.bashrc'
alias cat='bat --paging=never --style=numbers,changes,grid'
alias man='man -P "bat --style=numbers --color=always --wrap=never"'
