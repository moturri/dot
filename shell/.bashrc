#!/bin/bash

# If not running interactively, don't do anything
[[ $- != *i* ]] && return

alias grep='grep --color=auto'
PS1='[\u@\h \W]\$ '

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

export LIBVA_DRIVER_NAME=iHD
export LIBVA_DRIVERS_PATH=/usr/lib/dri

# [[ -f ~/.bash-preexec.sh ]] && source ~/.bash-preexec.sh
eval "$(atuin init bash)"
