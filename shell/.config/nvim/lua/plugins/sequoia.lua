return {
	{
		"forest-nvim/sequoia.nvim",
		priority = 1000,
		lazy = false,
		config = function()
			local colorscheme = "sequoia-insomnia" -- or "sequoia-night"

			local ok, _ = pcall(vim.cmd.colorscheme, colorscheme)
			if not ok then
				vim.notify("Sequoia colorscheme not found: " .. colorscheme, vim.log.levels.ERROR)
				return
			end

			local set_hl = vim.api.nvim_set_hl
			local transparent = { bg = "none", ctermbg = "none" }

			local groups = {
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

			for _, group in ipairs(groups) do
				set_hl(0, group, transparent)
			end

			set_hl(0, "Pmenu", { blend = 0 })
			set_hl(0, "PmenuSel", { blend = 0 })
		end,
	},
}
