return {
	{
		"forest-nvim/sequoia.nvim",
		priority = 1000,
		lazy = false, -- Load immediately to set colors early
		config = function()
			local colorscheme = "sequoia-insomnia" -- or: "sequoia-night"

			local ok = pcall(vim.cmd.colorscheme, colorscheme)
			if not ok then
				vim.notify("Sequoia colorscheme not found: " .. colorscheme, vim.log.levels.ERROR)
				return
			end

			-- Transparency groups
			local transparent = {
				"Normal",
				"NormalNC",
				"NormalFloat",
				"FloatBorder",
				"SignColumn",
				"VertSplit",
				"StatusLine",
				"StatusLineNC",
				"WinBar",
				"WinBarNC",
				"Pmenu",
				"PmenuSel",
				"TelescopeNormal",
				"TelescopeBorder",
			}

			for _, group in ipairs(transparent) do
				vim.api.nvim_set_hl(0, group, { bg = "none", ctermbg = "none" })
			end

			-- Optional: remove blend if any plugin sets it (like for `cmp` or `telescope`)
			vim.api.nvim_set_hl(0, "Pmenu", { blend = 0 })
			vim.api.nvim_set_hl(0, "PmenuSel", { blend = 0 })
		end,
	},
}
