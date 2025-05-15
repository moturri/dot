local opt = vim.opt

-- Leader key
vim.g.mapleader = " "

-- General settings
vim.g.have_nerd_font = true
vim.scriptencoding = "utf-8"
opt.background = "dark"
opt.termguicolors = true
opt.mouse = "a"
opt.timeoutlen = 500
opt.scrolloff = 20
opt.showmode = false
opt.signcolumn = "yes:1"
opt.clipboard = "unnamedplus"
opt.cursorline = true
opt.updatetime = 250

-- Persistent undo
opt.undofile = true
local undodir = vim.fn.stdpath("cache") .. "/undo"
opt.undodir = undodir
vim.fn.mkdir(undodir, "p")

-- Indentation
opt.tabstop = 2
opt.softtabstop = 2
opt.shiftwidth = 2
opt.expandtab = true
opt.smartindent = true
opt.autoindent = true

-- Folding
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
opt.inccommand = "split"

-- Display
opt.number = true
opt.relativenumber = true
opt.colorcolumn = "100"
opt.cmdheight = 2
opt.showtabline = 2
opt.showmatch = true
opt.list = true
opt.listchars = { tab = "» ", trail = "·", nbsp = "␣" }

-- Completion
opt.completeopt = { "menuone", "noselect" }

-- Wildmenu
opt.wildmenu = true
opt.wildmode = { "longest", "list", "full" }

-- Window/Buffer
opt.splitright = true
opt.splitbelow = true
opt.selection = "exclusive"
opt.modifiable = true

-- Key Mappings
vim.keymap.set("n", "<leader>q", vim.diagnostic.setloclist, { desc = "Open diagnostic [Q]uickfix list" })
vim.keymap.set("n", "<leader>h", ":nohlsearch<CR>", { desc = "Clear search highlighting" })
vim.keymap.set("n", "[d", vim.diagnostic.goto_prev, { desc = "Go to previous diagnostic" })
vim.keymap.set("n", "]d", vim.diagnostic.goto_next, { desc = "Go to next diagnostic" })

-- Recall cursor position
vim.api.nvim_create_autocmd("BufReadPost", {
  callback = function()
    local mark = vim.api.nvim_buf_get_mark(0, '"')
    local lcount = vim.api.nvim_buf_line_count(0)
    if mark[1] > 0 and mark[1] <= lcount then
      pcall(vim.api.nvim_win_set_cursor, 0, mark)
    end
  end,
})

