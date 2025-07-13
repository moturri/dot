return {
	{
		"williamboman/mason.nvim",
		cmd = {
			"Mason",
			"MasonInstall",
			"MasonInstallAll",
			"MasonUpdate",
			"MasonUpdateAll",
			"MasonUninstall",
			"MasonUninstallAll",
			"MasonLog",
		},
		opts = {
			ui = { border = "rounded" },
		},
	},

	{
		"williamboman/mason-lspconfig.nvim",
		event = { "BufReadPre", "BufNewFile" },
		dependencies = { "williamboman/mason.nvim" },
		opts = {
			automatic_installation = true,
		},
	},

	{
		"WhoIsSethDaniel/mason-tool-installer.nvim",
		cmd = { "MasonToolsInstall", "MasonToolsUpdate", "MasonToolsUninstall" },
		dependencies = { "williamboman/mason.nvim" },
		config = function()
			require("mason-tool-installer").setup({
				ensure_installed = {
					"clangd",
					"marksman",
					"markdownlint",
					"glow",
					"cbfmt",
					"taplo",
					"stylua",
					"black",
					"isort",
					"clang-format",
					"shfmt",
					"prettier",
					"flake8",
					"eslint_d",
					"luacheck",
					"shellcheck",
					"jsonlint",
					"pyright",
				},
			})
		end,
	},

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

				client.server_capabilities.documentFormattingProvider = false
				client.server_capabilities.documentRangeFormattingProvider = false

				vim.notify("LSP attached: " .. client.name, vim.log.levels.INFO, { title = "LSP" })
			end

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

			local ignore = { tombi = true }
			local mason_lspconfig = require("mason-lspconfig")

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
					toml = { "taplo" }
				},
				format_on_save = false,
			})

			vim.keymap.set("n", "<leader>fm", function()
				conform.format({ async = true, lsp_fallback = true })
			end, { desc = "Format buffer" })
		end,
	},

	{
		"mfussenegger/nvim-lint",
		event = { "BufReadPre", "BufNewFile" },
		config = function()
			local lint = require("lint")

			lint.linters_by_ft = {
				sh = { "shellcheck" },
				python = { "flake8" },
				markdown = { "markdownlint" },
				lua = { "luacheck" },
				javascript = { "eslint_d" },
				json = { "jsonlint" },
			}

			vim.keymap.set("n", "<leader>ge", vim.diagnostic.open_float, { desc = "Show line diagnostics" })
			vim.keymap.set("n", "<leader>ll", function()
				lint.try_lint()
			end, { desc = "Manually lint current buffer" })
		end,
	},
}
