local opt = vim.opt

-- General settings
vim.g.have_nerd_font = true
vim.o.background = "dark"
vim.g.mapleader = " "
opt.termguicolors = true
opt.encoding = "UTF-8"
opt.mouse = "a"
opt.timeoutlen = 500
opt.scrolloff = 10
opt.list = true
opt.listchars = { tab = "» ", trail = "·", nbsp = "␣" }
opt.showmode = false
opt.signcolumn = "yes"

-- Indentation settings
opt.tabstop = 2
opt.softtabstop = 2
opt.shiftwidth = 2
opt.expandtab = true -- Use spaces instead of tabs
opt.smartindent = true -- Enable smart indentation
opt.autoindent = true -- Enable automatic indentation

-- Folding settings
vim.o.foldmethod = 'expr' -- Use expression for folding
vim.o.foldexpr = "nvim_treesitter#foldexpr()" -- Use Treesitter for fold expression
vim.o.foldlevelstart = 99 -- Start with all folds open
vim.o.foldenable = true -- Enable folding by default
vim.o.foldcolumn = '1' -- Show fold column

-- Search settings
opt.hlsearch = true
opt.incsearch = true
opt.ignorecase = true
opt.smartcase = true
opt.inccommand = "split"

-- Display settings
opt.number = true
opt.relativenumber = true
opt.colorcolumn = "100"
opt.cmdheight = 2
opt.showtabline = 2
opt.undofile = true

-- Window and buffer settings
opt.splitright = true
opt.splitbelow = true
opt.selection = "exclusive"
opt.modifiable = true

-- Key mappings
vim.keymap.set("n", "<leader>q", vim.diagnostic.setloclist, { desc = "Open diagnostic [Q]uickfix list" })
vim.keymap.set("n", "<c-k>", ":wincmd k<CR>")
vim.keymap.set("n", "<c-j>", ":wincmd j<CR>")
vim.keymap.set("n", "<c-h>", ":wincmd h<CR>")
vim.keymap.set("n", "<c-l>", ":wincmd l<CR>")
vim.keymap.set("n", "<leader>h", ":nohlsearch<CR>")
vim.api.nvim_set_keymap("n", "<C-W>,", ":vertical resize -10<CR>", { noremap = true })
vim.api.nvim_set_keymap("n", "<C-W>.", ":vertical resize +10<CR>", { noremap = true })

-- Remember folds
vim.cmd([[
  augroup remember_folds
    autocmd!
    autocmd BufWinLeave *.* mkview
    autocmd BufWinEnter *.* silent! loadview
  augroup END
]])
