" Install vim-plug if not already installed:
" curl -fLo ~/.vim/autoload/plug.vim --create-dirs \
"     https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim
call plug#begin('~/.vim/plugged')

Plug 'preservim/nerdtree'
Plug 'tpope/vim-fugitive'
Plug 'airblade/vim-gitgutter'
Plug 'preservim/nerdcommenter'
Plug 'ryanoasis/vim-devicons'
Plug 'vim-airline/vim-airline'
Plug 'vim-airline/vim-airline-themes'
Plug 'prabirshrestha/vim-lsp'
Plug 'mattn/vim-lsp-settings'
Plug 'prabirshrestha/asyncomplete.vim'
Plug 'prabirshrestha/asyncomplete-lsp.vim'
Plug 'prabirshrestha/asyncomplete-buffer.vim'

call plug#end()

let mapleader = " "
set number
set relativenumber
set scrolloff=8
set sidescrolloff=8
set mouse=a
set wrap
set cmdheight=2
set showmatch
set colorcolumn=80
set foldcolumn=1
set showtabline=2
set laststatus=2
set termguicolors
set background=dark
set updatetime=300
syntax enable
filetype plugin indent on

set hlsearch
set incsearch
set ignorecase
set smartcase

set completeopt=menuone,noinsert,noselect,preview
set shortmess+=c
set pumheight=8

set tabstop=4
set shiftwidth=4
set expandtab
set autoindent
set smartindent

set foldenable
set foldmethod=indent
set foldlevelstart=4

set undofile
set undodir=~/.vim/undo//
set clipboard+=unnamedplus

nnoremap <C-h> <C-w>h
nnoremap <C-j> <C-w>j
nnoremap <C-k> <C-w>k
nnoremap <C-l> <C-w>l

nnoremap <C-s> :w<CR>
nnoremap <C-q> :q<CR>
nnoremap <leader>bn :bnext<CR>
nnoremap <leader>bp :bprev<CR>
nnoremap <leader>bd :bdelete<CR>

nnoremap <leader>e :NERDTreeToggle<CR>
nnoremap <leader>f :NERDTreeFind<CR>
let NERDTreeShowHidden=1
let NERDTreeMinimalUI=1
let NERDTreeDirArrows=1

nnoremap <leader>gs :G<CR>

if has("nvim") || has("terminal")
  tnoremap <Esc> <C-\><C-n>
endif

let g:lsp_diagnostics_echo_cursor = 1
let g:lsp_diagnostics_virtual_text_enabled = 1
let g:lsp_diagnostics_signs_enabled = 1
let g:lsp_settings = {
      \ 'pyright': {},
      \ 'bash-language-server': {},
      \ 'lua-language-server': {},
      \ }

let g:asyncomplete_auto_popup = 1
let g:asyncomplete_remove_duplicates = 1

inoremap <expr> <Tab> pumvisible() ? "\<C-n>" : "\<Tab>"
inoremap <expr> <S-Tab> pumvisible() ? "\<C-p>" : "\<S-Tab>"

let g:airline_powerline_fonts = 1
let g:airline_highlighting_cache = 1
let g:airline#extensions#tabline#enabled = 1
let g:airline_theme = 'dark'

augroup remember_cursor
  autocmd!
  autocmd BufReadPost * if line("'\"") > 1 && line("'\"") <= line("$") |
        \ execute "normal! g`\"" |
        \ endif
augroup END

highlight FoldColumn guibg=#000000 guifg=#5f5f5f
highlight SignColumn guibg=#000000
