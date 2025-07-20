#!/bin/bash
#
# ~/.bashrc
#

# If not running interactively, don't do anything
[[ $- != *i* ]] && return

alias grep='grep --color=auto'
PS1='[\u@\h \W]\$ '

# --- Custom additions from .zshrc and improvements ---

# Export common environment variables
export TERMINAL=kitty
export EDITOR=nvim
export VISUAL=nvim

# Aliases for common commands
# Check if bat is installed before aliasing cat
if command -v bat &>/dev/null; then
	alias cat="bat --paging=never --style=full"
fi

# Check if eza is installed before aliasing ls and lta
if command -v eza &>/dev/null; then
	alias ls="eza --icons=always" # Overrides existing ls alias
	alias vi="nvim"
	alias lta="eza -lTag --icons"
	alias lta2="eza -lTag --level=2 --icons"
	alias lta3="eza -lTag --level=3 --icons"
	alias ll="eza -l --icons"
	alias la="eza -la --icons"
fi

# Functions
cht() {
	curl -s "https://cht.sh/$1"
}

tldrr() {
	local cmd
	cmd=$(tldr --list |
		fzf --height=80% \
			--reverse \
			--preview='tldr --color always {}' \
			--preview-window=right:80%:wrap)

	if [[ -n $cmd ]]; then
		tldr "$cmd"
		printf "\n[Enter]\n"
		read -r
	fi
}

yayfz() {
	local selected_pkg
	selected_pkg=$(
		yay -Slq 2>/dev/null |
			fzf --height=80% \
				--reverse \
				--preview='yay -Si {} 2>/dev/null || yay -Qi {} 2>/dev/null' \
				--preview-window=right:80%:wrap
	)

	if [[ -n $selected_pkg ]]; then
		yay -Si "$selected_pkg" 2>/dev/null || yay -Qi "$selected_pkg" 2>/dev/null
		printf "\n[Enter]\n"
		read -r
	fi
}

# --- Git Aliases ---
alias g="git"
alias ga="git add"
alias gaa="git add ."
alias gau="git add -u"
alias gc="git commit -v"
alias gca="git commit -v -a"
alias gco="git checkout"
alias gd="git diff"
alias gds="git diff --staged"
alias gl="git log --oneline --decorate --graph --all"
alias gp="git push"
alias gpl="git pull"
alias gs="git status -sb"
alias gb="git branch"
alias gba="git branch -a"
alias gr="git remote -v"
alias grh="git reset --hard"
alias grs="git restore --staged"
alias gcl="git clean -fd"
alias gst="git stash"
alias gsta="git stash apply"
alias gstd="git stash drop"
alias gstl="git stash list"
alias gsts="git stash save"

# --- Archive/Unarchive Shortcuts ---
# Create a tar.gz archive
mkcdgz() { mkdir -p "$1" && cd "$1" && tar -czvf "$1".tar.gz "$@"; }
# Extract various archives
extract() {
	if [ -f "$1" ]; then
		case "$1" in
		*.tar.bz2) tar xvjf "$1" ;;
		*.tar.gz) tar xvzf "$1" ;;
		*.bz2) bunzip2 "$1" ;;
		*.rar) unrar x "$1" ;;
		*.gz) gunzip "$1" ;;
		*.tar) tar xvf "$1" ;;
		*.tbz2) tar xvjf "$1" ;;
		*.tgz) tar xvzf "$1" ;;
		*.zip) unzip "$1" ;;
		*.Z) uncompress "$1" ;;
		*.7z) 7za x "$1" ;;
		*) echo "don't know how to extract '$1'..." ;;
		esac
	else
		echo "'$1' is not a valid file!"
	fi
}

# --- History and Completion Settings ---
HISTCONTROL=ignoreboth:erasedups
HISTSIZE=5000
HISTFILESIZE=10000
shopt -s histappend # Append to the history file, don't overwrite it
# Save and reload the history after each command
PROMPT_COMMAND="history -n; history -w; history -c; history -r; $PROMPT_COMMAND"

# Fish-like history search with Ctrl+R (fzf is already sourced)
bind '"\C-r": "\C-e\C-u \C-r"'

# Enable programmable completion features (if available)
# shellcheck disable=SC1091
if ! shopt -oq posix; then
	if [ -f /usr/share/bash-completion/bash_completion ]; then
		. /usr/share/bash-completion/bash_completion
	elif [ -f /etc/bash_completion ]; then
		. /etc/bash_completion
	fi
fi

# --- Starship and fzf setup ---

# Starship prompt
# shellcheck disable=SC2034,SC1091
if command -v starship &>/dev/null; then
	eval "$(starship init bash)"
fi

# fzf key-bindings and completion
# shellcheck disable=SC1090
if [ -f ~/.fzf.bash ]; then
	source ~/.fzf.bash
fi
