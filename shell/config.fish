#!/usr/bin/fish

# Environment Variables
set -x TERMINAL kitty
set -x EDITOR nvim
set -x VISUAL nvim

# Starship Prompt
if type -q starship
  starship init fish | source
end

# Aliases for common commands
# bat for cat
if type -q bat
  alias cat "bat --paging=never --style=full"
end

# eza for ls and other listing commands
if type -q eza
  alias ls "eza --icons=always"
  alias ll "eza -l --icons"
  alias la "eza -la --icons"
  alias lta "eza -lTag --icons"
  alias lta2 "eza -lTag --level=2 --icons"
  alias lta3 "eza -lTag --level=3 --icons"
end

# Git Aliases (Fish functions are used for aliases)
abbr g git
abbr ga "git add"
abbr gaa "git add ."
abbr gau "git add -u"
abbr gc "git commit -v"
abbr gca "git commit -v -a"
abbr gco "git checkout"
abbr gd "git diff"
abbr gds "git diff --staged"
abbr gl "git log --oneline --decorate --graph --all"
abbr gp "git push"
abbr gpl "git pull"
abbr gs "git status -sb"
abbr gb "git branch"
abbr gba "git branch -a"
abbr gr "git remote -v"
abbr grh "git reset --hard"
abbr grs "git restore --staged"
abbr gcl "git clean -fd"
abbr gst "git stash"
abbr gsta "git stash apply"
abbr gstd "git stash drop"
abbr gstl "git stash list"
abbr gsts "git stash save"

# Functions
function cht
    curl -s "https://cht.sh/$argv"
end

function tldrr
  if type -q fzf
    set cmd (tldr --list | fzf --height=80% --reverse --preview='tldr --color always {}' --preview-window=right:80%:wrap)
    if test -n "$cmd"
      tldr "$cmd"
      printf "\n[Enter]\n"
      read -l
    end
  else
    echo "fzf is not installed. Please install fzf for tldrr to work."
  end
end

function yayfz
  if type -q fzf
    set selected_pkg (yay -Slq 2>/dev/null | fzf --height=80% --reverse --preview='yay -Si {} 2>/dev/null || yay -Qi {} 2>/dev/null' --preview-window=right:80%:wrap)
    if test -n "$selected_pkg"
      yay -Si "$selected_pkg" 2>/dev/null || yay -Qi "$selected_pkg" 2>/dev/null
      printf "\n[Enter]\n"
      read -l
    end
  else
    echo "fzf is not installed. Please install fzf for yayfz to work."
  end
end

# Archive/Unarchive Shortcuts
function mkcdgz
  mkdir -p "$argv[1]"
  cd "$argv[1]"
  tar -czvf "$argv[1]".tar.gz $argv[2..-1]
end

function extract
  if test -f "$argv[1]"
    switch "$argv[1]"
      case '*.tar.bz2'
        tar xvjf "$argv[1]"
      case '*.tar.gz'
        tar xvzf "$argv[1]"
      case '*.bz2'
        bunzip2 "$argv[1]"
      case '*.rar'
        unrar x "$argv[1]"
      case '*.gz'
        gunzip "$argv[1]"
      case '*.tar'
        tar xvf "$argv[1]"
      case '*.tbz2'
        tar xvjf "$argv[1]"
      case '*.tgz'
        tar xvzf "$argv[1]"
      case '*.zip'
        unzip "$argv[1]"
      case '*.Z'
        uncompress "$argv[1]"
      case '*.7z'
        7za x "$argv[1]"
      case '*'
        echo "don't know how to extract '$argv[1]'..."
    end
  else
    echo "'$argv[1]' is not a valid file!"
  end
end

# fzf key bindings for history search (Ctrl+R)
function fish_user_key_bindings
  if type -q fzf
    bind \cr 'fzf_history --reverse --exact --query=(commandline)'
  end
end
