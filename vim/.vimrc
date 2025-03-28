let mapleader = " "

set number
set relativenumber
set scrolloff=8
set sidescrolloff=8
set mouse=a
set wrap
set undofile
set hlsearch
set incsearch
set ignorecase
set smartcase
set cmdheight=2
set termguicolors
set background=dark
set completeopt=menuone,noinsert,noselect,preview
set shortmess+=c
set pumheight=8
set colorcolumn=80
set foldenable
set foldmethod=manual
set foldlevelstart=1
set foldcolumn=1
set showtabline=2

set tabstop=4
set shiftwidth=4
set expandtab
set smartindent
set autoindent

set laststatus=2
set showmatch
set timeoutlen=300

let NERDTreeShowHidden=1

let g:airline_powerline_fonts = 1
let g:airline_highlighting_cache = 1
let g:airline#extensions#tabline#enabled = 1

nnoremap <Leader>c ggVG"+y
nnoremap <C-p> :FZF<CR>
nnoremap <C-s> :w<CR>
nnoremap <C-q> :q<CR>
nnoremap <C-n> :NERDTreeToggle<CR>
" nnoremap <F5> :UndotreeToggle<CR>  " Uncomment to toggle Undotree

filetype plugin indent on
syntax enable

"set backup          " Enable backup files
"set backupdir=~/.vim/backup// " Set backup directory
"set directory=~/.vim/swap//    " Set swap file directory
set undodir=~/.vim/undo//
set clipboard+=unnamedplus

highlight Comment cterm=italic gui=italic
highlight Identifier cterm=bold gui=bold
highlight Statement cterm=bold gui=bold

