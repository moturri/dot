" Basic Leader Key
let mapleader = " "

" UI Settings
set number                  " Show absolute line numbers
set relativenumber          " Show relative numbers
set scrolloff=8            " Keep 8 lines visible above/below cursor
set sidescrolloff=8        " Horizontal scroll padding
set mouse=a                " Enable mouse support
set wrap                   " Wrap long lines
set cmdheight=1            " Minimal command line height
set showmatch              " Highlight matching brackets
set colorcolumn=80         " Vertical line at 80 chars
set foldcolumn=1           " Show fold column
set showtabline=2          " Always show tabline
set laststatus=2           " Always show status line
set termguicolors          " Enable 24-bit colors
set background=dark        " Dark theme background
set updatetime=300         " Faster swap file write and CursorHold

" Search Settings
set hlsearch               " Highlight search matches
set incsearch              " Incremental search
set ignorecase             " Case insensitive search...
set smartcase              " ...unless uppercase used

" Completion & Messages
set completeopt=menuone,noinsert,noselect,preview
set shortmess+=c
set pumheight=8            " Popup menu height

" Indentation
set tabstop=4
set shiftwidth=4
set expandtab              " Use spaces instead of tabs
set autoindent
set smartindent

" Folding
set foldenable
set foldmethod=indent
set foldlevelstart=4

" Undo & Backup
set undofile
set undodir=~/.vim/undo//

" Clipboard
set clipboard+=unnamedplus " Use system clipboard

" Remember Cursor Position
augroup remember_cursor
  autocmd!
  autocmd BufReadPost * if line("'\"") > 1 && line("'\"") <= line("$") |
    \ execute "normal! g`\"" |
    \ endif
augroup END

" Highlights
highlight FoldColumn guibg=#000000 guifg=#5f5f5f
highlight SignColumn guibg=#000000

" Filetype & Syntax
filetype plugin indent on
syntax enable

" NERDTree Configuration
let NERDTreeShowHidden=1
let NERDTreeMinimalUI=1
let NERDTreeDirArrows=1

" Airline enhancements
let g:airline_powerline_fonts = 1
let g:airline_highlighting_cache = 1
let g:airline#extensions#tabline#enabled = 1

" NERDTree keymaps
nnoremap <C-n> :NERDTreeToggle<CR>
nnoremap <Leader>n :NERDTreeFind<CR>

" Common Keymaps
nnoremap <C-s> :w<CR>             " Save file with Ctrl+s
nnoremap <C-q> :q<CR>             " Quit with Ctrl+q

" Window navigation with Ctrl + h/j/k/l
nnoremap <C-h> <C-w>h
nnoremap <C-j> <C-w>j
nnoremap <C-k> <C-w>k
nnoremap <C-l> <C-w>l

" Buffer navigation
nnoremap <Leader>bn :bnext<CR>
nnoremap <Leader>bp :bprev<CR>

" Terminal mode escape (for Neovim or Vim with terminal)
if has("nvim") || has("terminal")
  tnoremap <Esc> <C-\><C-n>
endif

