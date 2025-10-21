---@diagnostic disable: undefined-global

-- Leader key
vim.g.mapleader = " "

-- Encoding
vim.scriptencoding = "utf-8"
vim.opt.encoding = "utf-8"
vim.opt.fileencoding = "utf-8"

-- UI and appearance
vim.g.have_nerd_font = true
vim.opt.background = "dark"
vim.opt.termguicolors = true
vim.opt.mouse = "a"
vim.opt.showmode = false
vim.opt.cursorline = false
vim.opt.colorcolumn = "100"
vim.opt.cmdheight = 0
vim.opt.showtabline = 2
vim.opt.showmatch = true
vim.opt.signcolumn = "yes"
vim.opt.scrolloff = 10
vim.opt.splitright = true
vim.opt.splitbelow = true

-- Line numbers
vim.opt.number = true
vim.opt.relativenumber = true

-- Ensure relative numbers only in normal mode
vim.api.nvim_create_autocmd({ "InsertEnter" }, {
	callback = function()
		vim.opt.relativenumber = false
	end,
})

vim.api.nvim_create_autocmd({ "InsertLeave" }, {
	callback = function()
		vim.opt.relativenumber = true
	end,
})

-- Disable numbers in terminals and floating windows
vim.api.nvim_create_autocmd("TermOpen", {
	callback = function()
		vim.opt_local.number = false
		vim.opt_local.relativenumber = false
	end,
})

vim.api.nvim_create_autocmd("WinEnter", {
	callback = function()
		if vim.bo.buftype == "nofile" or vim.bo.buftype == "prompt" then
			vim.opt_local.number = false
			vim.opt_local.relativenumber = false
		end
	end,
})

-- Indentation and formatting
vim.opt.smartindent = true
vim.opt.autoindent = true
vim.opt.shiftround = true
vim.opt.breakindent = true

-- Search behaviour
vim.opt.hlsearch = true
vim.opt.incsearch = true
vim.opt.ignorecase = true
vim.opt.smartcase = true
vim.opt.inccommand = "nosplit"

-- Performance and responsiveness
vim.opt.timeoutlen = 500
vim.opt.updatetime = 300

-- Clipboard
vim.opt.clipboard = "unnamedplus"

-- Folding (Treesitter-based)
vim.opt.foldmethod = "expr"
vim.opt.foldexpr = "v:lua.vim.treesitter.foldexpr()"
vim.opt.foldenable = true
vim.opt.foldlevel = 99
vim.opt.foldlevelstart = 6

-- Wildmenu and completion
vim.opt.wildmenu = true
vim.opt.wildmode = { "longest:full", "full" }

-- Invisible characters
vim.opt.list = true
vim.opt.listchars = {
	tab = "» ",
	trail = "·",
	nbsp = "␣",
}

-- Persistent undo
local undodir = vim.fn.stdpath("cache") .. "/undo"
if vim.fn.isdirectory(undodir) == 0 then
	vim.fn.mkdir(undodir, "p")
end
vim.opt.undodir = undodir
vim.opt.undofile = true

-- Keymaps
vim.keymap.set("n", "<leader>h", ":nohlsearch<CR>", {
	desc = "Clear search highlights",
	silent = true,
})

-- Restore cursor to last position
vim.api.nvim_create_autocmd("BufReadPost", {
	desc = "Restore cursor to last position",
	callback = function()
		local mark = vim.api.nvim_buf_get_mark(0, '"')
		local lcount = vim.api.nvim_buf_line_count(0)
		if mark[1] > 0 and mark[1] <= lcount then
			pcall(vim.api.nvim_win_set_cursor, 0, mark)
		end
	end,
})
