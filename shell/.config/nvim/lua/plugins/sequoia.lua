---@diagnostic disable: undefined-global

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
			local get_hl = vim.api.nvim_get_hl
			local transparent = { bg = "none", ctermbg = "none" }

			local function merge_highlight(group, new_opts)
				local status_ok, current = pcall(get_hl, 0, { name = group, link = false })
				if not status_ok then
					return
				end
				set_hl(0, group, vim.tbl_extend("force", current, new_opts))
			end

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
				"LineNr",
			}

			for _, group in ipairs(groups) do
				merge_highlight(group, transparent)
			end

			merge_highlight("Pmenu", { blend = 0 })
			merge_highlight("PmenuSel", { blend = 0 })
		end,
	},
}
