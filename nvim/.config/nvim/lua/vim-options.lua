local opt = vim.opt

vim.g.have_nerd_font = true
vim.o.background = "dark"
vim.g.mapleader = " "
vim.o.foldenable = true
opt.tabstop = 2
opt.softtabstop = 2
opt.shiftwidth = 2
opt.cmdheight = 2
opt.colorcolumn = "100"
opt.showtabline = 2
opt.completeopt = "menuone,noinsert,noselect"
opt.backspace = "indent,eol,start"
opt.termguicolors = true
opt.hlsearch = true
opt.number = true
opt.relativenumber = true
opt.mouse = "a"
opt.breakindent = true
opt.smartindent = true
opt.undofile = true
opt.ignorecase = true
opt.incsearch = true
opt.wrap = false
opt.smartcase = true
opt.signcolumn = "yes"
opt.timeoutlen = 500
opt.splitright = true
opt.splitbelow = true
opt.list = true
opt.listchars = { tab = "» ", trail = "·", nbsp = "␣" }
opt.inccommand = "split"
opt.scrolloff = 10
opt.expandtab = true
opt.iskeyword:append("-")
opt.selection = "exclusive"
opt.mouse = "a"
-- opt.clipboard:append("unnamedplus")
opt.encoding = "UTF-8"
opt.showmode = false
vim.o.foldmethod = 'syntax'
vim.o.foldlevel = 99
vim.o.foldcolumn = '1'
opt.modifiable = true
opt.encoding = "UTF-8"
opt.showmode = false

vim.cmd([[
  augroup remember_folds
    autocmd!
    autocmd BufWinLeave *.* mkview
    autocmd BufWinEnter *.* silent! loadview
  augroup END
]])

vim.keymap.set("n", "<leader>q", vim.diagnostic.setloclist, { desc = "Open diagnostic [Q]uickfix list" })

vim.keymap.set("n", "<c-k>", ":wincmd k<CR>")
vim.keymap.set("n", "<c-j>", ":wincmd j<CR>")
vim.keymap.set("n", "<c-h>", ":wincmd h<CR>")
vim.keymap.set("n", "<c-l>", ":wincmd l<CR>")
vim.keymap.set("n", "<leader>h", ":nohlsearch<CR>")
vim.wo.number = true
vim.api.nvim_set_keymap("n", "<C-W>,", ":vertical resize -10<CR>", { noremap = true })
vim.api.nvim_set_keymap("n", "<C-W>.", ":vertical resize +10<CR>", { noremap = true })
