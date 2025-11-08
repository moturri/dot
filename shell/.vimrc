set nocompatible
filetype plugin indent on
syntax on
set encoding=utf-8
set hidden

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

let mapleader = " "

set tabstop=4
set shiftwidth=4
set expandtab
set autoindent
set smartindent

set hlsearch
set incsearch
set ignorecase
set smartcase

set completeopt=menuone,noinsert,noselect,preview
set shortmess+=c
set pumheight=8

if has("persistent_undo")
    if !isdirectory(expand("~/.vim/undo"))
        call mkdir(expand("~/.vim/undo"), "p")
    endif
    set undodir=~/.vim/undo
    set undofile
endif
set clipboard+=unnamedplus

set cursorline
hi Normal guibg=#000000 guifg=#ffffff
hi LineNr guibg=#000000 guifg=#00ff00
hi CursorLine guibg=#111111
hi CursorLineNr guibg=#111111 guifg=#00ff00
hi SignColumn guibg=#000000
hi FoldColumn guibg=#000000 guifg=#5f5f5f

hi GitGutterAdd guifg=#00ff00 guibg=#000000
hi GitGutterChange guifg=#ffff00 guibg=#000000
hi GitGutterDelete guifg=#ff0000 guibg=#000000

augroup remember_cursor
    autocmd!
    autocmd BufReadPost *
                \ if line("'\"") > 1 && line("'\"") <= line("$") |
                \   exe "normal! g`\"" |
                \ endif
augroup END

packadd minpac
call minpac#init()

" Core plugins
call minpac#add('preservim/nerdtree')
call minpac#add('tpope/vim-fugitive')
call minpac#add('airblade/vim-gitgutter')
call minpac#add('preservim/nerdcommenter')
call minpac#add('ryanoasis/vim-devicons')
call minpac#add('sheerun/vim-polyglot')
call minpac#add('itchyny/lightline.vim')
call minpac#add('prabirshrestha/vim-lsp')
call minpac#add('mattn/vim-lsp-settings')
call minpac#add('prabirshrestha/asyncomplete.vim')
call minpac#add('prabirshrestha/asyncomplete-lsp.vim')
call minpac#add('prabirshrestha/asyncomplete-buffer.vim')

command! PackUpdate call minpac#update()
command! PackClean call minpac#clean()

nnoremap <leader>e :NERDTreeToggle<CR>
nnoremap <leader>f :NERDTreeFind<CR>
let NERDTreeShowHidden=1
let NERDTreeMinimalUI=1
let NERDTreeDirArrows=1

nnoremap <leader>gs :G<CR>

nnoremap <C-h> <C-w>h
nnoremap <C-j> <C-w>j
nnoremap <C-k> <C-w>k
nnoremap <C-l> <C-w>l

nnoremap <C-s> :w<CR>
nnoremap <C-q> :q<CR>
nnoremap <leader>bn :bnext<CR>
nnoremap <leader>bp :bprev<CR>
nnoremap <leader>bd :bdelete<CR>

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
inoremap <expr> <cr> pumvisible() ? asyncomplete#close_popup() : "\<cr>"

let g:lightline = {
      \ 'colorscheme': 'one',
      \ 'active': {'left': [ ['mode', 'paste'], ['readonly', 'filename', 'modified']]},
      \ 'component_function': {}
      \ }

if has("nvim") || has("terminal")
  tnoremap <Esc> <C-\><C-n>
endif

augroup modern_init
    autocmd!
    autocmd BufWritePre * %s/\s\+$//e
augroup END
