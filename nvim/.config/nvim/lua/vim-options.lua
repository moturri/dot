local opt = vim.opt
local g = vim.g

-- Leader key
g.mapleader = " "

-- General
g.have_nerd_font = true
vim.scriptencoding = "utf-16"

opt.clipboard = "unnamedplus"
opt.background = "dark"
opt.termguicolors = true
opt.mouse = "a"
opt.timeoutlen = 300
opt.scrolloff = 8
opt.showmode = false
opt.signcolumn = "yes"
opt.cursorline = true
opt.updatetime = 200

-- Persistent undo
opt.undofile = true
local undodir = vim.fn.stdpath("cache") .. "/undo"
vim.fn.mkdir(undodir, "p")
opt.undodir = undodir

-- Indentation
opt.tabstop = 2
opt.softtabstop = 2
opt.shiftwidth = 2
opt.expandtab = true
opt.smartindent = true
opt.autoindent = true

-- Folding (Treesitter-based)
opt.foldmethod = "expr"
opt.foldexpr = "v:lua.vim.treesitter.foldexpr()"
opt.foldenable = true
opt.foldlevelstart = 4
opt.foldlevel = 99
opt.foldcolumn = "1"

-- Search
opt.hlsearch = true
opt.incsearch = true
opt.ignorecase = true
opt.smartcase = true
opt.inccommand = "nosplit"

-- UI Display
opt.number = true
opt.relativenumber = true
opt.colorcolumn = "100"
opt.cmdheight = 1
opt.showtabline = 2
opt.showmatch = true
opt.list = true
opt.listchars = { tab = "» ", trail = "·", nbsp = "␣" }

-- Completion
opt.completeopt = { "menuone", "noselect" }

-- Wildmenu (command line completion)
opt.wildmenu = true
opt.wildmode = { "longest:full", "full" }

-- Window/Buffer behavior
opt.splitright = true
opt.splitbelow = true
opt.selection = "inclusive"
opt.modifiable = true

-- Key mappings
vim.keymap.set("n", "<leader>q", vim.diagnostic.setloclist, { desc = "Open diagnostic [Q]uickfix list" })
vim.keymap.set("n", "<leader>h", ":nohlsearch<CR>", { desc = "Clear search highlighting" })
vim.keymap.set("n", "[d", vim.diagnostic.goto_prev, { desc = "Go to previous diagnostic" })
vim.keymap.set("n", "]d", vim.diagnostic.goto_next, { desc = "Go to next diagnostic" })

-- Restore cursor position on reopen
vim.api.nvim_create_autocmd("BufReadPost", {
  callback = function()
    local mark = vim.api.nvim_buf_get_mark(0, '"')
    local lcount = vim.api.nvim_buf_line_count(0)
    if mark[1] > 0 and mark[1] <= lcount then
      pcall(vim.api.nvim_win_set_cursor, 0, mark)
    end
  end,
})
