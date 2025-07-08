local opt = vim.opt
local g = vim.g

g.mapleader = " "

g.have_nerd_font = true
opt.background = "dark"
opt.termguicolors = true
opt.mouse = "a"
opt.clipboard = "unnamedplus"
opt.timeoutlen = 300
opt.updatetime = 200
opt.scrolloff = 8
opt.showmode = false
opt.cursorline = true

local undodir = vim.fn.stdpath("cache") .. "/undo"
vim.fn.mkdir(undodir, "p")
opt.undodir = undodir
opt.undofile = true

opt.foldmethod = "expr"
opt.foldexpr = "v:lua.vim.treesitter.foldexpr()"
opt.foldenable = true
opt.foldlevel = 99
opt.foldlevelstart = 5

opt.hlsearch = true
opt.incsearch = true
opt.ignorecase = true
opt.smartcase = true
opt.inccommand = "nosplit"

opt.number = true
opt.relativenumber = true
opt.colorcolumn = "100"
opt.cmdheight = 1
opt.showtabline = 2
opt.showmatch = true
opt.list = true
opt.listchars = { tab = "» ", trail = "·", nbsp = "␣" }

opt.wildmenu = true
opt.wildmode = { "longest:full", "full" }

opt.splitright = true
opt.splitbelow = true
opt.selection = "inclusive"
opt.modifiable = true

vim.keymap.set("n", "<leader>h", ":nohlsearch<CR>", { desc = "Clear search highlights" })
vim.keymap.set("n", "[d", vim.diagnostic.goto_prev, { desc = "Previous diagnostic" })
vim.keymap.set("n", "]d", vim.diagnostic.goto_next, { desc = "Next diagnostic" })

vim.api.nvim_create_autocmd("BufReadPost", {
	callback = function()
		local mark = vim.api.nvim_buf_get_mark(0, '"')
		local lcount = vim.api.nvim_buf_line_count(0)
		if mark[1] > 0 and mark[1] <= lcount then
			pcall(vim.api.nvim_win_set_cursor, 0, mark)
		end
	end,
})
