---@diagnostic disable: undefined-global

return {
	-- Core LSP Manager
	{
		"williamboman/mason.nvim",
		cmd = { "Mason", "MasonInstall", "MasonUpdate", "MasonUninstall", "MasonLog" },
		opts = {
			ui = { border = "rounded" },
		},
	},

	-- Bridge between Mason and lspconfig
	{
		"williamboman/mason-lspconfig.nvim",
		event = { "BufReadPre", "BufNewFile" },
		dependencies = { "williamboman/mason.nvim" },
		opts = {
			automatic_installation = true,
			automatic_enable = true,
		},
	},

	-- Auto installer for tools (formatters/linters)
	{
		"WhoIsSethDaniel/mason-tool-installer.nvim",
		cmd = { "MasonToolsInstall", "MasonToolsUpdate", "MasonToolsUninstall" },
		dependencies = { "williamboman/mason.nvim" },
		config = function()
			require("mason-tool-installer").setup({
				ensure_installed = {
					-- LSPs
					"clangd",
					"ts_ls",
					"bashls",
					"pyright",
					"lua_ls",
					"jsonls",
					"marksman",
					"taplo",
					"codespell",

					-- Formatters
					"stylua",
					"black",
					"isort",
					"clang-format",
					"shfmt",
					"prettier",
					"cbfmt",

					-- Linters
					"eslint_d",
					"shellcheck",
					"jsonlint",
				},
				auto_update = true,
				run_on_start = true,
				start_delay = 3000,
				debounce_hours = 12,
				integrations = {
					["mason-lspconfig"] = true,
				},
			})
		end,
	},

	-- Neovim-native LSP configurations
	{
		"neovim/nvim-lspconfig",
		event = { "BufReadPre", "BufNewFile" },
		config = function()
			local lspconfig = require("lspconfig")
			local capabilities = vim.lsp.protocol.make_client_capabilities()

			local ok_cmp, cmp_lsp = pcall(require, "cmp_nvim_lsp")
			if ok_cmp then
				capabilities = cmp_lsp.default_capabilities(capabilities)
			end

			vim.diagnostic.config({
				virtual_text = true,
				underline = true,
				severity_sort = true,
				update_in_insert = false,
				float = { border = "rounded" },
				signs = {
					text = {
						[vim.diagnostic.severity.ERROR] = "",
						[vim.diagnostic.severity.WARN] = "",
						[vim.diagnostic.severity.HINT] = "",
						[vim.diagnostic.severity.INFO] = "",
					},
				},
			})

			vim.lsp.set_log_level("off")

			local function on_attach(client, bufnr)
				local ok_navic, navic = pcall(require, "nvim-navic")
				if ok_navic and client.server_capabilities.documentSymbolProvider then
					navic.attach(client, bufnr)
				end

				-- Disable formatting in favor of Conform
				client.server_capabilities.documentFormattingProvider = false
				client.server_capabilities.documentRangeFormattingProvider = false

				vim.notify("LSP attached: " .. client.name, vim.log.levels.INFO, { title = "LSP" })
			end

			-- Disable default script providers
			for _, provider in ipairs({ "node", "perl", "python", "python3", "ruby" }) do
				vim.g["loaded_" .. provider .. "_provider"] = 0
			end

			-- Setup all mason-installed servers
			local mason_lspconfig = require("mason-lspconfig")
			local ignore = { tombi = true }

			for _, server in ipairs(mason_lspconfig.get_installed_servers()) do
				if not ignore[server] then
					local ok, server_module = pcall(function()
						return lspconfig[server]
					end)
					if ok and server_module then
						server_module.setup({
							capabilities = capabilities,
							on_attach = on_attach,
						})
					end
				end
			end
		end,
	},

	-- Format on demand (with Conform)
	{
		"stevearc/conform.nvim",
		event = { "BufReadPre", "BufNewFile" },
		config = function()
			local conform = require("conform")

			conform.setup({
				formatters_by_ft = {
					lua = { "stylua" },
					python = { "isort", "black" },
					javascript = { "prettier" },
					typescript = { "prettier" },
					c = { "cbfmt", "clang_format" },
					cpp = { "clang_format" },
					sh = { "shfmt" },
					json = { "prettier" },
					yaml = { "prettier" },
					markdown = { "prettier" },
					toml = { "taplo" },
				},
				format_on_save = false,
			})

			vim.keymap.set("n", "<leader>bf", function()
				conform.format({ async = true, lsp_fallback = true })
			end, { desc = "Format buffer" })
		end,
	},

	-- Linting with virtual diagnostics
	{
		"mfussenegger/nvim-lint",
		event = { "BufReadPre", "BufNewFile" },
		config = function()
			local lint = require("lint")

			lint.linters_by_ft = {
				sh = { "shellcheck" },
				javascript = { "eslint_d" },
				json = { "jsonlint" },
			}

			vim.keymap.set("n", "<leader>be", vim.diagnostic.open_float, { desc = "Show line diagnostics" })
			vim.keymap.set("n", "<leader>bL", function()
				lint.try_lint()
			end, { desc = "Manually lint current buffer" })
		end,
	},
}
