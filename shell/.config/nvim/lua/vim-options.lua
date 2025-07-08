local opt = vim.opt
local g = vim.g

-- Leader Key
g.mapleader = " "

-- General
g.have_nerd_font = true
opt.background = "dark"
opt.termguicolors = true
opt.mouse = "a"
opt.clipboard = "unnamedplus"
opt.timeoutlen = 300
opt.updatetime = 200
opt.scrolloff = 8
opt.showmode = false
opt.signcolumn = "yes"
opt.cursorline = true

-- Persistent Undo
local undodir = vim.fn.stdpath("cache") .. "/undo"
vim.fn.mkdir(undodir, "p")
opt.undodir = undodir
opt.undofile = true

-- Folding (Treesitter)
opt.foldmethod = "expr"
opt.foldexpr = "v:lua.vim.treesitter.foldexpr()"
opt.foldenable = true
opt.foldlevel = 99
opt.foldlevelstart = 5
opt.foldcolumn = "1"

-- Search
opt.hlsearch = true
opt.incsearch = true
opt.ignorecase = true
opt.smartcase = true
opt.inccommand = "nosplit"

-- UI
opt.number = true
opt.relativenumber = true
opt.colorcolumn = "100"
opt.cmdheight = 1
opt.showtabline = 2
opt.showmatch = true
opt.list = true
opt.listchars = { tab = "» ", trail = "·", nbsp = "␣" }

-- Wildmenu
opt.wildmenu = true
opt.wildmode = { "longest:full", "full" }

-- Windows
opt.splitright = true
opt.splitbelow = true
opt.selection = "inclusive"
opt.modifiable = true

-- Keymaps
vim.keymap.set("n", "<leader>h", ":nohlsearch<CR>", { desc = "Clear search highlights" })
vim.keymap.set("n", "[d", vim.diagnostic.goto_prev, { desc = "Previous diagnostic" })
vim.keymap.set("n", "]d", vim.diagnostic.goto_next, { desc = "Next diagnostic" })

-- Restore last cursor position when reopening files
vim.api.nvim_create_autocmd("BufReadPost", {
	callback = function()
		local mark = vim.api.nvim_buf_get_mark(0, '"')
		local lcount = vim.api.nvim_buf_line_count(0)
		if mark[1] > 0 and mark[1] <= lcount then
			pcall(vim.api.nvim_win_set_cursor, 0, mark)
		end
	end,
})

-- Disable some default providers
local default_providers = {
	"node",
	"perl",
	"python",
	"python3",
	"ruby",
}

for _, provider in ipairs(default_providers) do
	vim.g["loaded_" .. provider .. "_provider"] = 0
end

-- LSP-based folding
vim.api.nvim_create_autocmd("LspAttach", {
	group = vim.api.nvim_create_augroup("LspFolding", { clear = true }), -- Autogroup for LSP-based folding
	callback = function(args)
		local client = vim.lsp.get_client_by_id(args.data.client_id)
		-- If the LSP client provides folding ranges, use 'syntax' foldmethod
		if client.server_capabilities.foldingRangeProvider then
			vim.bo[args.buf].foldmethod = "syntax"
		end
	end,
})

