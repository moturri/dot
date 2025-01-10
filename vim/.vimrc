let mapleader = " "

set number
set relativenumber
set scrolloff=8
set sidescrolloff=8
set mouse=a
set wrap
set undofile
set tabstop=4
set shiftwidth=4
set expandtab
set smartindent
set autoindent
set hlsearch
set incsearch
set ignorecase
set smartcase
set cmdheight=2
set termguicolors
set showmatch
set timeoutlen=300
set laststatus=2
set background=dark
set completeopt=menuone,noinsert,noselect,preview
set shortmess+=c
set pumheight=8
set colorcolumn=80
"set clipboard+=unnamedplus
set foldenable
set foldmethod=manual
set foldlevelstart=1
set foldcolumn=1
set showtabline=2

let NERDTreeShowHidden=1

let g:airline_powerline_fonts = 1
let g:airline_highlighting_cache = 1
let g:airline#extensions#tabline#enabled = 1
"let g:airline#extensions#tabline#formatter = 'default'

nnoremap <Leader>c ggVG"+y
nnoremap <C-p> :FZF<CR>
nnoremap <C-s> :w<CR>
nnoremap <C-q> :q<CR>
nnoremap <C-n> :NERDTreeToggle<CR>
"nnoremap <F5> :UndotreeToggle<CR>


filetype plugin indent on
syntax enable

