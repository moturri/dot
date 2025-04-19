local opt = vim.opt

-- General settings
vim.g.have_nerd_font = true
vim.o.background = "dark"
vim.g.mapleader = " " -- Leader key setup
opt.termguicolors = true
opt.encoding = "UTF-8"
opt.mouse = "a" -- Enable mouse support
opt.timeoutlen = 500
opt.scrolloff = 10 -- Keep 10 lines visible above/below cursor
opt.list = true -- Show invisible characters like spaces and tabs
opt.listchars = { tab = "» ", trail = "·", nbsp = "␣" } -- Customize invisible characters
opt.showmode = false -- Hide mode in command line (we use lualine for this)
opt.signcolumn = "yes" -- Always show the sign column

-- Indentation settings
opt.tabstop = 2 -- Set tab stop to 2 spaces
opt.softtabstop = 2 -- How many spaces to treat as a tab
opt.shiftwidth = 2 -- Indentation width (used for >> and << operations)
opt.expandtab = true -- Use spaces instead of tabs
opt.smartindent = true -- Enable smart indentation
opt.autoindent = true -- Enable automatic indentation

-- Ensure Treesitter handles indentation properly
vim.cmd([[
  augroup treesitter_indentation
    autocmd!
    autocmd FileType * setlocal shiftwidth=2 softtabstop=2 tabstop=2 expandtab
  augroup END
]])

-- Folding settings
vim.o.foldmethod = "expr" -- Use expression for folding
vim.o.foldexpr = "nvim_treesitter#foldexpr()" -- Use Treesitter for fold expression
vim.o.foldlevelstart = 99 -- Start with all folds open
vim.o.foldenable = true -- Enable folding by default
vim.o.foldcolumn = "1" -- Show fold column

-- Search settings
opt.hlsearch = true -- Highlight search matches
opt.incsearch = true -- Incremental search
opt.ignorecase = true -- Ignore case for search
opt.smartcase = true -- Override ignorecase if search has uppercase
opt.inccommand = "split" -- Show search results live in a split

-- Display settings
opt.number = true -- Show line numbers
opt.relativenumber = true -- Show relative line numbers
opt.colorcolumn = "100" -- Highlight column 100 for wide code
opt.cmdheight = 2 -- Increase command line height for clarity
opt.showtabline = 2 -- Always show tabline
opt.undofile = true -- Enable persistent undo

-- Window and buffer settings
opt.splitright = true -- Open new vertical splits to the right
opt.splitbelow = true -- Open new horizontal splits below
opt.selection = "exclusive" -- Exclusive selection behavior
opt.modifiable = true -- Allow modification of buffer content

-- Key mappings (shortcuts for common actions)
vim.keymap.set("n", "<leader>q", vim.diagnostic.setloclist, { desc = "Open diagnostic [Q]uickfix list" })
vim.keymap.set("n", "<leader>h", ":nohlsearch<CR>", { desc = "Clear search highlighting" })

-- Remember folds (preserve fold state between sessions)
vim.cmd([[
  augroup remember_folds
    autocmd!
    autocmd BufWinLeave *.* mkview
    autocmd BufWinEnter *.* silent! loadview
  augroup END
]])
