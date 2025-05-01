local opt = vim.opt

-- General settings
vim.g.have_nerd_font = true
vim.scriptencoding = "utf-8" -- Use UTF-8 encoding
vim.o.background = "dark"
vim.g.mapleader = " "        -- Leader key
opt.termguicolors = true
opt.mouse = "a"              -- Enable mouse support
opt.timeoutlen = 500
opt.scrolloff = 20           -- Keep lines above/below cursor
opt.list = true              -- Show invisible characters
opt.listchars = { tab = "» ", trail = "·", nbsp = "␣" }
opt.showmode = false         -- Hide -- INSERT -- etc. (handled by lualine)
opt.signcolumn = "yes"

-- Indentation
opt.tabstop = 2
opt.softtabstop = 2
opt.shiftwidth = 2
opt.expandtab = true
opt.smartindent = true
opt.autoindent = true

-- Folding (Treesitter-aware)
opt.foldmethod = "expr"
opt.foldexpr = "v:lua.vim.treesitter.foldexpr()"
opt.foldenable = true
opt.foldlevelstart = 99
opt.foldcolumn = "1"

-- Search
opt.hlsearch = true
opt.incsearch = true
opt.ignorecase = true
opt.smartcase = true
opt.inccommand = "split"

-- Display
opt.number = true
opt.relativenumber = true
opt.colorcolumn = "100"
opt.cmdheight = 2
opt.showtabline = 2
opt.undofile = true

-- Window/Buffer
opt.splitright = true
opt.splitbelow = true
opt.selection = "exclusive"
opt.modifiable = true

-- Key mappings
vim.keymap.set("n", "<leader>q", vim.diagnostic.setloclist, { desc = "Open diagnostic [Q]uickfix list" })
vim.keymap.set("n", "<leader>h", ":nohlsearch<CR>", { desc = "Clear search highlighting" })

-- Restore folds and view state per buffer
vim.cmd([[
  augroup remember_folds
    autocmd!
    autocmd BufWinLeave * if &buftype == '' | mkview | endif
    autocmd BufWinEnter * if &buftype == '' | silent! loadview | endif
  augroup END
]])
